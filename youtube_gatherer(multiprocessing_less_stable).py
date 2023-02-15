"""This version is less stable,
   it runs two or more windows regard to how many processes you use
   you can adjust quantity of processes but don`t forget to increase a time for waiting
   otherwise it will be crashing more often"""


import subprocess
import re
import time

from selenium.webdriver.chrome.service import Service

from multiprocessing import Process, Queue
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (NoSuchElementException,
                                        NoSuchWindowException)
from selenium import webdriver
from typing import List


def getting_ids(command: str) -> List[str]:
    """https://github.com/nlitsme/youtube_tool tool for getting video names in playlist"""
    command_run = subprocess.run(command, stdout=subprocess.PIPE)  # get playlist list of video names by using yttool
    res = ((command_run.stdout).decode('utf-8'))  # after getting list we get names in bycode str so decoding it
    return re.findall(".+\s-", res)  # by using regex getting video ids


def runnin_selenium(url_source: str) -> None:
    """func for automatize handle of the saving site
    url_source: str - id of the video
    """
    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=service)
    driver.get(f'https://www.ssyoutube.com/watch?v={url_source}')
    current_window = driver.current_window_handle # fixating the current tab in brows due to ads tab
    time.sleep(10)
    button = driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div[2]/div[4]/div/div[1]/div[2]/div[2]/div[1]/a') # download button
    button.click()
    time.sleep(2)
    if driver.window_handles != 0:
        driver.switch_to.window(current_window)  # get to the crusial first tab
        time.sleep(35)  # time til the next iteration with the next video
    driver.quit()


if __name__ == "__main__":
    q = Queue()
    count = 0
    for url in getting_ids('yttool --playlist https://www.youtube.com/playlist?list=PLA0M1Bcd0w8y_QeedN81EZ-GP_WZpBRrh'):  # paste ref to playlist
        """ If downloading the playlist was interrupted(no matter why) you can go on it
            from that video on which it was interrupted by making a slice since that number
            of video to the end in order"""
        url_pass: str = url.split()[0].strip()
        # assert url_pass, "not true"
        # assert type(url_pass) == str(), "not str"
        q.put(url_pass)
    
    while not q.empty():
        p = Process(target=runnin_selenium, args=(q.get(),))  # create a process
        try:
            p.start()
        except NoSuchElementException:
            p.start()
        except NoSuchWindowException:
            p.start()
        except Exception as err:
            try:
                with open("errors_log.txt", 'w') as f:
                    f.write(str(err))
            except:
                continue
        count += 1
        if count % 4 == 0:  # dividing the entire queue of videos
            # on by no more then 2 in one call to create 2 processes
            # (it`s more optimal case due to always interrupting, need more just increase also need to increase time)
            p.join() # wait until to be done


    