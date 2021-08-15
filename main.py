#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import subprocess
import traceback

import PySimpleGUI as sg
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class GUI_Controller(object):
    def __init__(self, theme_name:str ="LightBlue5", proxy_url: str=None) -> None:
        self._license_info = None
        self._theme_name = theme_name
        self._proxy_url = proxy_url

    def _get_licenses(self):
        """
        Get pip module's license infomation
        """

        if self._license_info is None:
            json_licenses = json.loads(
                subprocess.check_output(
                    "pip-licenses --with-license-file --no-license-path --format=json"
                )
            )

            double_break = chr(10) * 2
            self._license_info = double_break.join([
                text["Name"] + " (" + text["Version"] + ")" + chr(10) + text["LicenseText"] for text in json_licenses
            ])

    def open(self):
        """
        open GUI
        """

        # init paramaters
        default_path = os.environ["USERPROFILE"] + r"\Desktop\result.png"
        sg.theme(self._theme_name)
        
        # declare menu-bar
        menu_def = [    
            [
                "Docs", 
                [
                    "Open selenium-python docs (Original)", 
                    "Open selenium-python docs (Japanese translated 1)",
                    "Open selenium-python docs (Japanese translated 2)",
                    "Open PySimpleGUI docs (Original)", 
                    "Open PySimpleGUI docs (Japanese translated)", 
                    "Open nuitka docs",
                ]
            ],     
            [
                "About", 
                [
                    "Show licenses", 
                ]
            ],
        ]
        
        # declare GUI layout
        layout = [
            [sg.Menu(menu_def, )],
            [sg.Text('Search word in Rakuten')],
            [sg.InputText(default_text="selenium python", size=(43, 20), key="search_word")],
            [sg.Text('Save screenshot in this path')],
            [sg.InputText(default_text=default_path, size=(43, 20), key="screenshot_path")],
            [sg.Button("Run", key="Run"), sg.Cancel()],
            [sg.HorizontalSeparator()],
            [sg.ProgressBar(6, orientation="h", size=(30, 20), key="progress_bar")],
        ]

        # Create the Window
        window_title = "Selenium with Nuitka GUI App PoC"
        window = sg.Window(window_title, layout)
        
        # declare event-loop
        while True:             
            event, values = window.read()

            if event in (sg.WIN_CLOSED, 'Cancel'):
                break

            if event == "Show licenses":
                self._get_licenses()
                sg.popup_scrolled(
                    self._license_info, 
                    title="Licenses", 
                    keep_on_top=True,
                    size=(80, 20),
                )
                
            if event == "Run":
                search_word = values["search_word"]
                file_path = values["screenshot_path"]

                try:
                    [window["progress_bar"].update(i) for i in self.screenshot_rakuten(search_word, file_path)]

                    sg.popup_ok("スクリーンショットを保存しました", title=window_title)
                    window["progress_bar"].update(0)
                
                except Exception as e:
                    sg.popup_ok(traceback.format_exception_only(type(e), e), title="ERROR")

            if event == "Open selenium-python documents (Original)":
                os.system("start https://selenium-python.readthedocs.io/")

            if event == "Open selenium-python docs (Japanese translated 1)":
                os.system("start https://www.seleniumqref.com/api/webdriver_abc_python.html")

            if event == "Open selenium-python docs (Japanese translated 2)":
                os.system("start https://selenium-python.readthedocs.io/")
            
            if event == "Open PySimpleGUI documents (Original)":
                os.system("start https://pysimplegui.readthedocs.io/en/latest/call%20reference/")

            if event == "Open PySimpleGUI documents (Japanese translated)":
                os.system("start http://www.k-techlabo.org/www_python/PySimpleGUI.pdf")

            if event == "Open nuitka documents":
                os.system("start https://nuitka.net/pages/documentation.html")

        window.close()

    def screenshot_rakuten(self, search_word: str, screenshot_file: str, is_headless: bool=True) -> int:
        yield 0
        startup_url = "https://www.rakuten.co.jp/"

        options = webdriver.ChromeOptions()
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-desktop-notifications")
        options.add_argument("--disable-print-preview")
        options.add_argument("--log-level=3")
        options.add_argument("--incognito")
        #options.add_experimental_option("excludeSwitches", ["enable-logging"])

        if is_headless:
            options.add_argument('--headless')

        if not self._proxy_url is None:
            options.add_argument("--proxy-server=http://%s" % self._proxy_url)
            os.environ["http_proxy"] = "http://%s" % self._proxy_url
            os.environ["https_proxy"] = "http://%s" % self._proxy_url
        
        screen_width = 1000
        screen_height = 2000

        #os.environ["WDM_LOG_LEVEL"] = "0"
        #os.environ["WDM_PRINT_FIRST_LINE"] = "False"

        driver_manager = ChromeDriverManager(cache_valid_range=7).install()
        yield 1

        driver = webdriver.Chrome(driver_manager, options=options)
        yield 2

        driver.set_window_size(screen_width, screen_height)
        driver.get(startup_url)
        yield 3

        try:
            search_bar = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, "common-header-search-input"))
            )
            search_bar.send_keys(search_word)
            search_bar.submit()
            yield 4

            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, "ri-cmn-hdr-sitem"))
            )
            yield 5

            driver.save_screenshot(screenshot_file)

        finally:
            driver.quit()
            yield 6

if __name__ == "__main__":
    gc = GUI_Controller()
    gc.open()