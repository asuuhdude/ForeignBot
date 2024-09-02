import os
import yaml

from dotenv import load_dotenv
load_dotenv()

with open("./config.yaml", "r", encoding="utf8") as file:
    config = yaml.safe_load(file)


BOT_TOKEN = os.environ["TOKEN"]
VERSION = config["core"].get("version")
OWNER_IDS = os.environ["OWNER_IDS"]
CONTRIBUTOR_IDS = os.environ["CONTRIBUTOR_IDS"] or "[0]"