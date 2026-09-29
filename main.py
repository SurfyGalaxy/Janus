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
except Exception as e:
    if FileNotFoundError:
        logging.critical("Missing programs.json")
    elif json.JSONDecodeError:
        logging.critical("Malformed JSON")
    else:
        logging.critical(f"Exception: {e}")
    sys.exit(1)


logging.info(f"Loaded {len(data)} programs")

programs = {}
for program in data:
    logging.info(f"Loading program '{program["Name"]}'")
    folder = program["URL"].split("/")[4].split(".")[0]
    if os.path.isdir(folder):
        logging.info(f"{program["Name"]}: Pulling from {folder}")
        result = subprocess.run(
            ["git", "pull"],
            cwd=folder,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            logging.info(f"{program["Name"]}: {result.stdout.strip()}")
        else:
            logging.error(f"{program["Name"]}: {result.stderr.strip()}")
    else:
        result = logging.info(f"{program["Name"]}: Cloning from {program["URL"]}")
        subprocess.run(
            ["git", "clone", program["URL"]],
            capture_output=True
        )
        if result.returncode == 0:
            logging.info(f"{program["Name"]}: Successfully cloned from {program["URL"]}")
        else:
            logging.error(f"{program["Name"]}: {result.stderr.strip()}")
    
    if program["Run"]:
        if result.returncode != 0 and not os.path.isdir(folder):
            logging.error(f"{program["Name"]}: Unable to fall back, no directory {folder}")
            continue
        elif result.returncode != 0:
            logging.warning(f"{program["Name"]}: Fell back to previous version")
        logging.info(f"{program["Name"]}: Using {program["Python"]} on {program["Entry"]}")
        process = subprocess.Popen([program["Python"], program["Entry"]],
        cwd=folder,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True)

        logging.info(f"{program["Name"]}: Sucessfully started program, PID {process.pid}")
        out, err = process.communicate()
        print(err)
        if err:
            logging.warning(f"{program["Name"]}: {err}")
