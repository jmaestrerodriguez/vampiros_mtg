import sys
import os
from dotenv import load_dotenv

# --- CONSTANTS ---

def get_env_config():
    """
    Parses command-line arguments to determine the environment and returns
    the corresponding configuration dictionary and environment name.
    Exits the script if the environment is invalid.
    """
    try:
        env_arg = sys.argv[1].lower()
        env_file = f".env.{env_arg}"
        # 3. Check if file exists
        if not os.path.exists(env_file):
              print(f"❌ Error: Environment config file not found: '{env_file}'")
              sys.exit(1)
        print(f"🚀 Loading environment config: {env_arg.upper()} desde {env_file}...")
        env_config = load_dotenv(dotenv_path=env_file)
        return env_config 
    except (IndexError, KeyError):
        print("Error: You must specify a valid environment.")
        print(f"Usage: python {sys.argv[0]} [dev|pro]")
        sys.exit(1)