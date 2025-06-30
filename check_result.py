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


# def __check_lucky_number(lucky_numbers: List[str], my_numbers: List[str]) -> str:
#     return_msg = ""
#     for my_num in my_numbers:
#         if my_num in lucky_numbers:
#             return_msg += f" [ {my_num} ] "
#             continue
#         return_msg += f" {my_num} "
#     return return_msg
    
def __check_lucky_number(win_numbers, my_numbers):
    matched = [n for n in my_numbers if n in win_numbers]
    return f"{len(matched)}개 일치: {' '.join(matched)}"


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

# def run(playwright: Playwright) -> None:
#     try:
#         issues_list = hook_github_get_issues().json()
#         if len(issues_list) == 0:
#             return

#         if len(issues_list[0]["labels"]) > 0 and issues_list[0]["labels"][0]["name"] != ":hourglass:":
#             return

#         browser = playwright.chromium.launch(headless=True)  # chrome 브라우저를 실행
#         context = browser.new_context()

#         page = context.new_page()
#         page.goto("https://dhlottery.co.kr/user.do?method=login")
#         page.click('[placeholder="아이디"]')
#         page.fill('[placeholder="아이디"]', USER_ID)
#         page.press('[placeholder="아이디"]', "Tab")
#         page.fill('[placeholder="비밀번호"]', USER_PW)
#         page.press('[placeholder="비밀번호"]', "Tab")

#         # Press Enter
#         # with page.expect_navigation(url="https://ol.dhlottery.co.kr/olotto/game/game645.do"):
#         with page.expect_navigation():
#             page.press('form[name="jform"] >> text=로그인', "Enter")
#         time.sleep(4)

#         # 당첨 결과 및 번호 확인, parsing issue 때문에 3중 retry
#         page.goto("https://dhlottery.co.kr/common.do?method=main")
#         retry_cnt = 0
#         result_info = page.query_selector("#article div.content")
#         while not result_info and retry_cnt < 3:
#             result_info = page.query_selector("#article div.content")
#             retry_cnt += 1
#         result_info = result_info.inner_text().split("이전")[0].replace("\n", " ")

#         # 번호 추출하기
#         # last index가 보너스 번호
#         lucky_number = (
#             result_info.split("당첨번호")[-1]
#             .split("1등")[0]
#             .strip()
#             .replace("보너스번호 ", "")
#             .replace(" ", ",")
#         )
#         lucky_number = lucky_number.split(",")

#         # 오늘 구매한 복권 결과
#         #now_date = __get_now().date().strftime("%Y%m%d")
#         now_date = issues_list[0]['title'].replace("-", "")
#         print(now_date)
#         page.goto(
#             url=f"https://dhlottery.co.kr/myPage.do?method=lottoBuyList&searchStartDate={now_date}&searchEndDate={now_date}&lottoId=&nowPage=1"
#         )

#         # 날짜 잘못 잡음
#         try:
#             a_tag_href = page.query_selector(
#                 "tbody > tr:nth-child(1) > td:nth-child(4) > a"
#             ).get_attribute("href")
#         except AttributeError as exc:
#             raise Exception(
#                 f"{exc} 에러 발생했습니다. now_date 값이 잘못세팅된 것 같습니다. 구매한 복권의 날짜와 결과 체크의 날짜가 동일한가요?"
#             )

#         detail_info = re.findall(r"\d+", a_tag_href)
#         page.goto(
#             url=f"https://dhlottery.co.kr/myPage.do?method=lotto645Detail&orderNo={detail_info[0]}&barcode={detail_info[1]}&issueNo={detail_info[2]}"
#         )
#         result_msg = ""
#         win_cnt = 0
#         # for result in page.query_selector_all("div.selected li"):
#         #     # 0번째 index에 기호와 당첨/낙첨 여부 포함
#         #     my_lucky_number = result.inner_text().split("\n")

#         #     if my_lucky_number[0] != '(낙첨)':
#         #         win_cnt = win_cnt + 1

#         #     result_msg += (
#         #         my_lucky_number[0]
#         #         + __check_lucky_number(lucky_number, my_lucky_number[1:])
#         #         + "\n"
#         #     )
#         for result in page.query_selector_all("div.selected li"):
#             my_lucky_number = result.inner_text().split("\n")
#             # 참고: inner_text는 ['A', '자동 (낙첨)', '4', '19', '23', '30', '32', '41'] 같은 구조
        
#             status = my_lucky_number[1] if len(my_lucky_number) > 1 else ''
#             numbers = my_lucky_number[2:]
        
