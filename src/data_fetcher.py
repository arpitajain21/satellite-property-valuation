import os
import requests
import pandas as pd

# ==============================
# Configuration
# ==============================

IMAGE_SIZE = 256          # 256x256 pixels
ZOOM_LEVEL = 17           # neighborhood-level zoom
MAP_STYLE = "satellite-v9"

TRAIN_CSV = "data/raw/train.csv"
TEST_CSV = "data/raw/test.csv"

TRAIN_IMG_DIR = "data/images/train"
TEST_IMG_DIR = "data/images/test"

# ==============================
# API Key
# ==============================

MAPBOX_API_KEY = os.getenv("MAPBOX_API_KEY")

if MAPBOX_API_KEY is None:
    raise ValueError(
        "MAPBOX_API_KEY not found. "
        "Set it using: $env:MAPBOX_API_KEY='your_token_here'"
    )

# ==============================
# Helper functions
# ==============================

def build_mapbox_url(lat, lon):
    """
    Build Mapbox Static Image API URL for given coordinates.
    """
    base_url = "https://api.mapbox.com/styles/v1/mapbox"
    return (
        f"{base_url}/{MAP_STYLE}/static/"
        f"{lon},{lat},{ZOOM_LEVEL}/"
        f"{IMAGE_SIZE}x{IMAGE_SIZE}"
        f"?access_token={MAPBOX_API_KEY}"
    )


def download_image(url, save_path):
    response = requests.get(url, timeout=10)

    if response.status_code == 200:
        with open(save_path, "wb") as f:
            f.write(response.content)
    else:
        print(f"Failed ({response.status_code}) → {save_path}")


def fetch_images(csv_path, image_dir):
    df = pd.read_csv(csv_path)
    os.makedirs(image_dir, exist_ok=True)

    print(f"\nFetching images for: {csv_path}")
    print(f"Total rows: {len(df)}")

    for idx, row in df.iterrows():
        house_id = row["id"]
        lat = row["lat"]
        lon = row["long"]

        # ✅ composite filename: id + row index
        image_name = f"{house_id}_{idx}.png"
        image_path = os.path.join(image_dir, image_name)

        # Skip if already downloaded
        if os.path.exists(image_path):
            continue

        try:
            url = build_mapbox_url(lat, lon)
            download_image(url, image_path)
        except Exception as e:
            print(f"Error for {image_name}: {e}")

    print(f"Completed: {image_dir}")

# ==============================
# Run for train & test
# ==============================

if __name__ == "__main__":
    fetch_images(TRAIN_CSV, TRAIN_IMG_DIR)
    fetch_images(TEST_CSV, TEST_IMG_DIR)
