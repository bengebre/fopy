# Fopy

Fopy is a quick and dirty wrapper allowing you to call Bill Gray's [Find_Orb](https://www.projectpluto.com/find_orb.htm) from Python.  It's probably best thought of as a shellscript for *nix systems at this point.

## Setting up Find_Orb (required)

1. Build Find_Orb from source from these instructions: https://projectpluto.com/find_sou.htm
2. Make sure the *fo* binary is somewhere in your PATH environment variable (e.g. in ~/bin)
3. Ensure you have a ~/.find_orb directory populated with files from the above build
4. In your ~/.find_orb directory, create a new directory called *jsons* ('mkdir jsons')
5. Edit the file ~/.find_orb/environ.dat and add the following text to the bottom of the file:
    * JSON_ELEMENTS_NAME=~/.find_orb/jsons/%p.json

## Installation

```pip install git+https://github.com/bengebre/fopy```

## Usage
```python
from fopy import Fopy

#specify the directory for file writing and reset the internal counter to zero
fp = Fopy('./OD',reset=True)

#OD solve
mpc_file = fp.write(radecs,times,obs_ids)   #radecs: Nx2 array degrees, times: Nx1 UTC Jdates, obs_ids: Nx1 MPC observatory code list
json_file = fp.solve(mpc_file)              #solve the file written in the line above
data = fp.load_json(json_file)              #load the json from the solve
```
