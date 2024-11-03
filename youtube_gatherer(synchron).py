"""This version regardless synchronic running is more stable,
   and you can run it and not to minimize it,
   just switch to another window,
   remain the window with downloading open and do your businesses"""


# ToDo: enhance to use command prompt for running the script

import subprocess
import re
import time

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, NoSuchWindowException
from selenium import webdriver
from typing import List


def getting_ids(command: str) -> List[str]:
    """https://github.com/nlitsme/youtube_tool tool for getting video names in playlist"""
    command_run = subprocess.run(
        command, stdout=subprocess.PIPE
    )  # get playlist list of video names by using yttool
    res = (command_run.stdout).decode(
        "utf-8"
    )  # after getting list we get names in bycode str so decoding it
    return re.findall(".+\s-", res)  # by using regex getting video ids


def runnin_selenium(
    driver: webdriver.Chrome, url_source: str, time_: int, current_window: str
) -> None:
    """func for automatize handle of the saving site
    driver: webdriver.Chrome - instance
    url_source: str - id of the video
    time_: int - time til closing the tab
    current_window: str - driver instance method for changing the tab
    """

    driver.get(f"https://www.ssyoutube.com/watch?v={url_source}")
    time.sleep(10)
    button = driver.find_element(
        By.XPATH,
        "/html/body/div[2]/div[1]/div[2]/div[4]/div/div[1]/div[2]/div[2]/div[1]/a",
    )  # download button
    button.click()
    time.sleep(2)
    if driver.window_handles != 0:
        driver.switch_to.window(current_window)  # get to the crusial first tab
        time.sleep(time_)  # time til the next iteration with the next video


if __name__ == "__main__":
    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=service)
    current_window = (
        driver.current_window_handle
    )  # fixating the current tab in brows due to ads tab

    for url in getting_ids(
        "yttool --playlist https://www.youtube.com/playlist?list=PLA0M1Bcd0w8yU5h2vwZ4LO7h1xt8COUXl"
    ):  # paste ref to playlist
        """If downloading the playlist was interrupted(no matter why) you can go on it
        from that video on which it was interrupted by making a slice since that number
        of video to the end in order"""
        url_pass: str = url.split()[0].strip()
        # assert url_pass, "not true"
        # assert type(url_pass) == str(), "not str"
        try:
            runnin_selenium(driver, url_pass, 8, current_window)
        except NoSuchElementException:
            runnin_selenium(driver, url_pass, 15, current_window)
        except NoSuchWindowException:
            driver.switch_to.window(current_window)
        except Exception as err:
            try:
                with open("errors_log.txt", "w") as f:
                    f.write(str(err))
                continue
            except:
                ...

    driver.quit()
