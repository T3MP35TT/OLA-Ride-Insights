# GitHub repository setup

The Git executable was not available in this environment, so this directory is prepared for GitHub but has not been initialized, committed or pushed.

After installing Git for Windows, open PowerShell at the project root. Confirm the source workbook may be shared before adding it; it is large and may contain restricted data. The `.gitignore` excludes `.env`, secrets, virtual environments and PBIX files.

```powershell
git init
git add .
git status
git commit -m "Build OLA Ride Insights analytics capstone"
git branch -M main
git remote add origin https://github.com/<your-user>/OLA-RIDE-INSIGHTS.git
git push -u origin main
```

Create the empty GitHub repository first. Do not commit credentials or private Power BI files. If the raw workbook cannot be redistributed, keep it out of Git and update the documented local data path or use an approved private data source.
