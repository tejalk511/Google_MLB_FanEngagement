#@title Import Python Libraries
# General data science libraries
import pandas as pd
import numpy as np

# Pulling data from APIs, parsing JSON
import requests
import json

# Interfacing w/ Cloud Storage from Python
from google.cloud import storage

# Plotting
import matplotlib.pyplot as plt
import seaborn as sns

from IPython.display import HTML, Image

#@title Modify Settings

# Expand max column width when displaying data frames to handle longer text
pd.set_option('display.max_colwidth', 200)

#@title Function to Process Results from Various MLB Stats API Endpoints
def process_endpoint_url(endpoint_url, pop_key=None):
  """
  Fetches data from a URL, parses JSON, and optionally pops a key.

  Args:
    endpoint_url: The URL to fetch data from.
    pop_key: The key to pop from the JSON data (optional, defaults to None).

  Returns:
    A pandas DataFrame containing the processed data
  """
  json_result = requests.get(endpoint_url).content

  data = json.loads(json_result)

   # if pop_key is provided, pop key and normalize nested fields
  if pop_key:
    df_result = pd.json_normalize(data.pop(pop_key), sep = '_')
  # if pop_key is not provided, normalize entire json
  else:
    df_result = pd.json_normalize(data)

  return df_result

#@title All Players from 1 Season

# Pick single season to get all players for (default is 2024)
season = 2024 # @param {type:"integer"}

single_season_players_url = f'https://statsapi.mlb.com/api/v1/sports/1/players?season={season}'

players = process_endpoint_url(single_season_players_url, 'people')

display(players)

#player_ids = [players['id'].index()]]
player_info = players[['id', 'firstName','lastName']].values.tolist()  # Extract both as a list of lists

print(player_info)

import os
import requests
from IPython.display import Image, display

# Ensure directory exists
save_folder = "player_images"
os.makedirs(save_folder, exist_ok=True)

for player_id, fname, lname in player_info:
    player_current_headshot_url = f"https://securea.mlb.com/mlb/images/players/head_shot/{player_id}.jpg"
    image_name = f"{fname}_{lname}.jpg"
    image_path = os.path.join(save_folder, image_name)

    # Download the image
    response = requests.get(player_current_headshot_url, stream=True)
    
    if response.status_code == 200:
        with open(image_path, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        
        print(f"✅ Saved: {image_name}")
        display(Image(image_path))  # Show saved image
    else:
        print(f"❌ No image found for {fname} {lname} ({player_id})")
