import os
import time


def download_wait(directory, timeout) -> None:
    """
    https://stackoverflow.com/questions/34338897/python-selenium-find-out-when-a-download-has-completed
    Wait for downloads to finish with a specified timeout.

    Args
    ----
    directory : str
        The path to the folder where the files will be downloaded.
    timeout : int
        How many seconds to wait until timing out.

    """
    seconds = 0
    dl_wait = True
    while dl_wait and seconds < timeout:
        time.sleep(1)
        dl_wait = False
        files = os.listdir(directory)

        for fname in files:
            if fname.endswith(".crdownload"):
                dl_wait = True

        seconds += 1
