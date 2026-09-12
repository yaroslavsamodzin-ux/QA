<#
    qa-toolkit/android/setup.ps1

    Ставить Android Platform Tools (adb) — без інсталятора, без адмінських прав,
    без root на телефоні. Просто розпаковує офіційний архів Google у профіль
    користувача.

    Запуск:
        powershell -ExecutionPolicy Bypass -File qa-toolkit\android\setup.ps1
        powershell -ExecutionPolicy Bypass -File qa-toolkit\android\setup.ps1 -AddToPath

    Видалити: стерти папку, яку скрипт назве в кінці, і прибрати її з PATH.
#>
param(
    [switch]$AddToPath,
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

$Url     = 'https://dl.google.com/android/repository/platform-tools-latest-windows.zip'
$Dest    = Join-Path $env:LOCALAPPDATA 'platform-tools'
$AdbPath = Join-Path $Dest 'adb.exe'

Write-Host ''
Write-Host '=== Android Platform Tools ===' -ForegroundColor Cyan

# Уже є в системі?
$existing = Get-Command adb -ErrorAction SilentlyContinue
if ($existing -and -not $Force) {
    Write-Host "adb вже встановлений: $($existing.Source)" -ForegroundColor Green
    & $existing.Source version
    Write-Host 'Нічого робити не треба. Для перевстановлення додай -Force.'
    return
}

if ((Test-Path $AdbPath) -and -not $Force) {
    Write-Host "Уже розпаковано: $AdbPath" -ForegroundColor Green
} else {
    $zip = Join-Path $env:TEMP 'platform-tools.zip'
    Write-Host "Завантажую $Url ..."
    Invoke-WebRequest -Uri $Url -OutFile $zip -UseBasicParsing
    $mb = [math]::Round((Get-Item $zip).Length / 1MB, 1)
    Write-Host "Завантажено $mb МБ. Розпаковую у $env:LOCALAPPDATA ..."

    if (Test-Path $Dest) { Remove-Item $Dest -Recurse -Force }
    Expand-Archive -Path $zip -DestinationPath $env:LOCALAPPDATA -Force
    Remove-Item $zip -Force
}

if (-not (Test-Path $AdbPath)) {
    throw "Щось пішло не так — adb.exe не знайдено за шляхом $AdbPath"
}

Write-Host ''
& $AdbPath version
Write-Host ''
Write-Host "Шлях: $AdbPath" -ForegroundColor Green

if ($AddToPath) {
    $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    if ($userPath -notlike "*$Dest*") {
        [Environment]::SetEnvironmentVariable('Path', "$userPath;$Dest", 'User')
        Write-Host "Додано в PATH користувача (запрацює в нових вікнах терміналу)." -ForegroundColor Green
    } else {
        Write-Host 'Уже в PATH.'
    }
}

Write-Host ''
Write-Host 'Далі на телефоні:' -ForegroundColor Cyan
Write-Host '  1. Налаштування > Про телефон > тапнути "Номер збірки" 7 разів'
Write-Host '  2. Налаштування > Для розробників > увімкнути "Налагодження USB"'
Write-Host '  3. Підключити кабелем і на телефоні натиснути "Дозволити" у вікні запиту'
Write-Host ''
Write-Host 'Перевірка:' -ForegroundColor Cyan
Write-Host '  powershell -ExecutionPolicy Bypass -File qa-toolkit\android\adb.ps1 devices'
Write-Host ''
