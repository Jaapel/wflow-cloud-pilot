import yaml
import boto3
import os
from dotenv import load_dotenv
from pathlib import Path
import urllib3
urllib3.disable_warnings()


current_folder = Path(__file__).parent
top_folder = current_folder.parent
load_dotenv(top_folder / "minio.env")


BUCKET = os.environ['AWS_BUCKET']
s3 = boto3.client('s3', verify=False)


def main(catalog_file_name: Path):

    catalog: dict
    try:
        with open(catalog_file_name, 'r') as yaml_file:
            # Parse the YAML data
            catalog = yaml.safe_load(yaml_file)
            # print(catalog)
    except FileNotFoundError:
        print(f"File '{catalog_file_name}' not found.")
    except Exception as e:
        print(f"Error reading the YAML file: {e}")
        
    p_drive_root = Path(catalog['meta']['root'])
    
    copy_list: list(tuple(str,str)) = []
    
    for dataset_name, item in catalog.items():
        #only look at items with a path
        if not 'path' in item:
            continue
        
        source_path = Path(item['path'])
        #replace variable with year we are looking for
        if '{year}' in source_path.__str__():
            source_path = Path(source_path.__str__().replace('{year}', '2010'))
        
        all_files = p_drive_root.glob(source_path.__str__())
        
        for file in all_files:
            relative_path = file.relative_to(p_drive_root)
            destination = Path(f"s3://{BUCKET}/{relative_path.as_posix()}")
            # print(f"Push file {file} to {destination}")

            copy_list.append((file, relative_path.as_posix()))
    print(f"About to copy {len(copy_list)} files")
    # print(copy_list)
    for idx, copy_item in enumerate(copy_list):
        print(f"{idx+1}/{len(copy_list)}")
        copy_file_to_bucket(file_path=copy_item[0], s3_object_key=copy_item[1], bucket_name=BUCKET)
        

def copy_file_to_bucket(file_path, s3_object_key, bucket_name):
    def upload_callback(size):
        nonlocal uploaded
        nonlocal uploaded_percentage
        if total_size == 0:
            return
        uploaded += size
        new_uploaded_percentage = int(uploaded / total_size * 100)
        if new_uploaded_percentage != uploaded_percentage:
            print("{} %".format(new_uploaded_percentage))
            uploaded_percentage = new_uploaded_percentage
        return
    total_size = os.stat(file_path).st_size
    uploaded = 0
    uploaded_percentage = 0
    if check_file_exists(s3_object_key=s3_object_key, bucket_name=bucket_name):
        print(f"Skipping '{file_path}' as it is already uploaded")
        return
    try:
        # Upload the file to S3
        print(f"Starting upload of {file_path}, size = {total_size}")
        s3.upload_file(file_path, bucket_name, s3_object_key, Callback=upload_callback)
        print(f'Successfully uploaded {file_path} to {bucket_name}/{s3_object_key}')
    except Exception as e:
        print(f'Error: {e}')

def check_file_exists(s3_object_key, bucket_name)-> bool:
    res = s3.list_objects_v2(Bucket=bucket_name, Prefix=s3_object_key, MaxKeys=1)
    return 'Contents' in res


if __name__ == "__main__":
   
    main(top_folder / 'deltares-data-curated.yaml')
    
    