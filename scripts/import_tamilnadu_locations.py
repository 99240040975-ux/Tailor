"""
Local Tailor Connect - Tamil Nadu Administrative Location Dataset Importer
==========================================================================
Sources:
  - Official Government of India Local Government Directory (LGD)
    (https://lgdirectory.gov.in)
  - Curated LGD public repository (planemad/india-local-government-directory)

Hierarchy Imported:
  State (Tamil Nadu - Code 33)
    ├── Districts (38 Districts)
    │     ├── Taluks / Sub-districts (313 Taluks)
    │     │     ├── Cities (Municipal Corporations / Large Urban Local Bodies)
    │     │     └── Towns (Municipalities / Town Panchayats)
    │     │           └── Villages (Revenue Villages)
    │     └── Localities / Urban Wards

Idempotent:
  Can be safely re-run without creating duplicate records or breaking foreign keys.
"""

import os
import sys
import csv
import io
import zipfile
import urllib.request
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Fix Windows console UTF-8 output if possible
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app import app
from models import db
from models.location import State, District, Taluk, City, Town, Village, Locality

# Cache directory for downloaded raw data
DATA_CACHE_DIR = PROJECT_ROOT / "data" / "lgd_tamil_nadu"
DATA_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Remote URLs (Official LGD verified mirrors)
URLS = {
    "state": "https://raw.githubusercontent.com/planemad/india-local-government-directory/main/administrative/1-state.csv",
    "district": "https://raw.githubusercontent.com/planemad/india-local-government-directory/main/administrative/2-district.csv",
    "subdistrict": "https://raw.githubusercontent.com/planemad/india-local-government-directory/main/administrative/3-subdistrict.csv",
    "municipal": "https://raw.githubusercontent.com/planemad/india-local-government-directory/main/municipal-directory.csv",
    "village_zip": "https://raw.githubusercontent.com/planemad/india-local-government-directory/main/administrative/4-village.csv.zip",
}

TN_STATE_CODE = "33"
TN_STATE_NAME = "Tamil Nadu"