#             if '낙첨' not in status:
#                 win_cnt += 1
        
#             result_msg += (
#                 f"{my_lucky_number[0]} - {status} - "
#                 + __check_lucky_number(lucky_number, numbers)
#                 + "\n"
#             )

#         hook_github_update_issue(issues_list[0]['number'], issues_list[0]['title'], issues_list[0]['body'], ":tada:" if win_cnt > 0 else ":skull_and_crossbones:")
#         # hook_github_create_issue(title, result_msg, ":tada:" if win_cnt > 0 else ":skull_and_crossbones:")


#         # End of Selenium
#         context.close()
#         browser.close()
#     except Exception as exc:
#         context.close()
#         browser.close()
#         raise exc

def run(playwright: Playwright) -> None:
    try:
        issues_list = hook_github_get_issues().json()
        if not issues_list:
            return

        for issue in issues_list:
            labels = [label["name"] for label in issue.get("labels", [])]
            if ":hourglass:" not in labels:
                continue  # ⏳ 없는 이슈는 skip

            now_date = issue["title"].replace("-", "")
            print(f"▶ 처리 중: #{issue['number']} {now_date}")

            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            # 로그인
            page.goto("https://dhlottery.co.kr/user.do?method=login")
            page.fill('[placeholder="아이디"]', USER_ID)
            page.press('[placeholder="아이디"]', "Tab")
            page.fill('[placeholder="비밀번호"]', USER_PW)
            page.press('[placeholder="비밀번호"]', "Tab")
            with page.expect_navigation():
                page.press('form[name="jform"] >> text=로그인', "Enter")
            time.sleep(4)

            # 당첨 번호 추출
            page.goto("https://dhlottery.co.kr/common.do?method=main")
            result_info = None
            for _ in range(3):
                result_info = page.query_selector("#article div.content")
                if result_info:
                    break
            if not result_info:
                raise Exception("당첨 정보 파싱 실패")
            result_text = result_info.inner_text().split("이전")[0].replace("\n", " ")

            # 추첨일 확인
            draw_date_match = re.search(r"추 첨 일\s*:\s*(\d{4}/\d{2}/\d{2})", result_text)
            if draw_date_match:
                draw_date_str = draw_date_match.group(1)
                draw_date = datetime.strptime(draw_date_str, "%Y/%m/%d").date()
                today = datetime.now().date()
                if draw_date > today:
                    print(f"⏳ 아직 추첨 전입니다 ({draw_date_str}) - skip")
                    context.close()
                    browser.close()
                    return

            lucky_number = (
                result_text.split("당첨번호")[-1]
                .split("1등")[0]
                .strip()
                .replace("보너스번호 ", "")
                .replace(" ", ",")
            ).split(",")

            # 구매 복권 내역 조회
            page.goto(
                url=f"https://dhlottery.co.kr/myPage.do?method=lottoBuyList&searchStartDate={now_date}&searchEndDate={now_date}&lottoId=&nowPage=1"
            )
            try:
                a_tag_href = page.query_selector(
                    "tbody > tr:nth-child(1) > td:nth-child(4) > a"
                ).get_attribute("href")
            except:
                print(f"📛 날짜 {now_date} 에 구매 내역 없음")
                context.close()
                browser.close()
                continue

            detail_info = re.findall(r"\d+", a_tag_href)
            page.goto(
                url=f"https://dhlottery.co.kr/myPage.do?method=lotto645Detail&orderNo={detail_info[0]}&barcode={detail_info[1]}&issueNo={detail_info[2]}"
            )

            result_msg = ""
            win_cnt = 0

            for result in page.query_selector_all("div.selected li"):
                my_lucky_number = result.inner_text().split("\n")
                # 예: ['A', '자동 (낙첨)', '4', '19', '23', '30', '32', '41']
                status_line = next((s for s in my_lucky_number if '(낙첨)' in s or '(당첨)' in s), '')
                is_winner = '낙첨' not in status_line
                numbers = my_lucky_number[2:]  # 숫자 부분만 추출

                if is_winner:
                    win_cnt += 1

                result_msg += f"{my_lucky_number[0]}" + "\n"

            # GitHub 이슈 상태 업데이트
            hook_github_update_issue(
                issue["number"],
                issue["title"],
                result_msg.strip(),
                ":tada:" if win_cnt > 0 else ":skull_and_crossbones:"
            )

            context.close()
            browser.close()

    except Exception as exc:
        try:
            context.close()
            browser.close()
        except:
            pass
        raise exc

with sync_playwright() as playwright:
    run(playwright)
