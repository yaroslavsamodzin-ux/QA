# Щоденний прогін: qa-checklist на нові задачі типу Test з мого фільтра Jira.
# Запускається планувальником (register-task.ps1), можна й руками: powershell -File run.ps1

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$here    = Split-Path -Parent $MyInvocation.MyCommand.Path
$repo    = Resolve-Path (Join-Path $here '..\..')
$logDir  = Join-Path $here 'logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$log     = Join-Path $logDir ("{0:yyyy-MM-dd_HHmm}.log" -f (Get-Date))
$prompt  = Get-Content -Raw -Encoding UTF8 (Join-Path $here 'prompt.md')

# Тільки потрібні тулзи; все інше в -p відхиляється автоматично.
# readonly-guard hook діє і тут — запис у Jira/GitLab заблокований так само, як у звичайній сесії.
$tools = @(
  'mcp__claude-in-chrome',
  'Read', 'Glob', 'Grep', 'Write', 'Edit',
  'Skill', 'Artifact', 'ToolSearch', 'PushNotification'
) -join ','

Set-Location $repo
"=== $(Get-Date -Format s) старт ===" | Out-File -FilePath $log -Encoding utf8

# Hook-и Claude Code на Windows виконуються через Git Bash. Без нього $CLAUDE_PROJECT_DIR у
# команді readonly-guard не розкривається, hook падає і (fail-closed) блокує всі тулзи Chrome.
# Git тут стоїть у D:\Git, а не в Program Files, тому шлях задаємо явно.
if (-not $env:CLAUDE_CODE_GIT_BASH_PATH) { $env:CLAUDE_CODE_GIT_BASH_PATH = 'D:\Git\bin\bash.exe' }

$prompt | & claude -p --chrome `
  --permission-mode acceptEdits `
  --allowedTools $tools `
  2>&1 | Out-File -FilePath $log -Append -Encoding utf8

"=== $(Get-Date -Format s) кінець, exit $LASTEXITCODE ===" | Out-File -FilePath $log -Append -Encoding utf8

# Логи старші за 30 днів прибираємо
Get-ChildItem $logDir -Filter *.log | Where-Object LastWriteTime -lt (Get-Date).AddDays(-30) | Remove-Item
