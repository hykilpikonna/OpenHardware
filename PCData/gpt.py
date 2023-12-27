from pathlib import Path

import openai
import pandas as pd
from hypy_utils.logging_utils import setup_logger

log = setup_logger()


def obtain_info_from_name(name: str):
    eg_info = """MSI Modern 15 Consumer Laptop 15.6"" FHD 144Hz Intel i7-1255U Intel Iris Xe 16GB 512GB SSD Windows 11 Home FLLR229YY (Open Box)"""
    eg_resp = """
Brand: MSI
Model: Modern 15
Model Code: FLLR229YY
CPU: Intel i7-1255U
GPU: Intel Iris Xe
RAM: 16GB
Storage: 512GB SSD
OS: Windows 11 Home
Screen: 15.6"
Resolution: FHD
Refresh Rate: 144Hz
    """
    openai_prompt = "Please extract product specifications from the following product name:\n\n"

    print(f"\n\n> {name}")
    complete = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are a computer science student examining laptops on sale."},
            {"role": "user",
             "content": f"{openai_prompt}{eg_info}"},
            {"role": "assistant",
             "content": f'"{eg_resp}"'},
            {"role": "user",
             "content": f"{openai_prompt}{name}"},
        ]
    )

    m = complete.choices[0].message.content.strip().strip('"').strip()
    print(f"{m}")
    return {k: v for k, v in [line.split(": ", 1) for line in m.splitlines()]}


if __name__ == '__main__':
    # Read from canada_computers_laptops.csv
    csv = pd.read_csv("data/canada_computers_laptops.csv")
    new_csv_f = Path("data/canada_computers_laptops_gpt.csv")
    new_csv = [] if not new_csv_f.exists() else pd.read_csv(new_csv_f).to_dict(orient="records")

    # Extract specs from name
    for i, row in csv.iterrows():
        if i < len(new_csv):
            continue
        name = row["name"]
        specs = obtain_info_from_name(name)
        for k in specs:
            if k not in {'Brand', 'Model', 'Model Code', 'CPU', 'GPU', 'RAM', 'Storage', 'OS', 'Screen', 'Resolution',
                         'Refresh Rate'}:
                log.warning(f"Unknown key: {k}")
        new_csv.append({**row, "gpt_specs": specs})

        # Save to csv
        pd.DataFrame(new_csv).to_csv(new_csv_f, index=False)
