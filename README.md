# Fitpet Jira App

[![🚜 Build and Test](https://github.com/sanggi-wjg/fitpet-jira-app/actions/workflows/build.yaml/badge.svg)](https://github.com/sanggi-wjg/fitpet-jira-app/actions/workflows/build.yaml)

## Commands

| 명령어           | 설명                                                                                                               |
|------------------|--------------------------------------------------------------------------------------------------------------------|
| `assign-version` | PR 이름(`[XXX-1234] [ADMIN,CONSUMER] ...`)에서 Jira 이슈와 버전 키를 찾아, 미배포 릴리즈 버전을 이슈에 할당합니다. |
| `create-release` | 버전 키의 최신 릴리즈 버전을 찾아 패치 버전을 올린 신규 릴리즈를 생성합니다. (구현 중)                             |

```shell
uv run python main.py --help                  # 전체 명령어 목록
uv run python main.py assign-version --help   # 명령어별 옵션
```

```shell
uv run python main.py create-release --version-key XXX \
                                     --server https://xxx.atlassian.net \
                                     --project FMP \
                                     --username user@example.com \
                                     --token <JIRA_API_TOKEN>
```

## Add GitHub action

```
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
        run: |
          uv run --locked --no-dev python main.py assign-version \
                                    --pr "${{ github.event.pull_request.title }}" \
                                    --server ${{ secrets.JIRA_SERVER }} \
                                    --project ${{ secrets.JIRA_PROJECT }} \
                                    --username ${{ secrets.JIRA_USERNAME }} \
                                    --token ${{ secrets.JIRA_TOKEN }}
```
