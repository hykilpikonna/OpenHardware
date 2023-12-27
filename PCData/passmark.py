"""
This file is used to crawl passmark data and store it as a csv
"""
from pathlib import Path
from typing import NamedTuple

import pandas as pd
import requests
from bs4 import BeautifulSoup


class CPU(NamedTuple):
    id: int
    name: str
    passmark: int


def crawl_cpu() -> pd.DataFrame:
    """
    Crawl cpu benchmark data
    """
    file = Path("data/cpu.csv")

    if file.exists():
        return pd.read_csv(file)

    url = "https://www.cpubenchmark.net/cpu_list.php"
    page = requests.get(url)
    bs = BeautifulSoup(page.content, "html.parser")

    table = bs.find("table", {"id": "cputable"})
    rows = table.findAll("tr")

    cpu_list = []
    for row in rows:
        cols = row.findAll("td")
        if len(cols) == 0:
            continue
        id = int(row["id"].replace("cpu", ""))
        cpu = cols[0].text.strip()
        passmark = int(cols[1].text.strip().replace(",", ""))
        cpu_list.append(CPU(id=id, name=cpu, passmark=passmark))

    file.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(cpu_list)
    df.to_csv(file, index=False)

    return df


if __name__ == '__main__':
    crawl_cpu()
