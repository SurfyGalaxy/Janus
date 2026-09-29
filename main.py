import logging
import json
import os
import subprocess
import sys
import time
import threading

def make_file_logger(name, filename, level, fmt=None, datefmt=None):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False  # keep it isolated from other loggers
    handler = logging.FileHandler(filename, mode="w")
    if fmt:
        handler.setFormatter(logging.Formatter(fmt, datefmt=datefmt))
    logger.addHandler(handler)
    return logger

def pump(name, proc):
    try:
        for line in proc.stdout:
            secondary.info(f"{name}: {line.rstrip()}")
    except Exception as e:
        primary.error(f"{name}: pump thread died: {e}")

def start_process(program, index):
    primary.info(f"{program['Name']}: Using {program['Python']} on {program['Entry']}")

    process = subprocess.Popen(
        [program["Python"], "-u", program["Entry"]],
        cwd=folder,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    primary.info(f"{program['Name']}: Started, PID {process.pid}")

    threading.Thread(target=pump, args=(program["Name"], process), daemon=True).start()

    plist.append({"Name": program["Name"], "Program": process, "Index": index})

primary = make_file_logger(
    "primary",
    ".log",
    logging.INFO,
    fmt="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

secondary = make_file_logger("secondary", "processes.log", logging.INFO)

try:
    with open("programs.json") as f:
        data = json.load(f)
except Exception as e:
    if FileNotFoundError:
        primary.critical("Missing programs.json")
    elif json.JSONDecodeError:
        primary.critical("Malformed JSON")
    else:
        primary.critical(f"Exception: {e}")
    sys.exit(1)


primary.info(f"Loaded {len(data)} programs")

plist = []
for index, program in enumerate(data):
    primary.info(f"Loading program '{program["Name"]}'")
    folder = program["URL"].split("/")[4].split(".")[0]
    if os.path.isdir(folder):
        primary.info(f"{program["Name"]}: Pulling from {folder}")
        result = subprocess.run(
            ["git", "pull"],
            cwd=folder,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            primary.info(f"{program["Name"]}: {result.stdout.strip()}")
        else:
            primary.error(f"{program["Name"]}: {result.stderr.strip()}")
    else:
        primary.info(f"{program["Name"]}: Cloning from {program["URL"]}")
        result = subprocess.run(
            ["git", "clone", program["URL"]],
            capture_output=True
        )
        if result.returncode == 0:
            primary.info(f"{program["Name"]}: Successfully cloned from {program["URL"]}")
        else:
            primary.error(f"{program["Name"]}: {result.stderr.strip()}")
    
    if program["Run"]:
        if result.returncode != 0 and not os.path.isdir(folder):
            primary.error(f"{program['Name']}: Unable to fall back, no directory {folder}")
            continue
        elif result.returncode != 0:
            primary.warning(f"{program['Name']}: Fell back to previous version")
        
        start_process(program, index)



primary.info(f"Completed loading programs")

while True:
    for index, program in enumerate(plist):
        if program["Program"].poll() is not None:
            primary.info(f"Watcher: Program {program["Name"]} Dead, respawning")
            start_process(data[program["Index"]], program["Index"])
            del plist[index]
    time.sleep(0.1)