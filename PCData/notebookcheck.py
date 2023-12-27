"""
This file is used to crawl notebookcheck data and store it as a csv
"""
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup
from hypy_utils import write

def crawl_gpu(name: str, url: str):
    """
    Crawl gpu benchmark data
    """
    file = Path(f"data/notebookcheck/{name}.csv")

    if file.exists():
        return pd.read_csv(file)

    html = Path(f"data/notebookcheck/{name}.html")
    if html.exists():
        page = html.read_text()
    else:
        page = requests.get(url).text
        write(html, page)
    bs = BeautifulSoup(page, "html.parser")

    table = bs.find("table", {"id": "sortierbare_tabelle"})
    rows = table.findAll("tr")

    # Find header
    header = table.find("tr", {"class": "header"})
    names = [v.text.strip().replace("\u00a0", " ") for v in header.findAll("td")[1:]]

    gpu_list = []
    for row in rows:
        # Skip headers
        if row.get("class") == ["header"]:
            continue

        cols = row.findAll("td")
        if len(cols) == 0:
            continue

        # Map values to names
        values = [v.text.strip().replace("\u00a0", " ") for v in cols[1:]]
        gpu_list.append(dict(zip(names, values)))

    file.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(gpu_list)
    df.to_csv(file, index=False)

    file.write_text(file.read_text().replace("\u00a0", " "))

    return df


if __name__ == '__main__':
    crawl_gpu("mobile-gpu", "https://www.notebookcheck.net/Mobile-Graphics-Cards-Benchmark-List.844.0.html?type=&sort=&professional=0&multiplegpus=1&perfrating=1&or=0&3dmark13_ice_gpu=1&3dmark13_cloud=1&3dmark13_cloud_gpu=1&3dmark11=1&3dmark11_gpu=1&3dmark13_fire=1&3dmark13_fire_gpu=1&3dmark13_time_spy=1&3dmark13_time_spy_gpu=1&vantage3dmark=1&3dmark06=1&3dmark01=1&glbenchmark=1&gfxbench30=1&gfxbench31=1&bmg12_vul_med_off=1&basemarkx11_med=1&basemarkx11_high=1&heaven3_dx=1&valley_dx=1&cb15_ogl=1&cinebench10_ogl=1&computemark_result=1&luxmark_sala=1&gpu_fullname=1&codename=1&architecture=1&corespeed=1&boostspeed=1&memoryspeed=1&memorybus=1&memorytype=1&maxmemory=1&directx=1&opengl=1&technology=1&daysold=1")
    crawl_gpu("all-gpu", "https://www.notebookcheck.net/Mobile-Graphics-Cards-Benchmark-List.844.0.html?type=&sort=&professional=0&multiplegpus=1&deskornote=2&perfrating=1&or=0&3dmark13_ice_gpu=1&3dmark13_cloud=1&3dmark13_cloud_gpu=1&3dmark11=1&3dmark11_gpu=1&3dmark13_fire=1&3dmark13_fire_gpu=1&3dmark13_time_spy=1&3dmark13_time_spy_gpu=1&vantage3dmark=1&3dmark06=1&3dmark01=1&glbenchmark=1&gfxbench30=1&gfxbench31=1&bmg12_vul_med_off=1&basemarkx11_med=1&basemarkx11_high=1&heaven3_dx=1&valley_dx=1&cb15_ogl=1&cinebench10_ogl=1&computemark_result=1&luxmark_sala=1&gpu_fullname=1&codename=1&architecture=1&corespeed=1&boostspeed=1&memoryspeed=1&memorybus=1&memorytype=1&maxmemory=1&directx=1&opengl=1&technology=1&daysold=1")
    crawl_gpu("mobile-cpu", "https://www.notebookcheck.net/Mobile-Processors-Benchmark-List.2436.0.html?type=&sort=&archive=1&perfrating=1&or=0&3dmark06cpu=1&cinebench10_s=1&cinebench10_m=1&cb11_single=1&cb11=1&cinebench_r15_single=1&cinebench_r15_multi=1&cinebench_r20_single=1&cinebench_r20_multi=1&cinebench_r23_single=1&cinebench_r23_multi=1&superpi1m=1&superpi32m=1&wprime_32=1&wprime_1024=1&winrar=1&x264_pass1=1&x264_pass2=1&x265=1&truecrypt_aes=1&truecrypt_twofish=1&truecrypt_serpent=1&blender=1&blender3_cpu=1&7-zip_single=1&7-zip_multiple=1&geekbench2=1&geekbench3_single=1&geekbench3_multi=1&geekbench4_1_single=1&geekbench4_1_multi=1&geekbench5_single=1&geekbench5_multi=1&geekbench5_1_single=1&geekbench5_1_multi=1&geekbench6_2_single=1&geekbench6_2_multi=1&passmark_cpu=1&sunspider=1&octane2=1&jetstream2=1&speedometer=1&webxprt3=1&webxprt4=1&cpu_fullname=1&codename=1&series=1&l2cache=1&l3cache=1&fsb=1&tdp=1&mhz=1&turbo_mhz=1&cores=1&threads=1&technology=1&architecture=1&64bit=1&daysold=1&gpu_name=1")
    crawl_gpu("all-cpu", "https://www.notebookcheck.net/Mobile-Processors-Benchmark-List.2436.0.html?type=&sort=&deskornote=2&archive=1&perfrating=1&or=0&3dmark06cpu=1&cinebench10_s=1&cinebench10_m=1&cb11_single=1&cb11=1&cinebench_r15_single=1&cinebench_r15_multi=1&cinebench_r20_single=1&cinebench_r20_multi=1&cinebench_r23_single=1&cinebench_r23_multi=1&superpi1m=1&superpi32m=1&wprime_32=1&wprime_1024=1&winrar=1&x264_pass1=1&x264_pass2=1&x265=1&truecrypt_aes=1&truecrypt_twofish=1&truecrypt_serpent=1&blender=1&blender3_cpu=1&7-zip_single=1&7-zip_multiple=1&geekbench2=1&geekbench3_single=1&geekbench3_multi=1&geekbench4_1_single=1&geekbench4_1_multi=1&geekbench5_single=1&geekbench5_multi=1&geekbench5_1_single=1&geekbench5_1_multi=1&geekbench6_2_single=1&geekbench6_2_multi=1&passmark_cpu=1&sunspider=1&octane2=1&jetstream2=1&speedometer=1&webxprt3=1&webxprt4=1&cpu_fullname=1&codename=1&series=1&l2cache=1&l3cache=1&fsb=1&tdp=1&mhz=1&turbo_mhz=1&cores=1&threads=1&technology=1&architecture=1&64bit=1&daysold=1&gpu_name=1")
