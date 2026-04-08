import os
import re
import time
import math
import requests
import cv2
from pathlib import Path

# ---------------------------------------------------------------------------
# IUCN Red List API v4  (https://api.iucnredlist.org)
# Requires a free API token – register at: https://api.iucnredlist.org/users/sign_up
# Set the token in the environment:  export IUCN_API_TOKEN=<your_token>
#
# Images are sourced from the Wikipedia REST API (no key required).
# ---------------------------------------------------------------------------

IUCN_API_BASE = "https://api.iucnredlist.org/api/v4"
WIKI_API_BASE = "https://en.wikipedia.org/api/rest_v1"
HEADERS = {"User-Agent": "cclarkson.co.uk/1.0 (endangered-species-art-project)"}

# EN = Endangered, CR = Critically Endangered
ENDANGERED_CATEGORIES = {"EN", "CR"}

CATEGORY_LABELS = {
    "CR": "Critically Endangered",
    "EN": "Endangered",
    "VU": "Vulnerable",
    "NT": "Near Threatened",
    "LC": "Least Concern",
    "DD": "Data Deficient",
    "EX": "Extinct",
    "EW": "Extinct in the Wild",
}


# ---------------------------------------------------------------------------
# IUCN API helpers
# ---------------------------------------------------------------------------

def get_endangered_species(token):
    """Return a list of all EN/CR taxa from the IUCN Red List API v4."""
    species_list = []
    page = 0
    while True:
        url = f"{IUCN_API_BASE}/taxa/page/{page}"
        resp = requests.get(url, params={"token": token}, headers=HEADERS, timeout=30)
        if resp.status_code != 200:
            print(f"Warning: IUCN API returned {resp.status_code} on page {page}. Stopping pagination.")
            break
        data = resp.json()
        taxa = data.get("taxa", [])
        if not taxa:
            break
        for taxon in taxa:
            if taxon.get("category") in ENDANGERED_CATEGORIES:
                species_list.append(taxon)
        print(f"  Page {page}: {len(taxa)} taxa fetched, {len(species_list)} endangered so far")
        page += 1
        time.sleep(0.5)
    return species_list


