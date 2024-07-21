[![Lotto Buy Bot (로또 구매봇)](https://github.com/Nuung/auto-lotto-gitaction/actions/workflows/action.yml/badge.svg?branch=main)](https://github.com/Nuung/auto-lotto-gitaction/actions/workflows/action.yml)

[![Check The Result Of Lotto (로또 결과봇)](https://github.com/Nuung/auto-lotto-gitaction/actions/workflows/action-result.yml/badge.svg?branch=main)](https://github.com/Nuung/auto-lotto-gitaction/actions/workflows/action-result.yml)

# Buying the lottery automatically through GitHub Actions

> **_매주 토요일 KST 08:50 에 동행 복권 로또 구매_** <br/> > **_매주 토요일 KST 21:50 에 동행 복권 로또 결과 slack hooking_**

- https://dhlottery.co.kr/ 동행복권 홈페이지
- https://velog.io/@king/githubactions-lotto 원작자분 벨로그입니다!
  - 해당 레포는 원작 소스 코드 기반으로 `(1)public` 하게 사용할 수 있게,
  - `(2) slack hook (optional)`
  - `(3) 결과/기타 info check` 첨가 정도 추가 되었습니다.
- public 으로 공유할 수 있게 모든 민감 정보 action secrets 값으로 관리
- slack bot을 통해 slack noti (hook) 전달함
- **_예치금 필요합니다._**

## GETTING START
 
#### 1. `fork`를 한다!

#### 2. `fork`한 repo를 `git clone` 한다.

#### 3. slack bot 세팅은 아래 글 참조, 사용하지 않는다면 그냥 주석처리해도 된다.

- https://yunwoong.tistory.com/129 최신글 참고 추천!
- slack python SDK를 사용하는 것이 아니라 restAPI Http call을 한다.

#### 4. `action.yml` 파일을 보면 gitaction 시크릿값을 python run 인자로 넘길때 사용하고 있다. 즉 시크릿값만 세팅하면 된다.

![](./imgs/img1.png)

#### 5. 시크릿값은 아래 사진 참고
![](./imgs/img2.png)

- GIT_OWNER는 Github id
- GIT_REPO_NAME은 지금 repository 명 ex) `auto-lotto-gitaction`
- BUY_COUNT가 구매할 복권 수 세팅 값이다.
- 그 외 user값은 https://dhlottery.co.kr/common.do?method=main 여기 회원가입한 정보를 넣자. **_절대 절대 절대 노출 안되게 조심_**

#### 6. 위 세팅 완료 후 test를 위해 `action.yml` 에서 `on: [push]` 로 바꾸고 push를 해보자

![](./imgs/img3.png)

- 구입 완료 / 에러시에 `Issues`에 새로운 issue가 등록 된다

#### 7. `action-result.yml` 은 이제 발표된 추첨 번호를 slack을 통해 전달해준다. 20시 35분경 발표가 나는 점, 업데이트가 나중에 되는점을 참작해 21시 50분경에 러닝하게 했다.

![](./imgs/img4.png)
![](./imgs/img5.png)

- 추첨 결과를 Issue Label로 추가해줌
- 하나라도 당첨시 🎉, 낙첨시 ☠️

## To develop something more in the local

1. 가상환경 구성을 추천한다. 편한대로 구성하면 된다, ex. `python3 -m venv .venv`
2. `requirements.txt` file을 install 한다.
3. `playwright install` 를 해준다. 기본 준비 끝 - https://playwright.dev/
4. 디버깅 모드 셀레니움이 익숙한 사람은 그렇게 사용해도 무방하다.

## TODO

- [x] 발표난 당첨 번호와 자동 비교 work flow 추가 ~~[23.06.03]~~
- [x] 랜덤으로 구매한 복권 번호, 우선 최대 5개 까지만, 번호 noti work flow 추가 ~~[23.06.25]~~
- [x] 구매한 복권 당첨 여부 가져오기 ~~[23.07.09]~~
- [x] result parsing issue 에서 retry 추가 ~~[24.02.24]~~
- [x] 특정 이슈는 slack을 통해서 빠르게 핸들링 할 수 있게 템플릿 ~~[24.02.24]~~
- [ ] 선호하는 번호 넘버링 골라서 고를 수 있게
- [ ] 여지껏 고른 랜덤 번호 저장하도록 중앙저장소 & 데이터 분석 기반

## STACK

- python
  - python 3.8+
  - Playwright & selenium (chrome driver)
  - requests
- lint: flask8 & black
- github action (action.yml)

---

## LOG & ISSUE

![](./imgs/img-get-1.png)

- `23.08.12` 대박,, 5등 당첨! 감격!
