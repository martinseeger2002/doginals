import json
import random

# Load the existing JSON file
with open("airDropList.json", "r") as json_file:
    airdrop_data = json.load(json_file)

# Shuffle the list of entries
random.shuffle(airdrop_data["airDropList"])

# Save the shuffled list back to the JSON file
with open("airDropList_shuffled.json", "w") as json_file:
    json.dump(airdrop_data, json_file, indent=4)

print("JSON entries have been randomly reordered and saved to airDropList_shuffled.json.")
