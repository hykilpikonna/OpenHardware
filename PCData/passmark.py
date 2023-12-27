"""
This file is used to crawl passmark data and store it as a csv
"""
from pathlib import Path
from typing import NamedTuple

import pandas as pd
import requests
from bs4 import BeautifulSoup


class Processor(NamedTuple):
    id: str
    name: str
    passmark: int


def crawl_cpu_gpu(cpu: bool) -> pd.DataFrame:
    """
    Crawl cpu/gpu benchmark data

    :param cpu: True if cpu, False if gpu
    """
    file = Path("data/cpu.csv" if cpu else "data/gpu.csv")

    if file.exists():
        return pd.read_csv(file)

    url = "https://www.cpubenchmark.net/cpu_list.php" if cpu else "https://www.videocardbenchmark.net/gpu_list.php"
    page = requests.get(url)
    bs = BeautifulSoup(page.content, "html.parser")

    table = bs.find("table", {"id": "cputable"})
    rows = table.findAll("tr")

    cpu_list = []
    for row in rows:
        cols = row.findAll("td")
        if len(cols) == 0:
            continue
        id = row["id"]
        name = cols[0].text.strip()
        passmark = int(cols[1].text.strip().replace(",", ""))
        cpu_list.append(Processor(id=id, name=name, passmark=passmark))

    file.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(cpu_list)
    df.to_csv(file, index=False)

    return df


if __name__ == '__main__':
    crawl_cpu_gpu(True)
    crawl_cpu_gpu(False)
