import requests, re
from time import time
from bs4 import BeautifulSoup

DEFAULT_URL = "https://www.willhaben.at/iad/immobilien/mietwohnungen/mietwohnung-angebote?sfId=2b56243b-42ca-4fa1-a200-14b483179e25&isNavigation=true&NO_OF_ROOMS_BUCKET=3X3&NO_OF_ROOMS_BUCKET=4X4&rows=30&areaId=117223&areaId=117224&areaId=117225&areaId=117226&areaId=117227&areaId=117228&areaId=117229&areaId=117230&areaId=117231&page=1&PRICE_FROM=700&PRICE_TO=1300"

class HousesStore:
    def __init__(self):
        self.houses_set = {}
        self.last_update = 0

    def update(self, ids: list[str]) -> int:
        current_time = time()
        update_set = {}
        for ide in ids:
            if ide not in self.houses_set:
                update_set[ide] = current_time
        
        self.houses_set.update(update_set)
        self.last_update = current_time
        
        return len(update_set) > 0

    def is_updated(self, interval: float) -> bool:
        return time() - self.last_update >= interval
    
    def is_new(self, current_time: float) -> bool:
        for k in self.houses_set:
            if self.houses_set[k] > current_time:
                return True
        return False


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

if __name__ == "__main__":
    ids = request_wills_house_ids()
    print(ids)
    print(f"Found {len(ids)} houses.")