import requests
from bs4 import BeautifulSoup

img_dict = {}

def get_images(url):
    response = requests.get(url)
    if response.status_code == 200:
    # Parse the HTML content of the webpage
        soup = BeautifulSoup(response.content, 'html.parser')

    # Find all image elements (assuming images have 'img' tag and specific class or attributes)
        images = soup.find_all('img')  # You may need to refine this to target specific images

    # Initialize an empty dictionary to store the image data
        icon_images = {}

    # Iterate over each image element found
        for img in images:
        # Extract the image URL and name
            img_url = img.get('src')
            img_name = img.get('alt') or img.get('title') or 'Unnamed'  # Use alt text or title as the name

        # Ensure URL is complete
            if not img_url.startswith('http'):
                img_url = url + img_url

        # Add the image URL and name to the dictionary
            icon_images[img_name] = img_url
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
    return icon_images


tabs = ["", "brawlers","maps", "gamemodes", "stats/profile/RV0PCU8PR"]
for tab in tabs:
    url = f"https://brawlify.com/{tab}"
    img_dict[f'{tab}'] = get_images(url)

import json
with open('brawl_star_img.json', 'w') as file:
    file.write(json.dumps(img_dict))