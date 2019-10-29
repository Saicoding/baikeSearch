from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import json  # 引入模块
import os
import time
from getBaike import Baike

data = open("./data.json", encoding='utf-8')

strJson = json.load(data)

num = strJson['num']

profile_dir=r"C:\Users\41735\AppData\Local\Google\Chrome\User Data" # 对应你的chrome的用户数据存放路径  
chrome_options=webdriver.ChromeOptions()
# 使用headless无界面浏览器模式
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')

chrome_options.add_argument("user-data-dir="+os.path.abspath(profile_dir))

# 启动浏览器，获取网页源代码
driver = webdriver.Chrome(options=chrome_options)

driver.maximize_window()

baike = Baike(driver, num)

baike.search()
