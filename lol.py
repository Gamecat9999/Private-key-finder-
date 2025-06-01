import os
import time
from web3 import Web3

# Define multiple networks to check
NETWORKS = [
    {"name": "Ethereum Mainnet", "rpc_url": "https://mainnet.infura.io/v3/f5250249edfa45239463cc08334180ce"},
    {"name": "Binance Smart Chain", "rpc_url": "https://bsc-dataseed.binance.org/"},
    {"name": "Polygon", "rpc_url": "https://polygon-rpc.com/"}
]

# Validate Ethereum address
def validate_eth_address(wallet_address):
    return Web3.is_address(wallet_address)

# Update the get_balance_on_network function to handle rate limits
RATE_LIMIT_DELAY = 0.01  # 10ms delay

def get_balance_on_network(wallet_address, rpc_url):
    try:
        web3 = Web3(Web3.HTTPProvider(rpc_url))
        if not web3.is_connected():
            return None
        balance = web3.eth.get_balance(wallet_address)
        return web3.from_wei(balance, 'ether')
    except Exception as e:
        error_message = str(e)
        if "rate limit" in error_message.lower() or "call rate limit exhausted" in error_message.lower():
            print(f"Rate limit hit for {rpc_url}. Applying delay...")
            time.sleep(RATE_LIMIT_DELAY)
            return get_balance_on_network(wallet_address, rpc_url)
        print(f"Error checking balance on network {rpc_url}: {e}")
        return None

# Update the save_to_file function to include currency names based on the network
def save_to_file(filename, data, network_name):
    currency = "ETH"  # Default currency
    if "Binance Smart Chain" in network_name:
        currency = "BNB"
    elif "Polygon" in network_name:
        currency = "POLY"

    with open(filename, "a") as file:
        file.write(f"{data}, Currency: {currency}\n")

# Update the save_to_file function to also track the richest account per network
def update_richest_account(network_name, wallet_address, balance, private_key):
    richest_file = "richest_accounts.txt"
    try:
        # Read existing data
        richest_data = {}
        if os.path.exists(richest_file):
            with open(richest_file, "r") as file:
                for line in file:
                    parts = line.strip().split(",")
                    if len(parts) == 4:
                        net, addr, bal, key = parts
                        richest_data[net] = (addr, float(bal), key)

        # Update the richest account for the network
        if network_name not in richest_data or balance > richest_data[network_name][1]:
            richest_data[network_name] = (wallet_address, balance, private_key)

        # Write updated data back to the file
        with open(richest_file, "w") as file:
            for net, (addr, bal, key) in richest_data.items():
                file.write(f"{net},{addr},{bal},{key}\n")

    except Exception as e:
        print(f"Error updating richest account: {e}")

# Adjust the get_last_private_key function to handle the new format in funded_wallets.txt
FUNDED_WALLET_FILE = "funded_wallets.txt"
HIGH_BALANCE_FILE = "high_balance_wallets.txt"

def get_last_private_key(filename):
    try:
        if os.path.exists(filename):
            with open(filename, "r") as file:
                lines = file.readlines()
                if lines:
                    for line in reversed(lines):
                        if "Private Key:" in line:
                            private_key_part = line.split("Private Key:")[-1].split(",")[0].strip()
                            return int(private_key_part, 16)
        print("Starting from the lowest private key...")
        return 1  # Default to the lowest private key if no file or key exists
    except Exception as e:
        print(f"Error reading last private key: {e}")
        return 1

# Add checkpoint file and logic
CHECKPOINT_FILE = "checkpoint.txt"

def save_checkpoint(private_key):
    """Save the current private key to the checkpoint file."""
    try:
        with open(CHECKPOINT_FILE, "w") as file:
            file.write(f"Private Key: {private_key}\n")
    except Exception as e:
        print(f"Error saving checkpoint: {e}")

def get_last_checkpoint():
    """Retrieve the last private key from the checkpoint file."""
    try:
        if os.path.exists(CHECKPOINT_FILE):
            with open(CHECKPOINT_FILE, "r") as file:
                line = file.readline().strip()
                if "Private Key:" in line:
                    private_key_part = line.split("Private Key: ")[-1].strip()
                    return int(private_key_part, 16)
        return 1  # Default to the lowest private key if no checkpoint exists
    except Exception as e:
        print(f"Error reading checkpoint: {e}")
        return 1

def get_starting_private_key():
    """Determine the starting private key based on funded wallets or checkpoint."""
    funded_last_key = get_last_private_key(FUNDED_WALLET_FILE)
    checkpoint_last_key = get_last_checkpoint()
    return max(funded_last_key, checkpoint_last_key)

# Update the search_wallets function to call update_richest_account
def search_wallets(target_address=None):
    print("Starting wallet search...")
    starting_private_key = get_starting_private_key()
    print(f"Resuming search from private key: {hex(starting_private_key)[2:].zfill(64)}")

    private_key_int = starting_private_key
    checkpoint_counter = 0
    last_checkpoint_time = time.time()

    while True:
        try:
            private_key = hex(private_key_int)[2:].zfill(64)
            account = Web3().eth.account.from_key(private_key)
            wallet_address = account.address

            if not validate_eth_address(wallet_address):
                private_key_int += 1
                continue

            print(f"Checking wallet: {wallet_address}")

            for network in NETWORKS:
                balance = get_balance_on_network(wallet_address, network["rpc_url"])
                if balance and balance > 0:
                    print(f"🎉 Found funded wallet on {network['name']}!")
                    print(f"Address: {wallet_address}")
                    print(f"Balance: {balance} ETH")
                    print(f"Private Key: {private_key}")
                    save_to_file(FUNDED_WALLET_FILE, f"{network['name']} - Address: {wallet_address}, Balance: {balance}, Private Key: {private_key}", network['name'])

                    # Save to high-balance file if balance exceeds 0.0001
                    if balance > 0.0001:
                        save_to_file(HIGH_BALANCE_FILE, f"{network['name']} - Address: {wallet_address}, Balance: {balance}, Private Key: {private_key}", network['name'])
                    update_richest_account(network["name"], wallet_address, balance, private_key)

            if target_address and wallet_address.lower() == target_address.lower():
                print(f"🎯 Found target address: {wallet_address}")
                save_to_file("target_address_found.txt", f"Target Address: {wallet_address}, Private Key: {private_key}", "Target")
                return

            checkpoint_counter += 1
            if checkpoint_counter >= 10 or (time.time() - last_checkpoint_time) >= 60:
                save_checkpoint(private_key)
                checkpoint_counter = 0
                last_checkpoint_time = time.time()

            private_key_int += 1

        except KeyboardInterrupt:
            print("Search interrupted by user.")
            break
        except Exception as e:
            print(f"Error during search: {e}")
            private_key_int += 1
            continue

if __name__ == "__main__":
    target = input("Enter the target address (or press Enter to skip): ").strip()
    target = target if target else None
    search_wallets(target_address=target)