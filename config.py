import sys

# --- CONSTANTS ---

VAMPIRE_CACHE_FILE = "vampires_cache.json"
CREDS_FILE = "credentials.json"

# --- ENVIRONMENTS ---

ENVIRONMENTS = {
    "dev": {
        "sheet_name": "vampiros_mtg_dev",
        "worksheet_name": "master"
    },
    "pro": {
        "sheet_name": "vampiros_mtg_prod",
        "worksheet_name": "master"
    }
}

def get_app_config():
    """
    Parses command-line arguments to determine the environment and returns
    the corresponding configuration dictionary and environment name.
    Exits the script if the environment is invalid.
    """
    try:
        env_arg = sys.argv[1].lower()
        config = ENVIRONMENTS[env_arg]
        return config, env_arg
    except (IndexError, KeyError):
        print("Error: You must specify a valid environment.")
        print(f"Usage: python {sys.argv[0]} [dev|pro]")
        sys.exit(1)