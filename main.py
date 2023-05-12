import os

import pandas as pd

import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def checkKeyword(sInputText):

    keyword = readTextFile('sortKeyword.txt')

    lstKeyword = keyword.split('\n')

    # lstKeyword = ['무료', '일일체험', '일일 체험']

    if sInputText is None:
        return False

    for i in lstKeyword:
        if i in sInputText:
            return True
            break
    return False

def saveDicToTextFile(dic):
    pass

def saveDicToExcelFile(dic, sFilePath, sSheetName):
    df = pd.DataFrame(columns=['상호명', '가격표', '이벤트', '쿠폰', 'url'])

    for i in dic:
        df.loc[len(df.index)] = [str(i), str(dic[i][0]), str(dic[i][1]), str(dic[i][2]), str(dic[i][3])]

    df.to_excel(sFilePath, sheet_name=sSheetName)

def readTextFile(sFilePath):

    sResultPath = "result.txt"

    if not os.path.isfile(sFilePath) or os.stat(sFilePath).st_size == 0:
        open(sFilePath, "w")
        file = open(sResultPath, "w")
        file.write(sFilePath+"에 정보 입력 필요")
        return None

    return open(sFilePath, "r", encoding='UTF8').read()

def initializeFrame(driver, time):
    driver.implicitly_wait(time)
    driver.switch_to.default_content()
    driver.implicitly_wait(time)

def selectFrame(driver, sFrameName, time):
    driver.implicitly_wait(time)
    driver.switch_to.frame(sFrameName)
    driver.implicitly_wait(time)

