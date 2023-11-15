import os
from itertools import repeat
from pathlib import Path
from typing import Tuple

import boto3
import urllib3
import yaml
from dotenv import load_dotenv
from pathos.multiprocessing import ProcessPool

urllib3.disable_warnings()


current_folder = Path(__file__).parent
top_folder = current_folder.parent
load_dotenv(top_folder / "minio.env")


BUCKET = os.environ["AWS_BUCKET"]
s3 = boto3.client("s3", verify=False)


def main(catalog_file_name: Path, multi_process: bool = False):
    catalog: dict
    try:
        with open(catalog_file_name, "r") as yaml_file:
            # Parse the YAML data
            catalog = yaml.safe_load(yaml_file)
    except FileNotFoundError:
        print(f"File '{catalog_file_name}' not found.")
    except Exception as e:
        print(f"Error reading the YAML file: {e}")

    p_drive_root = Path(catalog["meta"]["root"])

    copy_list: list(tuple(str, str)) = []

    for item in catalog.values():
        # only look at items with a path
        if not "path" in item:
            continue

        source_path = Path(item["path"])
        # replace variable with year we are looking for
        if "{year}" in source_path.__str__():
            source_path = Path(source_path.__str__().replace("{year}", "2010"))

        if source_path.suffix == ".zarr":
            # zarr files do not work with glob
            all_files = p_drive_root.glob(f"{source_path}/**/*")
        else:
            all_files = p_drive_root.glob(source_path.__str__())

        for file in all_files:
            relative_path = file.relative_to(p_drive_root)
            # destination = Path(f"s3://{BUCKET}/{relative_path.as_posix()}")
            # print(f"Push file {file} to {destination}")
            if relative_path.suffix == ".vrt":
                # if vrt present, also copy refernced files based on naming convention
                copy_list += list(
                    map(
                        lambda p: (
                            p,
                            Path(*p.parts[len(p_drive_root.parts) :]).as_posix(),
                        ),
                        (p_drive_root / relative_path.parent / relative_path.stem).glob(
                            "*"
                        ),
                    )
                )
            copy_list.append((file, relative_path.as_posix()))
    print(f"About to copy {len(copy_list)} files")

    def copy_file_helper(copy_tuple: Tuple[Path, str], bucket: str):
        copy_file_to_bucket(copy_tuple[0], copy_tuple[1], bucket, multiprocess=True)

    if multi_process:
        with ProcessPool(nodes=8) as pool:
            try:
                pool.map(copy_file_helper, copy_list, repeat(BUCKET))
            finally:
                pool.close()
                pool.join()
    else:
        for idx, copy_item in enumerate(copy_list):
            copy_file_to_bucket(
                file_path=copy_item[0],
                s3_object_key=copy_item[1],
                bucket_name=BUCKET,
                total_num_items=len(copy_list),
                item_nr=idx,
            )


def progressbar_pprint(
    uploaded_percentage: int, item_nr: int, total_num_items: int, width_bar=30
):
    left = width_bar * uploaded_percentage // 100
    right = width_bar - left
    print(
        "\r[",
        "#" * int(left),
        " " * int(right),
        "]",
        f" {uploaded_percentage:.0f}%",
        f" {item_nr}/{total_num_items}",
        sep="",
        end="",
        flush=True,
    )


def copy_file_to_bucket(
    file_path,
    s3_object_key,
    bucket_name,
    total_num_items: int | None = None,
    item_nr: int | None = None,
    multiprocess: bool = False,
):
    def upload_callback(size):
        nonlocal uploaded
        nonlocal uploaded_percentage
        if total_size == 0:
            return
        uploaded += size
        new_uploaded_percentage = int(uploaded / total_size * 100)
        if not multiprocess and new_uploaded_percentage != uploaded_percentage:
            progressbar_pprint(
                new_uploaded_percentage,
                item_nr=item_nr,
                total_num_items=total_num_items,
            )
            uploaded_percentage = new_uploaded_percentage
        return

    total_size = os.stat(file_path).st_size
    uploaded = 0
    uploaded_percentage = 0
    if check_file_exists(s3_object_key=s3_object_key, bucket_name=bucket_name):
        if not multiprocess:
            print(f"Skipping '{file_path}' as it is already uploaded")
        return
    try:
        # Upload the file to S3
        if not multiprocess:
            print(f"Starting upload of {file_path}, size = {total_size}")
        s3.upload_file(file_path, bucket_name, s3_object_key, Callback=upload_callback)
        if not multiprocess:
            print(
                f"\nSuccessfully uploaded {file_path} to {bucket_name}/{s3_object_key}"
            )
    except Exception as e:
        if not multiprocess:
            print(f"Error uploading {file_path} to {bucket_name}/{s3_object_key}")
            print(f"Error: {e}")
        else:
            pid = os.getpid()
            with open(top_folder / logs / f"error-{pid}.log", "a") as log_file:
                log_file.write(
                    f"Error uploading {file_path} to {bucket_name}/{s3_object_key}"
                )
                log_file.write(f"Error: {e}")


def check_file_exists(s3_object_key, bucket_name) -> bool:
    res = s3.list_objects_v2(Bucket=bucket_name, Prefix=s3_object_key, MaxKeys=1)
    return "Contents" in res


if __name__ == "__main__":
    # main(top_folder / "deltares-data-curated.yaml")
    main(top_folder / "data_catalogs" / "deltares-data-curated.yaml", True)
