import requests, re
from time import time
from bs4 import BeautifulSoup
from typing import Tuple

DEFAULT_URL = "https://www.willhaben.at/iad/immobilien/mietwohnungen/mietwohnung-angebote?sfId=2b56243b-42ca-4fa1-a200-14b483179e25&isNavigation=true&NO_OF_ROOMS_BUCKET=3X3&NO_OF_ROOMS_BUCKET=4X4&rows=30&areaId=117223&areaId=117224&areaId=117225&areaId=117226&areaId=117227&areaId=117228&areaId=117229&areaId=117230&areaId=117231&page=1&PRICE_FROM=800&PRICE_TO=1300"
URL_PREFIX = "https://www.willhaben.at"

class HousesStore:
    def __init__(self):
        self.houses_set = {}
        self.last_update = 0
        self.users_time = {}

    def update(self, ids: list[str], urls: list[str], user_id: str | None = None) -> set[str]:
        current_time = time()
        update_set = {}
        for ide, url in zip(ids, urls):
            if ide not in self.houses_set:
                update_set[ide] = {'time': current_time, 'url': URL_PREFIX + url}

        self.houses_set.update(update_set)
        self.last_update = current_time

        if user_id:
            self.users_time[user_id] = current_time

        return {x["url"] for x in update_set.values()} if update_set else set()

    def is_updated(self, interval: float) -> bool:
        return time() - self.last_update >= interval
    
    def is_new(self, user_id: str) -> set[str]:
        last_user_time = self.users_time.get(user_id, 0)
        current_time = time()
        self.users_time[user_id] = current_time

        new_houses = [self.houses_set[k]["url"] for k in self.houses_set if self.houses_set[k]["time"] > last_user_time]
        new_houses = set(new_houses)  # Remove duplicates

        return new_houses


def request_wills_house_ids(url:str = DEFAULT_URL) -> list[str]:
    """
    Requests the willhaben.at website and returns a list of IDs of the houses.
    """
    resp = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
    soup = BeautifulSoup(resp.text, "html.parser")

    # Compile a regex for class names starting with "Box-sc-"
    box_re = re.compile(r'Box-sc-[A-Za-z0-9_-]+')

    matches = soup.find_all(
        "div",
        id=lambda x: bool(x) and x.isdigit(),           # numeric-only id
        class_=lambda classes: bool(classes) and bool(box_re.match(classes))
        # class_=lambda classes: bool(classes)
    )

    return [match.get("id") for match in matches] # type: ignore


def request_wills_house_ids_url(url:str = DEFAULT_URL) -> dict[str, dict]:
    """
    Requests the willhaben.at website and returns a list of IDs of the houses.
    """
    resp = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
    soup = BeautifulSoup(resp.text, "html.parser")

    # Compile a regex for class names starting with "Box-sc-"
    box_re = re.compile(r'Box-sc-[A-Za-z0-9_-]+')

    matches = soup.find_all(
        "div",
        id=lambda x: bool(x) and x.isdigit(),           # numeric-only id
        class_=lambda classes: bool(classes) and bool(box_re.match(classes))
        # class_=lambda classes: bool(classes)
    )

    solution = {}

    for div in matches:
        a_tags = div.find_all("a", href=True) # type: ignore
        for a in a_tags:
            ide = div.get("id") # type: ignore
            solution[ide] = {
                "text": a.get_text(strip=True),
                "url": a['href'] # type: ignore
            } 

    return solution

if __name__ == "__main__":
    ids = request_wills_house_ids_url()
    store = HousesStore()
    sol = store.update(list(ids.keys()), [data["url"] for data in ids.values()])
    print(f"New houses: {sol}")