def startJob(SearchKeywords):

    lstKeyword = SearchKeywords.split("\n")
    dicResult = {}

    for keyword in lstKeyword:

        driver = webdriver.Chrome("chromedriver.exe")  # selenium 사용에 필요한 chromedriver.exe 파일 경로 지정
        driver.get("https://map.naver.com/v5/")  # 네이버 신 지도

        wait = WebDriverWait(driver, 3)

        # 브라우저 작업
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "input_search")))
        search_box = driver.find_element(By.CLASS_NAME, "input_search")
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.ENTER)

        while True:

            # 변수 초기화
            lstPlace = []  # 페이지 내 상호 저장
            timeoutSelectFrame = 1
            timeoutInitialFrame = 1

            sResultPriceInfo = None
            sResultBookInfo = None
            sResultAddrInfo = None

            print("start ::: 스크롤 내림")
            # 프레임 변경
            # wait.until(EC.presence_of_element_located((By.ID, "searchIframe")))
            # driver.switch_to.frame('searchIframe')
            selectFrame(driver, 'searchIframe', timeoutSelectFrame)

            # 프레임 클릭
            driver.find_element(By.CSS_SELECTOR, value="body").click()
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
            before_len = 0

            # 페이지 스크롤 End 까지 출력
            while True:
                for _ in range(0, 5):
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
                    driver.find_element(By.CSS_SELECTOR, value="body").send_keys(Keys.END)

                # 스크롤 후 로딩 된 리스트 갯수 확인
                lst = driver.find_elements(By.CLASS_NAME, value="place_bluelink")
                after_len = len(lst)
                # 로딩된  데이터 개수가 같다면 반복을 멈춤
                print("before_leb : {0}, after_len : {1}".format(before_len, after_len))
                if before_len == after_len:
                    break
                before_len = after_len
                time.sleep(0.5)

            # # 프레임 초기화
            # driver.switch_to.default_content()
            initializeFrame(driver, timeoutInitialFrame)

            print("end ::: 스크롤 내림")

            # 블루링크 클릭
            print("start ::: 블루링크 클릭")
            selectFrame(driver, 'searchIframe', timeoutSelectFrame)
            # driver.implicitly_wait(10)
            # driver.switch_to.frame('searchIframe')

            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
            lstBlueLink = driver.find_elements(By.CLASS_NAME, value="place_bluelink")

            for i in lstBlueLink:
                try:
                    print("")
                    initializeFrame(driver, timeoutInitialFrame)
                    selectFrame(driver, 'searchIframe', timeoutSelectFrame)
                    sResultPriceInfo = ""
                    sResultEventInfo = ""
                    sResultCuponInfo = ""


                    # 이미 열람한 가게는 건너띄기
                    if str(i.text) in lstPlace:
                        continue

                    placeName = i.text  # 가게 상호
                    print(placeName)

                    lstPlace.append(i.text)
                    i.click()
                    # time.sleep(1)
                    initializeFrame(driver, timeoutInitialFrame)
                    selectFrame(driver, 'entryIframe', timeoutSelectFrame)
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))

                    # 주소 출력 //
                    startTime = time.time()
                    try:
                        while True:
                            addrInfo = driver.find_element(By.CLASS_NAME, value="O8qbU.tQY7D").text

                            if sResultAddrInfo != addrInfo:
                                sResultAddrInfo = addrInfo
                                break

                            if time.time() - startTime > 5:
                                sResultAddrInfo = addrInfo
                            time.sleep(0.1)

                    except Exception as e:
                        sResultAddrInfo = ""
                        print("addrInfo Err : " + str(e)[0:50])

                    print(sResultAddrInfo.split("\n")[1])

                    try:
                        if not sResultAddrInfo is None:
                            time.sleep(0.3)
                            sResultPriceInfo = driver.find_element(By.CLASS_NAME, value="O8qbU.tXI2c").text

                    except Exception as e:
                        sResultPriceInfo = ""
                        print("priceInfo Err : " + str(e)[0:50])

                    try:
                        if not sResultAddrInfo is None:
                            sResultEventInfo = driver.find_element(By.CLASS_NAME, value="ngGKH.IH0v0").text

                    except Exception as e:
                        sResultBookInfo = ""
                        print("bookInfo Err : " + str(e)[0:50])

                    try:
                        if not sResultAddrInfo is None:
                            sResultCuponInfo = driver.find_element(By.CLASS_NAME, value="YA6Z1._1_64.UsEih.e33ZS").text

                    except Exception as e:
                        sResultCuponInfo = ""
                        print("cuponInfo Err : " + str(e)[0:50])

                    if sResultPriceInfo == "" and sResultEventInfo == "" and sResultCuponInfo == "":
                        continue
                    elif not checkKeyword(sResultPriceInfo) and not checkKeyword(sResultEventInfo) and not checkKeyword(sResultCuponInfo):
                        continue
                    else:
                        dicResult[placeName] = [sResultPriceInfo, sResultEventInfo, sResultCuponInfo, driver.current_url]
                        print(sResultAddrInfo.replace("\n","").replace(" ","")[0:10] + " / " + sResultPriceInfo.replace("\n","").replace(" ","")[0:10] + " / " + sResultEventInfo.replace("\n","").replace(" ","")[0:10] + " / " + sResultCuponInfo.replace("\n","").replace(" ","")[0:10])
                except Exception as e:
                    print(e)

            initializeFrame(driver, timeoutInitialFrame)
            print("end ::: 블루링크 클릭")

            # 다음 페이지 버튼 클릭
            print("start ::: 다음 페이지 클릭")

            selectFrame(driver, 'searchIframe', timeoutSelectFrame)

            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))

            pageBtns = driver.find_elements(By.CLASS_NAME, "eUTV2 ")
            nextBtn = pageBtns[-1]
            nextBtn.click()

            validNextBtn = driver.find_elements(By.CLASS_NAME, value="eUTV2.Y89AQ")
            if len(validNextBtn) > 0:
                initializeFrame(driver, timeoutInitialFrame)
                print("프로세스 종료")
                break

            # 프레임 초기화
            initializeFrame(driver, timeoutInitialFrame)
            print("end ::: 다음 페이지 클릭")

        driver.close()

    return dicResult

def main():

    df = pd.DataFrame(columns = ['상호명', '가격표', '이벤트', '쿠폰', 'url'])

    sResult = ""

    keywords = readTextFile('searchKeyword.txt')

    # 합쳐서 받기
    dic = startJob(keywords)
    saveDicToExcelFile(dic, 'result.xlsx')

    # keyword = keywords.split("\n")
    # dicTotal = {}
    #
    # for i in keyword:
    #     try:
    #         dic = startJob(i)
    #     except:
    #         continue
    #
    #     for j in dic.copy():
    #         for k in dicTotal.copy():
    #             if j == k:
    #                 dic.pop(j)
    #                 break
    #
    #     dicTotal.update(dic)
    #    saveDicToExcelFile(dic, i.replace(" ","")+'.xlsx', i)

main()