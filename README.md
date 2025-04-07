# Fitpet Jira App

## Add Github action

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
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Clone repo and install poetry
        run: |
          git clone https://github.com/sanggi-wjg/fitpet-jira-app.git app

      - name: Install poetry and dependencies
        run: |
          curl -sSL https://install.python-poetry.org | python3 -
          echo "$HOME/.local/bin" >> $GITHUB_PATH
          poetry --version

          cd app
          poetry install --no-interaction --no-root

      - name: Run Python Script with PR Title
        working-directory: app
        run: |
          poetry run python main.py --command assign_version \
                                    --pr "${{ github.event.pull_request.title }}" \
                                    --server ${{ secrets.JIRA_SERVER }} \
                                    --project ${{ secrets.JIRA_PROJECT }} \
                                    --username ${{ secrets.JIRA_USERNAME }} \
                                    --token ${{ secrets.JIRA_TOKEN }}
```
