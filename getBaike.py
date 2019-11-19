from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import pymysql
import time, unittest, re
import json  # 引入模块
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoAlertPresentException

class Baike:
    def __init__(self, driver, num):
        # 下面为Person对象增加2个实例变量
        self.driver = driver
        self.num = num
        self.start = True
        self.count = 0
        self.driver.set_page_load_timeout(10)

        # db指定数据库；charset指定字符集；
        self.connection = pymysql.connect(host='47.92.252.98',
                                          user='root',
                                          password='ty8399782',
                                          db='sai',
                                          charset='utf8mb4',
                                          cursorclass=pymysql.cursors.DictCursor)

    def search(self):
        while self.start:
            referUrl = ""
            refer = ""
            referDate = ""

            # 打开网页
            try:
                self.driver.get('https://baike.baidu.com/edit/1/{}'.format(self.num))
                try:
                    alert = self.driver.switch_to.alert
                    print('有弹窗')
                    alert.accept()
                except NoAlertPresentException:
                    pass
            except TimeoutException:
                print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&卡住了，在刷新1')

                continue

            # 如果没有该词条，继续下个回合
            current_url = self.driver.current_url

            try:
                if current_url.find('baike.baidu.com/error') != -1:
                    print('***************************{}'.format(self.num))
                    self.num += 1
                    continue
                else:
                    pass
            except TimeoutException:
                print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&卡住了，在刷新2')
                continue


            # 等待找到title这个dom
            if current_url.find('/editor/load/editload?') != -1:
                try:
                    WebDriverWait(self.driver, 10 , 0.5).until(
                        EC.presence_of_element_located((By.ID, 'J-lemma-desc')))
                    time.sleep(0.2)
                    name = self.driver.find_element_by_class_name("lemma-title").text
                    flag = self.driver.find_element_by_id('J-lemma-desc').get_attribute("placeholder")

                    # 设置标签信息

                    try:
                        flag.index('世界500强企业')
                        flag = '企业'
                    except Exception:
                        pass

                    try:
                        flag.index('如游戏主播')
                        flag = '人物'
                    except Exception:
                        pass

                    try:
                        flag.index('的现任职位或原职位')
                        flag = '官员'
                    except Exception:
                        pass

                except Exception:
                    print('卡住了，在刷新3')
                    continue

            else:
                try:
                    WebDriverWait(self.driver, 10, 0.5).until(EC.presence_of_element_located((By.CLASS_NAME, 'card-tip-icon')))
                    time.sleep(1)
                    name = self.driver.find_element_by_id("bke_title").text
                    # 词条类型
                    flag = self.driver.find_element_by_xpath('//*[@id="curType"]').text

                    # 参考资料名称
                    refer = self.driver.find_element_by_xpath('//*[@id="anchorTextIndex1"]/span[1]').text

                    # 参考资料地址
                    referUrl = self.driver.find_element_by_xpath('//*[@id="urlIndex1"]').text

                    # 引用日期
                    referDate = self.driver.find_element_by_xpath('//*[@id="anchorTextIndex1"]/span[2]').text

                except Exception:
                    print('***************************{}'.format(self.num))
                    self.num += 1
                    continue

            # 获取当前的url
            current_url = self.driver.current_url

            # 历史版本url
            historyUrl = "https://baike.baidu.com/historylist/" + name + "/{}".format(self.num)

            # print('正在查询:' + name + ' 编号:{}'.format(self.num))

            self.driver.execute_script('window.onbeforeunload = function() {}')

            self.driver.get(historyUrl)
            try:
                alert = self.driver.switch_to.alert
                alert.accept()
            except NoAlertPresentException:
                pass

            try:
                # 等待找到编辑次数这个组件
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.editedTimes')))
                time.sleep(0.2)
                edit_num = self.driver.find_element_by_class_name("editedTimes").text

            except Exception:
                print('***************************{}'.format(self.num))
                self.num += 1
                continue

            num_index1 = edit_num.index('辑')
            num_index2 = edit_num.index('次')

            # 获取编辑的次数
            edit_num = edit_num[num_index1 + 1:num_index2]


            # 获取创建者姓名
            cname = self.driver.find_element_by_xpath("/html/body/div[2]/table/tbody/tr["+edit_num+"]/td[4]/a").text

            # 获取创建时间
            ctime = self.driver.find_element_by_xpath("/html/body/div[2]/table/tbody/tr["+edit_num+"]/td[2]").text

            # 获取最近编辑者姓名
            ename = self.driver.find_element_by_xpath("/html/body/div[2]/table/tbody/tr[1]/td[4]/a").text

            # 获取最近编辑时间
            etime = self.driver.find_element_by_xpath("/html/body/div[2]/table/tbody/tr[1]/td[2]").text

            # 获取最近编辑原因"
            ereson = self.driver.find_element_by_xpath("/html/body/div[2]/table/tbody/tr[1]/td[5]").text


            # print('https://baike.baidu.com/item/' + name + '/{}'.format(self.num))

            str = "词条名称: %s 最近编辑者：%s 最近编辑时间：%s,'编辑次数：%s, '词条类型：%s '参数资料：%s%s.%s" %(name, ename, etime, edit_num, flag, referUrl, refer, referDate);

            # print(str)
            # print('   ')

            # print(name, flag, refer, referUrl, referDate, edit_num, cname, ename, ctime, etime, ereson, self.num)

            num_str = {"num": self.num}

            # 存储num信息
            with open("./data.json", 'r+', encoding='utf-8') as f:
                f.seek(0)  # 指针移到最前面
                f.truncate()  # 清除内容
                f.write(json.dumps(num_str))
                # 存储词条信息
                self.add(name, flag, refer, referUrl, referDate, edit_num, cname, ename, ctime, etime, ereson, self.num)

            self.num += 1

    # 操作数据库
    def add(self, name, flag, refer, referUrl, referDate, edit_num, cname, ename, ctime, etime, ereson, num):
        try:
            with self.connection.cursor() as cursor:
                sql = "INSERT INTO `baike` (`name`, `flag`,`refer`,`referUrl`,`referDate`,`edit_num`,`cname`,`ename`,`ctime`,`etime`,`ereson`,`num`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

                # Create a new record
                # 构建sql语句
                cursor.execute(sql, (name, flag, refer, referUrl, referDate, edit_num, cname, ename, ctime, etime, ereson, num))
                print(name,flag,ctime,num)
            # connection is not autocommit by default. So you must commit to save
            # your changes.
            # 向mysql提交更改，如果是查询语句，无需执行connection.commit()
            # 可以通过设置connection.autocommit()来自动提交，传入True即可
            self.connection.commit()
        except Exception:
            print('###############################################################################################')
            print(name, flag, refer, referUrl, referDate, edit_num, cname, ename, ctime, etime, ereson, num)
            print('操作数据库错误')
            print('###############################################################################################')
