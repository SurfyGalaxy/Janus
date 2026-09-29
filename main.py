import logging
import json
import os
import subprocess
import sys

logging.basicConfig(
    filename=".log",
    filemode="w",
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

try:
    with open("programs.json") as f:
        data = json.load(f)
except FileNotFoundError:
    logging.critical("Missing programs.json")

logging.info(f"Loaded {len(data)} programs")

for program in data:
    logging.info(f"Loading program '{program["Name"]}'")
    folder = program["URL"].split("/")[4].split(".")[0]
    if os.path.isdir(folder):
        result = logging.info(f"{program["Name"]}: Pulling from {folder}")
        subprocess.run(
            ["git", "pull"],
            cwd= "Loggie",
            capture_output=True
        )
        logging.info(f"{program["Name"]}: {result}")
    else:
        result = logging.info(f"{program["Name"]}: Cloning from {program["URL"]}")
        subprocess.run(
            ["git", "clone", program["URL"]],
            capture_output=True
        )