"""
This file is used to crawl passmark data and store it as a csv
"""
import json
from pathlib import Path
from typing import NamedTuple

import pandas as pd
import requests
from bs4 import BeautifulSoup
from hypy_utils.logging_utils import setup_logger
from hypy_utils.tqdm_utils import tmap
from orjson import orjson


log = setup_logger()

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


def crawl_id(id: str):
    """
    Crawl cpu/gpu benchmark data

    :param id: id of cpu/gpu
    """
    cpu = id.startswith("cpu")
    id = id[3:]
    url = f"https://www.cpubenchmark.net/cpu.php" if cpu else f"https://www.videocardbenchmark.net/gpu.php"
    page = requests.get(url, params={"id": id})
    bs = BeautifulSoup(page.content, "html5lib")

    desc = bs.find("div", {"class": "desc"})
    name = desc.find("span", {"class": "cpuname"}).text.strip()
    specs = {}
    spec_nodes = (list(desc.find("em", {"class": "left-desc-cpu"}).findAll("p")) +
                  list(desc.find("div", {"class": "desc-foot"}).findAll("p")))
    for spec in spec_nodes:
        key = spec.find("strong")
        if not key:
            continue
        key = key.text.strip()
        value = spec.text.strip().replace(key, "").strip().replace("\u00a0", "")
        specs[key.strip(":").replace("\u00a0", "")] = value

    # Parse score
    score_lines = desc.find("div", {"class": "right-desc"}).text.strip().splitlines()[1:]
    score = int(score_lines.pop(0).strip().strip("\t"))
    specs["Score"] = score
    for line in score_lines:
        if ':' not in line:
            continue
        key, value = line.split(":")
        key = key.strip()
        value = int(value.strip())
        specs[key] = value

    return name, specs


def crawl_gpuinfo_batch():
    gpu_info_f = Path("data/gpu_info.json")
    gpu_info = {} if not gpu_info_f.exists() else json.loads(gpu_info_f.read_text())
    left = [gpu for gpu in crawl_cpu_gpu(False)["id"] if gpu not in gpu_info]

    # Batch
    bs = 100
    while len(left) > 0:
        log.info(f"Crawling batch of {bs}, {len(left)} left")
        batch = left[:bs]
        left = left[bs:]
        info = tmap(lambda id: crawl_id(id), batch, max_workers=20)
        gpu_info.update({id: info for id, info in zip(batch, info)})
        gpu_info_f.write_text(json.dumps(gpu_info, indent=4))


if __name__ == '__main__':
    # crawl_cpu_gpu(True)
    # crawl_cpu_gpu(False)
    crawl_gpuinfo_batch()
