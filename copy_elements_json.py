import requests
import os

# URL of the gist's raw JSON
url = "https://gist.githubusercontent.com/GoodmanSciences/c2dd862cd38f21b0ad36b8f96b4bf1ee/raw"

# Local destination path (relative to your current working directory)
destination_dir = "static/data"
destination_path = os.path.join(destination_dir, "elements.json")

# Ensure the directory exists
os.makedirs(destination_dir, exist_ok=True)

# Download the file
response = requests.get(url)
response.raise_for_status()

with open(destination_path, "w", encoding="utf-8") as f:
    f.write(response.text)

print(f"elements.json successfully saved to {destination_path}")
