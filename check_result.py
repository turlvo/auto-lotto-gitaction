import re
import sys
import time
import json
from datetime import datetime, timedelta

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
            
            # 추첨일 추출
            draw_date_raw = page.locator("ul >> li").filter(has_text="추 첨 일").first.inner_text()
            # draw_date_raw 예: "추 첨 일 : 2025/07/05"
            draw_date_match = re.search(r"\d{4}/\d{2}/\d{2}", draw_date_raw)
            if draw_date_match:
                draw_date = datetime.strptime(draw_date_match.group(), "%Y/%m/%d").date()
                # 구매일로부터 해당 주의 토요일 계산
                purchase_date = datetime.strptime(issue["title"], "%Y-%m-%d").date()
                # 해당 주의 토요일 구하기 (토요일 = weekday 5)
                days_until_saturday = (5 - purchase_date.weekday()) % 7
                if days_until_saturday == 0:  # 이미 토요일인 경우
                    expected_draw_date = purchase_date
                else:
                    expected_draw_date = purchase_date + timedelta(days=days_until_saturday)
                
                if draw_date != expected_draw_date:
                    print(f"⏳ 추첨일 불일치: 예상 {expected_draw_date}, 실제 {draw_date} - skip")
                    context.close()
                    browser.close()
                    continue

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

                result_msg += f"{my_lucky_number[0]} - {status_line} - {__check_lucky_number(lucky_number, numbers)}\n"

            # GitHub 이슈 상태 업데이트 - 기존 내용에 결과 추가
            updated_body = issue["body"] + f"\n\n## 추첨 결과\n{result_msg}\n\n당첨 번호: {', '.join(lucky_number[:-1])} + 보너스 {lucky_number[-1]}"
            hook_github_update_issue(
                issue["number"],
                issue["title"],
                updated_body,
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
