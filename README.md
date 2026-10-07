# Fitpet Jira App

[![🚜 Build and Test](https://github.com/sanggi-wjg/fitpet-jira-app/actions/workflows/build.yaml/badge.svg)](https://github.com/sanggi-wjg/fitpet-jira-app/actions/workflows/build.yaml)

## Commands

| 명령어           | 설명                                                                                                               |
|------------------|--------------------------------------------------------------------------------------------------------------------|
| `assign-version` | PR 이름(`[XXX-1234] [ADMIN,CONSUMER] ...`)에서 Jira 이슈와 버전 키를 찾아, 미배포 릴리즈 버전을 이슈에 할당합니다. |
| `create-release` | 버전 키의 최신 릴리즈 버전을 찾아 패치 버전을 올린 신규 릴리즈를 생성합니다.                                       |

```shell
uv run python main.py --help                  # 전체 명령어 목록
uv run python main.py assign-version --help   # 명령어별 옵션
```

### 공통 인자

모든 명령어에 필요한 Jira 접속 정보입니다. 옵션 대신 환경변수로도 전달할 수 있습니다.

| 옵션         | 환경변수        | 설명                                             |
|--------------|-----------------|--------------------------------------------------|
| `--server`   | `JIRA_SERVER`   | Jira 서버 주소 (예시, https://xxx.atlassian.net) |
| `--project`  | `JIRA_PROJECT`  | Jira 프로젝트 키 (예시, FMP)                     |
| `--username` | `JIRA_USERNAME` | Jira 계정 이메일                                 |
| `--token`    | `JIRA_TOKEN`    | Jira API 토큰                                    |

### `assign-version`

| 옵션   | 설명                                                                                                            |
|--------|-----------------------------------------------------------------------------------------------------------------|
| `--pr` | Github PR 이름 (예시, `[FMP-1234] [ADMIN,CONSUMER] 상품 조회 API 구현`). 띄어쓰기가 있으니 따옴표로 감싸주세요. |

### `create-release`

| 옵션            | 설명                                                                     |
|-----------------|--------------------------------------------------------------------------|
| `--version-key` | 릴리즈 버전 키 (`API`, `ADMIN`, `SELLER`, `CONSUMER`, `BATCH`, `LEGACY`) |

## GithubAction

### assign-version

```yaml
name: 😀 When PR Merged

on:
  pull_request:
    types: [ closed ]

jobs:
  assign-version-of-task:
    if: github.event.pull_request.merged == true && github.base_ref == 'main'
    name: Assign Version of Task
    runs-on: ubuntu-latest

    steps:
      - name: Install uv
        uses: astral-sh/setup-uv@v10.2.0

      - name: Clone repo
        run: |
          git clone https://github.com/sanggi-wjg/fitpet-jira-app.git app

      - name: Run Python Script with PR Title
        working-directory: app
        env:
          PR_TITLE: ${{ github.event.pull_request.title }}
          JIRA_SERVER: ${{ secrets.JIRA_SERVER }}
          JIRA_PROJECT: ${{ secrets.JIRA_PROJECT }}
          JIRA_USERNAME: ${{ secrets.JIRA_USERNAME }}
          JIRA_TOKEN: ${{ secrets.JIRA_TOKEN }}
        run: |
          uv run --locked --no-dev python main.py assign-version --pr "$PR_TITLE"
```
