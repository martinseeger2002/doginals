import json

# Addresses
address_1 = "DCHxodkzaKCLjmnG4LP8uH6NKynmntmCNz"
address_2 = ""

# Create the airdrop list
airdrop_list = [{"dogecoin_address": address_1} for _ in range(10)] + \
               [{"dogecoin_address": address_2} for _ in range(0)]

# Create the final JSON structure
airdrop_data = {
    "airDropList": airdrop_list
}

# Save to a JSON file
with open("airDropList.json", "w") as json_file:
    json.dump(airdrop_data, json_file, indent=4)

print("JSON file created with 2500 entries.")
