# GitHub repository setup

This guide covers publishing the local project to a GitHub repository. Before pushing, review data redistribution rights and remove credentials or private report material.

## Before the first push

- Confirm that `data/OLA_DataSet.xlsx` and processed outputs may be shared. If not, keep them out of Git and provide an approved local or private runtime data source.
- Inspect `.gitignore` and run `git status` before committing. It excludes virtual environments, Python cache files, and Streamlit secrets, but does not currently exclude the workbook, processed CSV, or PBIX file.
- Do not commit credentials, secret tokens, or restricted Power BI content. Add ignore rules appropriate to your organization before staging sensitive files.
- Create an empty repository on GitHub and copy its remote URL.

## Initialize and push

From the project root in PowerShell:

```powershell
git init
git status
git add .
git status
git commit -m "Build OLA Ride Insights analytics project"
git branch -M main
git remote add origin https://github.com/<your-user>/<repository>.git
git push -u origin main
```

Review the staged file list before `git commit`. If a restricted file was staged, unstage it and add a suitable ignore rule before continuing.

For deployment after publishing, see the [deployment guide](DEPLOYMENT_GUIDE.md).
