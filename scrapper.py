import requests
import re
import bs4
import csv

BASE_URL = "https://nzaca.org.nz/members/nzaca-provider-homes/"


def is_entry_title(t):
    """
    The site uses inconsistent tags for entry titles. A entry title is:
    1. H3 followed by p (containing detail)
    2. P with spans inside but not those containing details
    """
    return (t.name == "h3" and t.next_sibling.name == "p") or \
        (t.name == "p" and t.find("span")
         and t.text[0] not in ["a", "p", "e", "f", "w"])


def get_region_infos(url):
    """Retrieve title, phone, and email address for all entries in region."""

    region = bs4.BeautifulSoup(requests.get(url).content, features="lxml").find(id="ss-content")
    infos = []
    for title in region.find_all(is_entry_title):
        info = [title.text]
        detail = title.next_sibling
        phone = re.search(r"(?<=p:)[\s\d]*", detail.text)
        if phone:
            phone = phone.group().strip()
        email = detail.find(lambda t: t.name ==
                            "a" and t["href"].startswith("mailto"))
        if email:
            email = email["href"].lstrip("mailto:")
        info += [phone, email]
        infos.append(info)
    return infos


if __name__ == "__main__":
    response = requests.get(BASE_URL)
    bs = bs4.BeautifulSoup(response.content, features="lxml")
    nav = bs.find("ul", {"class": "side-nav"})
    links = [(a.text, a["href"].replace("/members/nzaca-provider-homes/", ""))
             for a in nav.find_all("a")]
    region_titles = []
    results = []
    for link in links:
        try:
            results.append(get_region_infos(BASE_URL + link[1]))
            region_titles.append(link[0])
        except:
            print("Have problem scraping ", link)
    with open("nzaca.csv", "wt") as f:
        writer = csv.writer(f)
        for i in range(len(results)):
            writer.writerow([region_titles[i]])
            writer.writerows(results[i])