def get_species_narrative(species_id, token):
    """Return the population narrative text for a species (plain text, HTML stripped)."""
    url = f"{IUCN_API_BASE}/taxa/{species_id}/narrative"
    try:
        resp = requests.get(url, params={"token": token}, headers=HEADERS, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            # v4 nests narrative under a 'narrative' key; population is an HTML string
            narrative = data.get("narrative", {})
            pop_html = narrative.get("population", "") or ""
            if pop_html:
                # Strip HTML tags to get plain text
                return re.sub(r"<[^>]+>", " ", pop_html).strip()
    except Exception as e:
        print(f"  Warning: narrative fetch failed for {species_id}: {e}")
    return "Unknown"


def get_species_habitats(species_id, token):
    """Return a comma-separated string of habitat names for a species."""
    url = f"{IUCN_API_BASE}/taxa/{species_id}/habitats"
    try:
        resp = requests.get(url, params={"token": token}, headers=HEADERS, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            habitats = data.get("habitats", [])
            names = [h.get("description", "").strip() for h in habitats if h.get("description")]
            return ", ".join(names) if names else "Unknown"
    except Exception as e:
        print(f"  Warning: habitats fetch failed for {species_id}: {e}")
    return "Unknown"


def get_species_countries(species_id, token):
    """Return a comma-separated string of country names for a species."""
    url = f"{IUCN_API_BASE}/taxa/{species_id}/countries"
    try:
        resp = requests.get(url, params={"token": token}, headers=HEADERS, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            countries = data.get("countries", [])
            names = [c.get("country", "").strip() for c in countries if c.get("country")]
            return ", ".join(names) if names else "Unknown"
    except Exception as e:
        print(f"  Warning: countries fetch failed for {species_id}: {e}")
    return "Unknown"


# ---------------------------------------------------------------------------
# Wikipedia image helper
# ---------------------------------------------------------------------------

def get_species_image(common_name, scientific_name):
    """
    Return a URL for a species image using the Wikipedia REST API.
    Tries common_name first, falls back to scientific_name.
    Returns None if no image found.
    """
    for name in [common_name, scientific_name]:
        if not name:
            continue
        encoded = requests.utils.quote(name.replace(" ", "_"))
        url = f"{WIKI_API_BASE}/page/summary/{encoded}"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                thumbnail = data.get("thumbnail", {})
                img_url = thumbnail.get("source", "")
                if img_url:
                    # Request a larger version where possible
                    for small in ["/150px-", "/240px-", "/320px-"]:
                        img_url = img_url.replace(small, "/800px-")
                    return img_url
        except Exception as e:
            print(f"  Warning: Wikipedia image fetch failed for '{name}': {e}")
    return None


# ---------------------------------------------------------------------------
# Population parser (unchanged from original)
# ---------------------------------------------------------------------------

def calculate_population(animal):
    """
    Parse the population text (animal[1][1][1]) into numeric bounds.
    Returns [min, max], ['Unknown'], or ['Extinct'].
    """
    pop_text = animal[1][1][1]
    text = pop_text.split(' ')
    nums = []
    for word in text:
        for subsplit in word.split('-'):
            try:
                num = float(subsplit.replace(',', ''))
                if num not in nums:
                    nums.append(num)
            except ValueError:
                pass
    if not nums:
        if 'Unknown' in pop_text:
            return ['Unknown']
        elif 'extinct' in pop_text.lower():
            return ['Extinct']
        else:
            return ['Unknown']
    if len(nums) == 1:
        nums = [nums[0], nums[0]]
    if len(nums) > 2:
        nums = [nums[0], nums[-1]]
    return nums


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    TOKEN = os.environ.get("IUCN_API_TOKEN")
    if not TOKEN:
        print("Error: IUCN_API_TOKEN environment variable not set.")
        print("Register for a free token at: https://api.iucnredlist.org/users/sign_up")
        exit(1)

    ROOT = "../apps/apps_static/WWF"
    img_ROOT = "../apps_static/WWF"

    # ------------------------------------------------------------------
    # 1. Fetch endangered species list from IUCN
    # ------------------------------------------------------------------
    print("Fetching Endangered/Critically Endangered species from IUCN Red List...")
    all_species = get_endangered_species(TOKEN)
    print(f"Total: {len(all_species)} species to process\n")

    # ------------------------------------------------------------------
    # 2. Fetch details for each species
    # ------------------------------------------------------------------
    imgHTMLList = []
    for taxon in all_species:
        species_id = taxon.get("taxonid") or taxon.get("sis_id")
        sci_name = taxon.get("scientific_name", "")
        common_name = taxon.get("main_common_name", "")
        category = taxon.get("category", "")

        display_name = common_name or sci_name
        filename = display_name.lower().replace(" ", "_").replace("-", "_")
        if not filename or not species_id:
            continue

        print(f"Processing: {display_name}")

        pop_text = get_species_narrative(species_id, TOKEN)
        time.sleep(0.3)
        habitats = get_species_habitats(species_id, TOKEN)
        time.sleep(0.3)
        places = get_species_countries(species_id, TOKEN)
        time.sleep(0.3)

        # Build details list in the same format as the old grabDetails()
        details = [
            ["Status", CATEGORY_LABELS.get(category, category)],
            ["Population", pop_text],
            ["Scientific Name", sci_name],
            ["Habitats", habitats],
            ["Places", places],
        ]

        iucn_url = f"https://www.iucnredlist.org/species/{species_id}"
        image_url = get_species_image(common_name, sci_name)

        imgHTMLList.append([
            iucn_url,
            details,
            image_url,
            filename,
            "{}/animalImages/{}.jpg".format(ROOT, filename),
        ])

    # ------------------------------------------------------------------
    # 3. Create output directories
    # ------------------------------------------------------------------
    for subdir in ["", "/animalImages", "/resizedImages", "/outputImages"]:
        Path(ROOT + subdir).mkdir(parents=True, exist_ok=True)

    # Clear existing files
    for subdir in ["/animalImages", "/resizedImages", "/outputImages"]:
        for f in os.listdir(ROOT + subdir):
            os.remove(ROOT + subdir + "/" + f)

    # ------------------------------------------------------------------
    # 4. Download images
    # ------------------------------------------------------------------
    print("\nDownloading images...")
    for entry in imgHTMLList:
        image_url = entry[2]
        dest_path = entry[4]
        if not image_url:
            print(f"  No image found for {entry[3]}")
            continue
        try:
            resp = requests.get(image_url, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                with open(dest_path, "wb") as f:
                    f.write(resp.content)
            else:
                print(f"  Image download failed for {entry[3]}: HTTP {resp.status_code}")
        except Exception as e:
            print(f"  Image download error for {entry[3]}: {e}")

    # ------------------------------------------------------------------
    # 5. Pixelate images and build CSV
    # ------------------------------------------------------------------
    print("\nProcessing images...")
    final_csv = []
    for animal in imgHTMLList:
        numList = calculate_population(animal)
        if numList is None:
            continue
        if not os.path.exists(animal[4]):
            continue

        img = cv2.imread(animal[4])
        if img is None:
            continue

        animalName = animal[3].replace(" ", "")
        img = cv2.resize(img, (800, 800))
        cv2.imwrite("{}/resizedImages/{}.jpg".format(ROOT, animalName), img)

        if len(numList) == 1:
            if numList[0] == "Unknown":
                altImage = "Unknown"
                numList[0] = 0
                continue
            elif numList[0] == "Extinct":
                numList[0] = 0
                altImage = "Extinct"

            placeholder = cv2.imread("{}/{}.jpg".format(ROOT, altImage))
            if placeholder is not None:
                placeholder = cv2.resize(placeholder, (800, 800))
                cv2.imwrite("{}/outputImages/{}.jpg".format(ROOT, animalName), placeholder)
        else:
            total = sum(numList)
            if total != 0:
                avg = float(total) / float(len(numList))
                width = math.sqrt(avg)
                height = int(math.ceil(width))
                width = int(math.floor(width))
                img_small = cv2.resize(img, (max(width, 1), max(height, 1)))
                img_pixel = cv2.resize(img_small, (800, 800), interpolation=cv2.INTER_NEAREST)
                cv2.imwrite("{}/outputImages/{}.jpg".format(ROOT, animalName), img_pixel)

        tmp = [numList[0]]
        for row in animal:
            tmp.append(row)
        tmp.append("{}/resizedImages/{}.jpg".format(img_ROOT, animalName))
        tmp.append("{}/outputImages/{}.jpg".format(img_ROOT, animalName))
        final_csv.append(tmp)

    with open("{}/list.csv".format(ROOT), "w") as f:
        for row in final_csv:
            f.write(str(row) + "\n")

    print(f"\nDone! {len(final_csv)} animals written to {ROOT}/list.csv")
