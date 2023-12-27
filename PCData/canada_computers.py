"""
This file is used to crawl Canada Computers items
"""
import json
import re
from pathlib import Path
from typing import NamedTuple

import js2py
import pandas as pd
import requests
from bs4 import BeautifulSoup, Tag, ResultSet
from hypy_utils import nlp_utils
from hypy_utils.logging_utils import setup_logger
from hypy_utils.nlp_utils import substr_between
from hypy_utils.tqdm_utils import tmap
from js2py.internals.simplex import JsException

log = setup_logger()


def get_match(pattern: str | re.Pattern, html: str) -> str | None:
    """
    Get the first match of a pattern in html

    :param pattern: regex pattern
    :param html: html to search in
    """
    match = re.search(pattern, html)
    if match is None:
        return None
    return match.group(1)


RE_ID = re.compile(r'data-item-id="(\d+)"')


class Product(NamedTuple):
    id: int
    item_id: str
    name: str
    brand: str
    categories: list[str]
    price: float
    specs: dict[str, str]


def crawl_page(url: str, p: int) -> list[Product]:
    """
    Crawl a page of Canada Computers items

    :param url: URL of an item listing page
    :param p: Page number
    :return: list of Product
    """
    items = []
    log.info(f"Crawling page {p}")
    page = requests.get(url, params={"page": p, "ajax": "true"})
    # We can't use BS4 because the html contains json that is not properly escaped

    # Find productTemplate
    products: list[str] = page.text.split("<div class=\"col-12 py-1 px-1 bg-white mb-1 productTemplate")[1:]

    for product in products:
        try:
            # Get ID (regex, data-item-id="(\d+)")
            id = substr_between(product, 'data-item-id="', '"')

            # Get gtag, eval it to get the product name
            js = substr_between(product, r"""onclick="gtag('event', 'select_item', """, ')" >')
            js = f"a = {js}; a"
            p = js2py.eval_js(js)['items'][0]

            # Get specs
            specs_html = substr_between(product, """<div class="d-inline pl-0_5" data-toggle="tooltip" data-html="true" title='""", "'>")
            specs_html = BeautifulSoup(specs_html, "html.parser")
            specs = [li.text.strip().split(":", 1) for li in specs_html.findAll("li")]
            specs = {k.strip(): v.strip() for k, v in specs}

            items.append(Product(
                id=id,
                item_id=p['item_id'],
                name=p['item_name'],
                brand=p['item_brand'],
                categories=[p['item_category'], p['item_category_2'], p['item_category_3'], p['item_category_4']],
                price=float(p['price']),
                specs=specs
            ))
            log.debug(f"> Got: {items[-1].name}")

        except ValueError:
            log.warning("Failed to parse product")
            continue

        except JsException as e:
            log.warning(f"JsException: {e}")
            continue

        except Exception as e:
            log.warning(f"Exception: {e}")
            continue

    return items


def crawl_url(url: str):
    """
    Crawl Canada Computers items

    :param url: url to crawl
    """
    file = Path("data/canada_computers_laptops.csv")

    if file.exists():
        return pd.read_csv(file)

    items = []
    i = 0
    batch_size = 20
    while True:
        r = list(range(i * batch_size + 1, (i + 1) * batch_size + 1))
        log.info(f"Crawling batch {i}")

        # Get batch
        batch = tmap(lambda p: crawl_page(url, p), r, max_workers=10)

        # Flatten
        items += [item for sublist in batch for item in sublist]

        # If at least one batch is empty, we are done
        if any([len(b) == 0 for b in batch]):
            log.info(f"Done at batch {i}")
            break

        i += 1

    file.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(items)
    df.to_csv(file, index=False)

    return items


if __name__ == '__main__':
    # cPath 710 is laptops
    crawl_url("https://www.canadacomputers.com/index.php?cPath=710")
