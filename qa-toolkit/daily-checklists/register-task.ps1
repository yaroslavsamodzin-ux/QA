# Реєструє задачу Windows "QA Daily Checklists": щодня о 9:00 запускає run.ps1.
# Запуск лише коли користувач залогінений (потрібен відкритий Work Chrome з розширенням).
# Якщо о 9:00 комп'ютер спав/був вимкнений — прогін стартує, щойно стане доступним.
# Видалити: Unregister-ScheduledTask -TaskName 'QA Daily Checklists' -Confirm:$false

$run = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) 'run.ps1'

$action   = New-ScheduledTaskAction -Execute 'powershell.exe' `
              -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$run`""
$trigger  = New-ScheduledTaskTrigger -Daily -At 9:00
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopIfGoingOnBatteries `
              -AllowStartIfOnBatteries -ExecutionTimeLimit (New-TimeSpan -Hours 2) -MultipleInstances IgnoreNew
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName 'QA Daily Checklists' -Action $action -Trigger $trigger `
  -Settings $settings -Principal $principal -Force |
  Select-Object TaskName, State