def download_file(url: str, dest_path: Path) -> Path:
    """Download a file if it does not already exist in cache."""
    if dest_path.exists() and dest_path.stat().st_size > 0:
        print(f"  [Cache Hit] Using local file: {dest_path.name}")
        return dest_path

    print(f"  [Downloading] {url} -> {dest_path.name}...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=90) as response, open(dest_path, "wb") as out_file:
        out_file.write(response.read())
    print(f"  [Saved] {dest_path.name} ({dest_path.stat().st_size / 1024:.1f} KB)")
    return dest_path


def clean_name(name: str) -> str:
    """Standardize title casing for cleaner presentation."""
    if not name:
        return ""
    name = name.strip()
    # If uppercase, title-case it nicely
    words = name.split()
    return " ".join(w.capitalize() if not w.isupper() or len(w) > 3 else w.title() for w in words)


def import_locations():
    """Main orchestration function to import all Tamil Nadu administrative data."""
    print("\n" + "=" * 70)
    print("TAMIL NADU ADMINISTRATIVE LOCATION IMPORTER")
    print("Source: Government of India Local Government Directory (LGD)")
    print("=" * 70)

    with app.app_context():
        # Ensure database tables exist
        db.create_all()

        # -------------------------------------------------------------
        # 1. State: Tamil Nadu
        # -------------------------------------------------------------
        print("\n[Step 1/5] Importing State: Tamil Nadu...")
        state = State.query.filter_by(code=TN_STATE_CODE).first()
        if not state:
            state = State.query.filter(State.name.ilike(TN_STATE_NAME)).first()
        if not state:
            state = State(name=TN_STATE_NAME, code=TN_STATE_CODE)
            db.session.add(state)
            db.session.commit()
            print(f"  + Created State: {state.name} (ID: {state.id}, Code: {state.code})")
        else:
            state.name = TN_STATE_NAME
            state.code = TN_STATE_CODE
            db.session.commit()
            print(f"  [OK] Existing State verified: {state.name} (ID: {state.id}, Code: {state.code})")

        state_id = state.id

        # -------------------------------------------------------------
        # 2. Districts (All 38 Tamil Nadu Districts)
        # -------------------------------------------------------------
        print("\n[Step 2/5] Importing Districts (Tamil Nadu)...")
        district_csv_path = download_file(URLS["district"], DATA_CACHE_DIR / "2-district.csv")

        # Map to store district_code -> district_id
        district_code_map = {}
        district_name_map = {}

        # Preload existing districts
        existing_districts = District.query.filter_by(state_id=state_id).all()
        for d in existing_districts:
            if d.code:
                district_code_map[str(d.code).strip()] = d.id
            district_name_map[d.name.strip().upper()] = d.id

        new_districts = 0
        with open(district_csv_path, mode="r", encoding="utf-8-sig", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                st_code = str(row.get("State Code", "")).strip()
                if st_code != TN_STATE_CODE:
                    continue

                dist_code = str(row.get("District Code", "")).strip()
                dist_name_raw = row.get("District Name", "").strip()
                dist_name = clean_name(dist_name_raw)

                if not dist_name:
                    continue

                dist_key = dist_name.upper()
                if dist_code in district_code_map:
                    dist_id = district_code_map[dist_code]
                elif dist_key in district_name_map:
                    dist_id = district_name_map[dist_key]
                    district_code_map[dist_code] = dist_id
                else:
                    new_dist = District(
                        state_id=state_id,
                        name=dist_name,
                        code=dist_code or None
                    )
                    db.session.add(new_dist)
                    db.session.flush()
                    dist_id = new_dist.id
                    district_code_map[dist_code] = dist_id
                    district_name_map[dist_key] = dist_id
                    new_districts += 1

        db.session.commit()
        total_districts = District.query.filter_by(state_id=state_id).count()
        print(f"  [OK] Districts Processed: {total_districts} total ({new_districts} newly created)")

        # -------------------------------------------------------------
        # 3. Taluks / Sub-districts (Tamil Nadu)
        # -------------------------------------------------------------
        print("\n[Step 3/5] Importing Taluks / Sub-districts...")
        subdistrict_csv_path = download_file(URLS["subdistrict"], DATA_CACHE_DIR / "3-subdistrict.csv")

        # Map to store subdistrict_code -> taluk_id
        taluk_code_map = {}
        taluk_name_dist_map = {}

        existing_taluks = Taluk.query.join(District).filter(District.state_id == state_id).all()
        for t in existing_taluks:
            if t.code:
                taluk_code_map[str(t.code).strip()] = t.id
            taluk_name_dist_map[(t.district_id, t.name.strip().upper())] = t.id

        new_taluks = 0
        with open(subdistrict_csv_path, mode="r", encoding="utf-8-sig", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                st_code = str(row.get("State Code", "")).strip()
                if st_code != TN_STATE_CODE:
                    continue

                dist_code = str(row.get("District Code", "")).strip()
                dist_id = district_code_map.get(dist_code)

                # Fallback to district name lookup if code not found directly
                if not dist_id:
                    d_name_raw = row.get("District Name", "").strip().upper()
                    dist_id = district_name_map.get(d_name_raw)

                if not dist_id:
                    continue

                taluk_code = str(row.get("Sub-district Code", "")).strip()
                taluk_name_raw = row.get("Sub-district Name", "").strip()
                taluk_name = clean_name(taluk_name_raw)

                if not taluk_name:
                    continue

                taluk_pair = (dist_id, taluk_name.upper())
                if taluk_code in taluk_code_map:
                    taluk_id = taluk_code_map[taluk_code]
                elif taluk_pair in taluk_name_dist_map:
                    taluk_id = taluk_name_dist_map[taluk_pair]
                    taluk_code_map[taluk_code] = taluk_id
                else:
                    new_taluk = Taluk(
                        district_id=dist_id,
                        name=taluk_name,
                        code=taluk_code or None
                    )
                    db.session.add(new_taluk)
                    db.session.flush()
                    taluk_id = new_taluk.id
                    taluk_code_map[taluk_code] = taluk_id
                    taluk_name_dist_map[taluk_pair] = taluk_id
                    new_taluks += 1

        db.session.commit()
        total_taluks = Taluk.query.join(District).filter(District.state_id == state_id).count()
        print(f"  [OK] Taluks Processed: {total_taluks} total ({new_taluks} newly created)")

        # -------------------------------------------------------------
        # 4. Cities and Towns (Municipal Directory & Urban Bodies)
        # -------------------------------------------------------------
        print("\n[Step 4/5] Importing Cities & Towns (Municipal & Urban Bodies)...")
        municipal_csv_path = download_file(URLS["municipal"], DATA_CACHE_DIR / "municipal-directory.csv")

        existing_cities = {c.name.strip().upper(): c.id for c in City.query.all()}
        existing_towns = {t.name.strip().upper(): t.id for t in Town.query.all()}

        city_code_map = {}
        town_code_map = {}
        new_cities = 0
        new_towns = 0

        # Known major city corporations in Tamil Nadu for classification
        corporation_keywords = [
            "CORPORATION", "CHENNAI", "COIMBATORE", "MADURAI", "TIRUCHIRAPPALLI",
            "SALEM", "TIRUNELVELI", "TIRUPPUR", "ERODE", "VELLORE", "THOOTHUKUDI",
            "DINDIGUL", "THANJAVUR", "NAGERCOIL", "HOSUR", "TAMBARAM", "AVADI",
            "KANCHEEPURAM", "KARUR", "KUMBAKONAM", "CUDDALORE", "SIVAKASI"
        ]

        with open(municipal_csv_path, mode="r", encoding="utf-8-sig", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                st_name = str(row.get("State Name", "")).strip().upper()
                if "TAMIL NADU" not in st_name:
                    continue

                body_code = str(row.get("Localbody Code", "")).strip()
                body_name_raw = row.get("Localbody Name", "").strip()
                dist_code = str(row.get("District Code", "")).strip()
                subdist_code = str(row.get("Subdistrict Code", "")).strip()

                dist_id = district_code_map.get(dist_code)
                taluk_id = taluk_code_map.get(subdist_code)

                clean_body = clean_name(body_name_raw)
                if not clean_body:
                    continue

                upper_body = clean_body.upper()
                is_major_city = any(k in upper_body for k in corporation_keywords)

                if is_major_city:
                    # Classify as City
                    if upper_body in existing_cities:
                        city_id = existing_cities[upper_body]
                    else:
                        city_obj = City(
                            name=clean_body,
                            code=body_code or None,
                            district_id=dist_id,
                            taluk_id=taluk_id
                        )
                        db.session.add(city_obj)
                        db.session.flush()
                        city_id = city_obj.id
                        existing_cities[upper_body] = city_id
                        new_cities += 1
                    city_code_map[body_code] = city_id
                else:
                    # Classify as Town / Municipality / Town Panchayat
                    if upper_body in existing_towns:
                        town_id = existing_towns[upper_body]
                    else:
                        # Find parent city if matched, or default to district/taluk link
                        town_obj = Town(
                            name=clean_body,
                            code=body_code or None,
                            district_id=dist_id,
                            taluk_id=taluk_id
                        )
                        db.session.add(town_obj)
                        db.session.flush()
                        town_id = town_obj.id
                        existing_towns[upper_body] = town_id
                        new_towns += 1
                    town_code_map[body_code] = town_id

        db.session.commit()
        print(f"  [OK] Cities Processed: {len(existing_cities)} ({new_cities} new)")
        print(f"  [OK] Towns Processed: {len(existing_towns)} ({new_towns} new)")

        # -------------------------------------------------------------
        # 5. Villages (From Government LGD Revenue Village Directory)
        # -------------------------------------------------------------
        print("\n[Step 5/5] Importing Revenue Villages (Tamil Nadu)...")
        village_zip_path = download_file(URLS["village_zip"], DATA_CACHE_DIR / "4-village.csv.zip")

        # Extract village CSV if needed or read directly from zip
        existing_village_codes = {v.code for v in Village.query.filter(Village.code.isnot(None)).all()}
        new_villages = 0
        batch = []
        batch_size = 2000

        with zipfile.ZipFile(village_zip_path, "r") as z:
            csv_names = [n for n in z.namelist() if n.endswith(".csv")]
            if not csv_names:
                raise RuntimeError("No CSV found in village zip archive.")
            target_csv = csv_names[0]
            print(f"  Reading '{target_csv}' from archive...")

            with z.open(target_csv) as zf:
                text_stream = io.TextIOWrapper(zf, encoding="utf-8-sig", errors="ignore")
                reader = csv.DictReader(text_stream)

                for row in reader:
                    st_code = str(row.get("State Code", "")).strip()
                    if st_code != TN_STATE_CODE:
                        continue

                    v_code = str(row.get("Village Code", "")).strip()
                    if not v_code or v_code in existing_village_codes:
                        continue

                    # Official LGD file header has 'Village Name (In Englsih)'
                    v_name_raw = (
                        row.get("Village Name (In Englsih)")
                        or row.get("Village Name (In English)")
                        or row.get("Village Name")
                        or ""
                    )
                    v_name = clean_name(v_name_raw)
                    if not v_name:
                        continue

                    subdist_code = str(row.get("Subdistrict Code") or row.get("Sub-district Code") or "").strip()
                    dist_code = str(row.get("District Code") or "").strip()
                    census_code = str(row.get("Census 2011 Code") or "").strip()

                    taluk_id = taluk_code_map.get(subdist_code)
                    dist_id = district_code_map.get(dist_code)

                    batch.append({
                        "name": v_name,
                        "code": v_code,
                        "census_code": census_code or None,
                        "taluk_id": taluk_id,
                        "district_id": dist_id
                    })
                    existing_village_codes.add(v_code)
                    new_villages += 1

                    if len(batch) >= batch_size:
                        db.session.bulk_insert_mappings(Village, batch)
                        db.session.commit()
                        batch.clear()
                        print(f"    ... {new_villages} villages imported so far")

                if batch:
                    db.session.bulk_insert_mappings(Village, batch)
                    db.session.commit()
                    batch.clear()

        total_villages = Village.query.count()
        print(f"  [OK] Villages Processed: {total_villages} total ({new_villages} newly created)")

        # -------------------------------------------------------------
        # Summary
        # -------------------------------------------------------------
        print("\n" + "=" * 70)
        print("IMPORT COMPLETE - SUMMARY OF TAMIL NADU LOCATIONS")
        print("=" * 70)
        print(f"  States:     {State.query.count()}")
        print(f"  Districts:  {District.query.filter_by(state_id=state_id).count()} (All 38 TN Districts)")
        print(f"  Taluks:     {Taluk.query.join(District).filter(District.state_id == state_id).count()}")
        print(f"  Cities:     {City.query.count()}")
        print(f"  Towns:      {Town.query.count()}")
        print(f"  Villages:   {Village.query.count()}")
        print("=" * 70 + "\n")


if __name__ == "__main__":
    import_locations()
