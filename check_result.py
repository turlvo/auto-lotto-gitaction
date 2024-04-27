import re
import sys
import time
import json
from datetime import datetime, timedelta
from typing import List

from requests import post, get, patch, Response
from playwright.sync_api import Playwright, sync_playwright

RUN_FILE_NAME = sys.argv[0]

# 동행복권 아이디와 패스워드를 설정
USER_ID = sys.argv[1]
USER_PW = sys.argv[2]

# GITHUB
GITHUB_TOKEN = sys.argv[3]
GITHUB_OWNER = sys.argv[4]
GITHUB_REPO = sys.argv[5]
GITHUB_ISSUE_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/issues"


def __get_now() -> datetime:
    now_utc = datetime.utcnow()
    korea_timezone = timedelta(hours=9)
    now_korea = now_utc + korea_timezone
    return now_korea


def __check_lucky_number(lucky_numbers: List[str], my_numbers: List[str]) -> str:
    return_msg = ""
    for my_num in my_numbers:
        if my_num in lucky_numbers:
            return_msg += f" [ {my_num} ] "
            continue
        return_msg += f" {my_num} "
    return return_msg


def hook_github_get_issues() -> Response:
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer "+ GITHUB_TOKEN,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    res = get(GITHUB_ISSUE_URL, headers=headers)
    return res


def hook_github_create_issue(title: str, content: str, label: str) -> Response:
    payload = {
        "title": title,
        "body": content,
        "labels": [label]
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer "+ GITHUB_TOKEN,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    res = post(GITHUB_ISSUE_URL, data=json.dumps(payload), headers=headers)
    return res


def hook_github_update_issue(number: str, title: str, content: str, label: str) -> Response:
    payload = {
        "title": title,
        "body": content,
        "labels": [label]
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer "+ GITHUB_TOKEN,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    res = patch(GITHUB_ISSUE_URL + f"/{number}", data=json.dumps(payload), headers=headers)
    return res

def run(playwright: Playwright) -> None:
    try:
        issues_list = hook_github_get_issues().json()
        if len(issues_list) == 0:
            return

        if len(issues_list[0]["labels"]) > 0 and issues_list[0]["labels"][0]["name"] != ":hourglass:":
            return

        browser = playwright.chromium.launch(headless=True)  # chrome 브라우저를 실행
        context = browser.new_context()

        page = context.new_page()
        page.goto("https://dhlottery.co.kr/user.do?method=login")
        page.click('[placeholder="아이디"]')
        page.fill('[placeholder="아이디"]', USER_ID)
        page.press('[placeholder="아이디"]', "Tab")
        page.fill('[placeholder="비밀번호"]', USER_PW)
        page.press('[placeholder="비밀번호"]', "Tab")

        # Press Enter
        # with page.expect_navigation(url="https://ol.dhlottery.co.kr/olotto/game/game645.do"):
        with page.expect_navigation():
            page.press('form[name="jform"] >> text=로그인', "Enter")
        time.sleep(4)

        # 당첨 결과 및 번호 확인, parsing issue 때문에 3중 retry
        page.goto("https://dhlottery.co.kr/common.do?method=main")
        retry_cnt = 0
        result_info = page.query_selector("#article div.content")
        while not result_info and retry_cnt < 3:
            result_info = page.query_selector("#article div.content")
            retry_cnt += 1
        result_info = result_info.inner_text().split("이전")[0].replace("\n", " ")

        # 번호 추출하기
        # last index가 보너스 번호
        lucky_number = (
            result_info.split("당첨번호")[-1]
            .split("1등")[0]
            .strip()
            .replace("보너스번호 ", "")
            .replace(" ", ",")
        )
        lucky_number = lucky_number.split(",")

        # 오늘 구매한 복권 결과
        now_date = __get_now().date().strftime("%Y%m%d")
        page.goto(
            url=f"https://dhlottery.co.kr/myPage.do?method=lottoBuyList&searchStartDate={now_date}&searchEndDate={now_date}&lottoId=&nowPage=1"
        )

        # 날짜 잘못 잡음
        try:
            a_tag_href = page.query_selector(
                "tbody > tr:nth-child(1) > td:nth-child(4) > a"
            ).get_attribute("href")
        except AttributeError as exc:
            raise Exception(
                f"{exc} 에러 발생했습니다. now_date 값이 잘못세팅된 것 같습니다. 구매한 복권의 날짜와 결과 체크의 날짜가 동일한가요?"
            )

        detail_info = re.findall(r"\d+", a_tag_href)
        page.goto(
            url=f"https://dhlottery.co.kr/myPage.do?method=lotto645Detail&orderNo={detail_info[0]}&barcode={detail_info[1]}&issueNo={detail_info[2]}"
        )
        result_msg = ""
        win_cnt = 0
        for result in page.query_selector_all("div.selected li"):
            # 0번째 index에 기호와 당첨/낙첨 여부 포함
            my_lucky_number = result.inner_text().split("\n")

            if my_lucky_number[0] == '당첨':
                win_cnt = win_cnt + 1

            result_msg += (
                my_lucky_number[0]
                + __check_lucky_number(lucky_number, my_lucky_number[1:])
                + "\n"
            )

        hook_github_update_issue(issues_list[0]['number'], issues_list[0]['title'], issues_list[0]['body'], ":tada:" if win_cnt > 0 else ":skull_and_crossbones:")
        # hook_github_create_issue(title, result_msg, ":tada:" if win_cnt > 0 else ":skull_and_crossbones:")


        # End of Selenium
        context.close()
        browser.close()
    except Exception as exc:
        context.close()
        browser.close()
        raise exc


with sync_playwright() as playwright:
    run(playwright)
