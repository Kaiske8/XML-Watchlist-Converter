import json
import os
import time
import urllib.parse
import xml.etree.ElementTree as ET

import requests

CACHE_FILE = "mal_ids.json"
OUTPUT_FILE = "aniwatch_full_list.xml"
OUTPUT_NOZERO = "aniwatch_full_list_nozero.xml"
JSON_FILES = ["watching.json", "completed.json", "plan-to-watch.json"]
STATUS_MAP = {"watching.json": 1, "completed.json": 2, "plan-to-watch.json": 6}


def load_json_file(filename):
    with open(filename, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    with open(CACHE_FILE, "r", encoding="utf-8") as handle:
        return json.load(handle)


def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as handle:
        json.dump(cache, handle, indent=2, ensure_ascii=False)


def query_jikan(title):
    url = "https://api.jikan.moe/v4/anime"
    params = {"q": title, "limit": 1}
    response = requests.get(url, params=params, timeout=15)
    if response.status_code == 429:
        raise RuntimeError("rate_limited")
    response.raise_for_status()
    data = response.json()
    results = data.get("data") or []
    if not results:
        return 0
    return int(results[0].get("mal_id", 0))


def get_mal_id(title, cache):
    if title in cache:
        return cache[title]

    attempts = 0
    while attempts < 4:
        attempts += 1
        try:
            mal_id = query_jikan(title)
            cache[title] = mal_id
            return mal_id
        except RuntimeError as exc:
            if str(exc) != "rate_limited":
                raise
            wait = 60 * attempts
            print(f"Rate limited on '{title}'. Waiting {wait}s...")
            time.sleep(wait)
        except Exception as exc:
            print(f"Error searching '{title}': {exc}")
            time.sleep(10)

    cache[title] = 0
    return 0


def build_records():
    records = {}
    for filename in JSON_FILES:
        data = load_json_file(filename)
        status = STATUS_MAP[filename]
        for item in data:
            title = item["title"].strip()
            if title not in records:
                records[title] = {"title": title, "status": status}
                continue
            existing = records[title]["status"]
            if status < existing:
                records[title]["status"] = status
    return list(records.values())


def create_xml(records, filename):
    root = ET.Element("myanimelist")
    myinfo = ET.SubElement(root, "myinfo")
    ET.SubElement(myinfo, "user_export_type").text = "1"

    for record in records:
        anime = ET.SubElement(root, "anime")
        ET.SubElement(anime, "series_animedb_id").text = str(record["mal_id"])
        ET.SubElement(anime, "series_title").text = record["title"]
        ET.SubElement(anime, "series_type").text = "1"
        ET.SubElement(anime, "series_episodes").text = "0"
        ET.SubElement(anime, "series_score").text = "0"
        ET.SubElement(anime, "series_status").text = "0"
        ET.SubElement(anime, "series_start").text = "0000-00-00"
        ET.SubElement(anime, "series_end").text = "0000-00-00"
        ET.SubElement(anime, "series_image").text = ""
        ET.SubElement(anime, "my_id").text = "0"
        ET.SubElement(anime, "my_watched_episodes").text = "0"
        ET.SubElement(anime, "my_start_date").text = "0000-00-00"
        ET.SubElement(anime, "my_finish_date").text = "0000-00-00"
        ET.SubElement(anime, "my_score").text = "0"
        ET.SubElement(anime, "my_status").text = str(record["status"])
        ET.SubElement(anime, "my_rated").text = "0"
        ET.SubElement(anime, "my_comments").text = ""
        ET.SubElement(anime, "my_times_watched").text = "0"
        ET.SubElement(anime, "my_rewatching").text = "0"
        ET.SubElement(anime, "my_rewatching_ep").text = "0"
        ET.SubElement(anime, "my_last_updated").text = "0"
        ET.SubElement(anime, "my_tags").text = ""
        ET.SubElement(anime, "my_rewatch_value").text = "0"
        ET.SubElement(anime, "my_recommender").text = "0"
        ET.SubElement(anime, "my_priority").text = "0"

    tree = ET.ElementTree(root)
    tree.write(filename, encoding="utf-8", xml_declaration=True)


def main():
    print("Loading anime lists...")
    records = build_records()
    cache = load_cache()

    print(f"Found {len(records)} unique anime titles.")
    for record in records:
        record["mal_id"] = get_mal_id(record["title"], cache)

    save_cache(cache)

    print(f"Writing full XML to {OUTPUT_FILE}...")
    create_xml(records, OUTPUT_FILE)

    nozero_records = [r for r in records if r["mal_id"] != 0]
    print(f"Writing no-zero XML to {OUTPUT_NOZERO} ({len(nozero_records)} entries)...")
    create_xml(nozero_records, OUTPUT_NOZERO)
    print("Done.")


if __name__ == "__main__":
    main()
