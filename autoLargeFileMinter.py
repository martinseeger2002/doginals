import subprocess
import time
import json
import re
import os
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

rpc_user = os.getenv('RPC_USER', 'your_rpc_user')
rpc_password = os.getenv('RPC_PASSWORD', 'your_rpc_password')
rpc_host = os.getenv('RPC_HOST', '192.168.68.84')
rpc_port = os.getenv('RPC_PORT', '22555')

rpc_connection = AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@{rpc_host}:{rpc_port}/")

def read_last_output(json_file_name):
    if os.path.exists(json_file_name):
        try:
            with open(json_file_name, 'r') as file:
                data = json.load(file)
                return len(data)
        except json.JSONDecodeError as e:
            print(f"JSON decode error in {json_file_name}: {e}")
    return 0

def extract_details(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            details = json.load(file).get('airDropList', [])
            print(f"Extracted {len(details)} details from {file_name}")
            return details
    except Exception as e:
        print(f"An error occurred while reading {file_name}: {e}")
        return []

def update_json_file(image_path, txid, details):
    json_file_name = "airDropOutput.json"
    try:
        data = {}
        if os.path.exists(json_file_name):
            with open(json_file_name, 'r') as file:
                data = json.load(file)
        key = os.path.basename(image_path)
        data[key] = {"txid": txid, "address": details['dogecoin_address']}
        with open(json_file_name, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Updated {json_file_name} with {key}: {txid}, {details['dogecoin_address']}")
    except Exception as e:
        print(f"Error updating {json_file_name}: {e}")

def process_mint(directory, file_extension, start_number, details_list):
    for i in range(start_number, len(details_list) + start_number):
        actual_index = i - start_number
        if actual_index >= len(details_list):
            print(f"Index {i} exceeds the length of details_list {len(details_list)}")
            break
        details = details_list[actual_index]
        image_path = os.path.join(directory, f"{i}.{file_extension}")
        print(f"Processing file: {image_path} for address: {details['dogecoin_address']}")
        if not os.path.exists(image_path):
            print(f"File not found: {image_path}")
            continue
        
        # Minting process
        mint_command = f"node . mint {details['dogecoin_address']} {image_path}"
        result_mint = subprocess.run(mint_command, shell=True, capture_output=True, text=True)
        print("Output from mint command:")
        print(result_mint.stdout)
        if result_mint.stderr:
            print("Error in mint command:")
            print(result_mint.stderr)
        
        # Extract TXID and update JSON
        txid_search = re.search(r"txid: (\w+)", result_mint.stdout)
        if txid_search:
            last_txid = txid_search.group(1)
            modified_txid = f"{last_txid}i0"
            print(f"Successful mint, TXID: {modified_txid}")
            update_json_file(image_path, modified_txid, details)
        else:
            print("No TXID found, skipping file update.")
            continue

        # Handle post-minting actions
        handle_post_action(last_txid)

def handle_post_action(txid_to_confirm):
    while True:
        wait_for_tx_confirmation(txid_to_confirm)
        result_sync = subprocess.run("node . wallet sync", shell=True, capture_output=True, text=True)
        print("Output from wallet sync command:")
        print(result_sync.stdout)

        txid_search = re.search(r"txid: (\w+)", result_sync.stdout)
        if txid_search:
            txid_to_confirm = txid_search.group(1)
            print(f"New TXID to confirm: {txid_to_confirm}")

        if "too long mempool reached" not in result_sync.stdout:
            break

def wait_for_tx_confirmation(txid):
    while True:
        try:
            tx_info = rpc_connection.gettransaction(txid)
            if tx_info and tx_info.get("confirmations", 0) >= 1:
                print(f"Transaction {txid} is confirmed.")
                break
        except JSONRPCException as e:
            print(f"Error fetching transaction {txid}: {e}")
        time.sleep(10)

def continuous_minting_process(directory, file_extension, start_number):
    last_count = read_last_output('airDropOutput.json')
    print(f"Starting minting process from last count: {last_count}")
    details_list = extract_details('airDropList.json')
    details_list = details_list[last_count:]
    process_mint(directory, file_extension, start_number, details_list)

# Initialize main variables and start process
directory = r'C:\hashlips\build\images'
file_extension = 'png'
start_number = 1

continuous_minting_process(directory, file_extension, start_number)
