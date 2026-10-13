# 自动化周报配置

## 1. 每周跑一次

### crontab (Linux/Mac)

```bash
# 每周一早上 8 点跑周报
0 8 * * 1 cd /path/to/seo-agent && /path/to/.venv/bin/python scripts/weekly_report.py --site "https://your-site.com/" --geo-brand "YourBrand" --out /path/to/reports/report_$(date +\%Y\%m\%d).md
```

### launchd (Mac)

`~/Library/LaunchAgents/com.seo-agent.weekly.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.seo-agent.weekly</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/.venv/bin/python</string>
        <string>/path/to/seo-agent/scripts/weekly_report.py</string>
        <string>--site</string>
        <string>https://your-site.com/</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Weekday</key>
        <integer>1</integer>
        <key>Hour</key>
        <integer>8</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/tmp/seo-weekly.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/seo-weekly.err</string>
</dict>
</plist>
```

## 2. 输出

- stdout 打印 markdown
- 文件默认 `weekly_report_YYYYMMDD.md`
- `--out` 显式指定路径

## 3. 配合 Slack/邮件

把 cron 改成 pipe 到 webhook:

```bash
0 8 * * 1 cd /path && python scripts/weekly_report.py --site X | curl -X POST -H "Content-Type: text/plain" --data-binary @- https://hooks.slack.com/services/XXX
```

## 4. mock 模式提示

如果 DataForSEO / xAI 还在 mock 模式，周报中会标注 `⚠️ mock 模式`。
跑真实数据前先按 [`STARTUP.md`](../docs/STARTUP.md) 接好凭证。
