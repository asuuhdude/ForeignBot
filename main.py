import sys

from pathlib import Path
if not Path("./.env").exists():

    from toml import load

    with open("./config.toml", "r", encoding="utf8") as file:
        config = load(file)

    if config["core"].get("automaticENVCreation"):
        print("no .env file found, creating one...")
        
        with open("./.env", "w", encoding="utf8") as file:
            file.write("TOKEN=replace_me!\nOWNER_IDS=[]")
            file.close()

        print("done! please modify the .env file and restart the program")
    else:
        print("no .env file found, please create one and restart the program")

    sys.exit(1)


from fbot import ForeignBot

if __name__ == "__main__":
    ForeignBot().run()