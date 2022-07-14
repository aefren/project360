import time
from cytolk import tolk
from pdb import Pdb

tolk.load()

def timer(seconds):
    tolk.output(f"Starting!",1)
    while  seconds > 0:
        tolk.output(f"{seconds}.",1)
        seconds -= 1
        time.sleep(1)


timer(60) 