"""Script to download Dryad dataset that accompanied Plos Comp Biology paper.

Mets, David G.; Brainard, Michael S. (2019),
Data from: An automated approach to the quantitation of vocalizations and vocal learning in the songbird.,
Dryad, Dataset, https://doi.org/10.5061/dryad.8tn4660
"""
import pathlib
import shutil
import sys
import time
import urllib.request


def reporthook(count, block_size, total_size):
    """hook for urlretrieve that gives us a simple progress report
    https://blog.shichao.io/2012/10/04/progress_speed_indicator_for_urlretrieve_in_python.html
    """
    global start_time
    if count == 0:
        start_time = time.time()
        return
    duration = time.time() - start_time
    progress_size = int(count * block_size)
    speed = int(progress_size / (1024 * duration))
    percent = int(count * block_size * 100 / total_size)
    sys.stdout.write("\r...%d%%, %d MB, %d KB/s, %d seconds passed" %
                     (percent, progress_size / (1024 * 1024), speed, duration))
    sys.stdout.flush()


PCB_DATA_URL = "https://datadryad.org/stash/downloads/file_stream/14140"
PCB_DATA_TAR_PATH = pathlib.Path("./data/pcb_data.tar.gz")
PCB_DATA_PATH = pathlib.Path("./data/")  # will unpack 'pcb_data' into ./data


urllib.request.urlretrieve(PCB_DATA_URL,
                           PCB_DATA_TAR_PATH,
                           reporthook)

shutil.unpack_archive(PCB_DATA_TAR_PATH, PCB_DATA_PATH)
