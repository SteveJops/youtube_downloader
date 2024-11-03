import re
import subprocess

from multiprocessing import Process, Queue
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

from undetected_chromedriver import Chrome
from typing import List
from selenium.common.exceptions import (
    NoSuchElementException,
    NoSuchWindowException,
    ElementNotInteractableException,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from download_status_checker import download_wait


def getting_ids(command: str) -> List[str]:
    """https://github.com/nlitsme/youtube_tool tool for getting video names in playlist"""
    # command_run = subprocess.run(
    #     command, stdout=subprocess.PIPE
    # )
    command_run = subprocess.getoutput(
        command
    )  # get playlist list of video names by using yttool
    return re.findall(r".+-", command_run)  # by using regex getting video ids


def runnin_selenium(url_source: str) -> None:
    """func for automatize handle of the saving site
    url_source: str - id of the video
    """
    # service = Service(executable_path="chromedriver_mac64.zip")
    settings = webdriver.ChromeOptions()
    settings.add_argument("start-maximized")
    # settings.add_argument("--headless")
    # driver = webdriver.Chrome(settings)
    driver = Chrome(settings)
    driver.get(f"https://www.ssyoutube.com/watch?v={url_source}")
    current_window = (
        driver.current_window_handle
    )  # fixating the current tab in browser due to ads tab
    waiting = WebDriverWait(
        driver=driver,
        timeout=10,
        ignored_exceptions=[NoSuchElementException, ElementNotInteractableException],
    )
    try:
        driver.implicitly_wait(10)
        button = driver.find_element(
            By.XPATH,
            # "/html/body/div[2]/div[1]/div[2]/div[4]/div/div[1]/div[2]/div[2]/div[1]/a",
            '//*[@id="sf_result"]/div/div[1]/div[2]/div[2]/div[1]/a',
        )  # download button
        waiting.until(lambda d: button.is_displayed())
    except Exception as er:
        print(er)
        ActionChains(driver).key_down(Keys.COMMAND).send_keys("s").key_up(
            Keys.COMMAND
        ).send_keys(Keys.ENTER).perform()
    else:
        button.click()
        if driver.window_handles != 0:
            driver.switch_to.window(current_window)  # get the crucial first tab
        driver.implicitly_wait(2)
        download_wait(directory="/Users/stevejops7/Downloads", timeout=10)
    finally:
        driver.quit()


if __name__ == "__main__":

    q: Queue = Queue()
    count = 0
    for url in getting_ids(
        "yttool --playlist https://www.youtube.com/playlist?list=PLng18F_203mIDL8riq2kmEdkJT0ZngrGt"
    ):  # paste ref to playlist
        """If downloading the playlist was interrupted(no matter why) you can go on it
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
                with open("errors_log.txt", "w") as f:
                    f.write(str(err))
                continue
            except:
                continue
        count += 1
        if count % 2 == 0:  # dividing the entire queue of videos
            # on by no more then 2 in one call to create 2 processes
            # (it`s more optimal case due to always interrupting, need more just increase also need to increase time)
            p.join()  # wait until to be done
