# Переносить папку завершеної задачі: qa-toolkit/tasks/<KEY> → qa-toolkit/tasks/_done/<KEY>.
# Єдина файлова операція, дозволена щоденному прогону (run.ps1). Нічого не видаляє.
# Використання: powershell -NoProfile -File qa-toolkit/daily-checklists/archive-task.ps1 CMS-28567

param([Parameter(Mandatory)][string]$Key)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

if ($Key -notmatch '^[A-Z]+-\d+$') { Write-Output "ВІДМОВА: '$Key' — не ключ Jira"; exit 2 }

$tasks = Resolve-Path (Join-Path $PSScriptRoot '..\tasks')
$src   = Join-Path $tasks $Key
$done  = Join-Path $tasks '_done'
$dst   = Join-Path $done $Key

if (-not (Test-Path $src -PathType Container)) { Write-Output "ПРОПУЩЕНО: $Key — у корені tasks/ немає такої папки"; exit 0 }
if (Test-Path $dst) { Write-Output "ВІДМОВА: $Key — у _done/ вже є папка з таким ключем, переносити руками"; exit 3 }

New-Item -ItemType Directory -Force -Path $done | Out-Null
Move-Item -LiteralPath $src -Destination $dst
Write-Output "ПЕРЕНЕСЕНО: tasks/$Key → tasks/_done/$Key"
