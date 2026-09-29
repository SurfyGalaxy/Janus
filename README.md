# Janus
<!-- why are you reading the raw? it's not a .txt -->

A way to allow python projects to remain updated and start them automatically

## Usage
1. `git clone htpps://github.com/SurfyGalaxy/Janus`
2. Setup `programs.json` in the same folder level as main.py
3. Enroll Janus in your boot sequence (e.g systemd)

## programs.json

programs.json is an array of dictionaries, with the fields as follows:

### Name [str]
Name is a user accesible string to be used as a reference to the program

### URL [str]
The git URL of the repository to pull from

### Python [str]
The python interperator to use for this program

### Entry [str]
The file to start the program from

### Run [bool]
Wether to run the file after updating

## Structure

Janus will place every installed program in its own directory and will run from it

## AI disclosure

No AI was used in this project