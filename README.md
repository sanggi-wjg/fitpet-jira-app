# Fitpet Jira App

[![🚜 Build and Test](https://github.com/sanggi-wjg/fitpet-jira-app/actions/workflows/build.yaml/badge.svg)](https://github.com/sanggi-wjg/fitpet-jira-app/actions/workflows/build.yaml)

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
          uv run --locked --no-dev python main.py --command assign_version \
                                    --pr "${{ github.event.pull_request.title }}" \
                                    --server ${{ secrets.JIRA_SERVER }} \
                                    --project ${{ secrets.JIRA_PROJECT }} \
                                    --username ${{ secrets.JIRA_USERNAME }} \
                                    --token ${{ secrets.JIRA_TOKEN }}
```
