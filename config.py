import os

# API Configuration
INFURA_API_KEY = "f5250249edfa45239463cc08334180ce"
ETHERSCAN_API_KEY = "GMVN9XPJP1QE388AWFA3GH2RX3KWNI3V8Z"

# Network Configuration
ETH_NETWORK = "mainnet"
INFURA_URL = f"https://{ETH_NETWORK}.infura.io/v3/{INFURA_API_KEY}"
ETHERSCAN_URL = "https://api.etherscan.io/api"

# Processing Configuration
BATCH_SIZE = 10  # Number of keys to check in each batch
MAX_WORKERS = 1  # Single worker for sequential processing
REQUEST_TIMEOUT = 10
MAX_RETRIES = 3

# File Configuration
DATA_DIR = "wallet_data"
ENCRYPTION_KEY_FILE = "encryption_key.txt"
RECOVERED_KEY_FILE = "recovered_key.txt"
FUNDED_WALLET_FILE = "funded_wallet.txt"

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FILE = "wallet_finder.log"

# Key Generation Configuration
MAX_PRIVATE_KEY = "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141" 