import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

units = {"B": 1, "KB": 10**3, "MB": 10**6, "GB": 10**9, "TB": 10**12}


def parse_size(size):
    number, unit = [string.strip() for string in size.split()]
    return int(float(number) * units[unit])


df = pd.read_csv("up.csv")
df.columns = ["time", "ip", "bytes_up"]
df["time"] = pd.to_datetime(df["time"], format="%Y-%m-%d-%H-%M-%S")
df["bytes_up"] = df["bytes_up"].str.replace(
    r"(\d+)(\w+)", lambda x: x.group(1) + " " + x.group(2), regex=True
)
df["bytes_up"] = df["bytes_up"].apply(parse_size)
df.plot(x="time", y="bytes_up")
plt.show()
