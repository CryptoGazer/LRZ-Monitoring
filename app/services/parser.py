import requests
from bs4 import BeautifulSoup, Tag

import re
from pprint import pprint

ROOT_URL = "https://wlan.lrz.de/apstat/"
ALIAS_TO_AP_NAME = {
    "MW_MAGISTRALE": ("apa06-0w0",),  # 0101, Magistrale MW Gebäudeteil 1
    "TUM_IMMAT": ("apa20-0bb",),  # 0136, Immatrikulationshalle
    "AUDIMAX": ("apa09-0bb", "apa10-0bb"),  # 2 rows, parse separately afterwards (Freigelaende vor Audimax)
    "MI_MAGISTRALE": ("",),  # ask Elias
    "FREISING_CAMPUS": ("apa13-0qi",)  # only foyer for now, ask Elias
}


def retrieve_actual_connections(networks_stats: list[Tag], filter_network: str) -> int | None:
    assert filter_network in ('e', 'b')
    match filter_network:
        case 'e':
            filter_network = "eduroam"
        case 'b':
            filter_network = "@BayernWLAN"

    for network in networks_stats:
        if filter_network in network.text:
            m = re.search(r'\(([^()]*)\)', network.text).group(1)
            return int(m.split(" - ")[1])

    print(f"\nWARNING: NETWORK {filter_network} COULDN'T BE PARSED!\n")
    return 0


def parse_tag(location: str) -> tuple[int, int] | None:
    ap_names = ALIAS_TO_AP_NAME.get(location)
    if ap_names:
        eduroam_conn = 0
        bayern_wlan_conn = 0
        for ap_name in ap_names:
            apstat_response = requests.get(ROOT_URL)
            soup = BeautifulSoup(apstat_response.content, "html.parser")
            all_rows = soup.find("table", class_ = "tablesorter").find("tbody").find_all("tr", recursive=False)
            location_row_tds = None
            for row in all_rows:
                tds = row.find_all("td", recursive=False)
                if tds[2].string == ap_name:
                    location_row_tds = tds
                    break
            if location_row_tds:
                networks = location_row_tds[5].find("table").find_all("tr", recursive=False)
                pprint(networks)
                eduroam_conn += retrieve_actual_connections(networks, 'e')
                bayern_wlan_conn += retrieve_actual_connections(networks, 'b')
            else:
                print(f"\nWARNING: NO ROW BY LOCATION: {location}!\n")
        return eduroam_conn, bayern_wlan_conn
    else:
        print(f"\nWARNING: NO AP NAME BY LOCATION: {location}!\n")


if __name__ == "__main__":
    print(parse_tag("MW_MAGISTRALE"))
    print()
    print(parse_tag("TUM_IMMAT"))
    print()
    print(parse_tag("FREISING_CAMPUS"))
    print()
    print(parse_tag("AUDIMAX"))
