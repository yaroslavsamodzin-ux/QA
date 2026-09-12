<#
    qa-toolkit/android/adb.ps1

    Обгортка над adb з командами під ручне тестування.

    Запуск:
        powershell -ExecutionPolicy Bypass -File qa-toolkit\android\adb.ps1 <команда> [аргументи]

    Команди:
        devices                      список підключених пристроїв
        info                         модель, Android, розмір екрана, щільність
        shot [файл.png]              скріншот екрана
        rec <сек> [файл.mp4]         запис екрана
        tap <x> <y>                  тап
        swipe <x1> <y1> <x2> <y2> [мс]  свайп
        text "рядок"                 ввести текст у активне поле
        key <назва|код>              back home enter tab del menu power volup voldown
        open <url>                   відкрити посилання в браузері телефона
        app <package>                запустити застосунок
        ui [файл.xml]                вивантажити дерево UI
        audit                        знайти дрібні тач-таргети й елементи за межами екрана
        log [фільтр]                 logcat (Ctrl+C щоб зупинити)
        clearlog                     очистити буфер логів
        inspect                      підказка, як відкрити DevTools для Chrome на телефоні
        pair <host:port> <код>       бездротове парування (Android 11+)
        connect <host:port>          бездротове підключення
        raw <...>                    будь-яка команда adb як є
#>
param(
    [Parameter(Position = 0)][string]$Command,
    [Parameter(Position = 1, ValueFromRemainingArguments = $true)][string[]]$Args
)

$ErrorActionPreference = 'Stop'

# ------------------------------------------------------------------ пошук adb
function Get-Adb {
    $candidates = @(
        (Join-Path $env:LOCALAPPDATA 'platform-tools\adb.exe'),
        (Join-Path $env:ProgramFiles 'platform-tools\adb.exe'),
        (Join-Path $env:LOCALAPPDATA 'Android\Sdk\platform-tools\adb.exe')
    )
    foreach ($c in $candidates) { if (Test-Path $c) { return $c } }
    $onPath = Get-Command adb -ErrorAction SilentlyContinue
    if ($onPath) { return $onPath.Source }
    throw "adb не знайдено. Запусти спершу: qa-toolkit\android\setup.ps1"
}

$Adb = Get-Adb

function Invoke-Adb { & $Adb @args }

function Assert-Device {
    $lines = (& $Adb devices) -split "`n" | Where-Object { $_ -match "`tdevice$" }
    if (-not $lines) {
        Write-Host ''
        Write-Host 'Пристрій не підключений.' -ForegroundColor Yellow
        Write-Host 'Перевір: кабель у режимі передачі даних, увімкнене "Налагодження USB",'
        Write-Host 'і що на телефоні натиснуто "Дозволити" у вікні запиту відбитка ключа.'
        Write-Host ''
        & $Adb devices
        exit 1
    }
}

function New-OutPath([string]$given, [string]$ext) {
    if ($given) { return $given }
    $dir = Join-Path $PSScriptRoot 'out'
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    return Join-Path $dir ("{0:yyyy-MM-dd_HH-mm-ss}.{1}" -f (Get-Date), $ext)
}

# Витягує файл із телефона на ПК і прибирає за собою.
function Pull-Temp([string]$remote, [string]$local) {
    & $Adb pull $remote $local | Out-Null
    & $Adb shell rm $remote | Out-Null
    return $local
}

$KeyMap = @{
    back = 4; home = 3; enter = 66; tab = 61; del = 67; menu = 82
    power = 26; volup = 24; voldown = 25; search = 84; escape = 111
    up = 19; down = 20; left = 21; right = 22
}

# ------------------------------------------------------------------- команди
switch ($Command) {

    'devices' { & $Adb devices -l; break }

    'info' {
        Assert-Device
        Write-Host ''
        Write-Host 'Модель:   ' (& $Adb shell getprop ro.product.model).Trim()
        Write-Host 'Виробник: ' (& $Adb shell getprop ro.product.manufacturer).Trim()
        Write-Host 'Android:  ' (& $Adb shell getprop ro.build.version.release).Trim()
        Write-Host 'SDK:      ' (& $Adb shell getprop ro.build.version.sdk).Trim()
        Write-Host 'Екран:    ' (& $Adb shell wm size).Trim()
        Write-Host 'Щільність:' (& $Adb shell wm density).Trim()
        Write-Host ''
        break
    }

    'shot' {
        Assert-Device
        $out = New-OutPath $Args[0] 'png'
        & $Adb shell screencap -p /sdcard/_qa_shot.png | Out-Null
        Pull-Temp '/sdcard/_qa_shot.png' $out | Out-Null
        Write-Host "Скріншот: $out" -ForegroundColor Green
        break
    }

    'rec' {
        Assert-Device
        $sec = if ($Args[0]) { [int]$Args[0] } else { 10 }
        $out = New-OutPath $Args[1] 'mp4'
        Write-Host "Пишу $sec с... роби дії на телефоні." -ForegroundColor Cyan
        & $Adb shell screenrecord --time-limit $sec /sdcard/_qa_rec.mp4 | Out-Null
        Start-Sleep -Milliseconds 800   # даємо файлу дописатись
        Pull-Temp '/sdcard/_qa_rec.mp4' $out | Out-Null
        Write-Host "Відео: $out" -ForegroundColor Green
        break
    }

    'tap' {
        Assert-Device
        & $Adb shell input tap $Args[0] $Args[1]
        break
    }

    'swipe' {
        Assert-Device
        $ms = if ($Args[4]) { $Args[4] } else { '300' }
        & $Adb shell input swipe $Args[0] $Args[1] $Args[2] $Args[3] $ms
        break
    }

    'text' {
        Assert-Device
        # adb input text не вміє пробіли й частину спецсимволів — екрануємо
        $t = ($Args -join ' ') -replace ' ', '%s'
        & $Adb shell input text "`"$t`""
        break
    }

    'key' {
        Assert-Device
        $k = $Args[0]
        $code = if ($KeyMap.ContainsKey($k)) { $KeyMap[$k] } else { $k }
        & $Adb shell input keyevent $code
        break
    }

    'open' {
        Assert-Device
        & $Adb shell am start -a android.intent.action.VIEW -d "$($Args[0])" | Out-Null
        Write-Host "Відкрито на телефоні: $($Args[0])" -ForegroundColor Green
        break
    }

    'app' {
        Assert-Device
        & $Adb shell monkey -p $Args[0] -c android.intent.category.LAUNCHER 1 | Out-Null
        Write-Host "Запущено: $($Args[0])" -ForegroundColor Green
        break
    }

    'ui' {
        Assert-Device
        $out = New-OutPath $Args[0] 'xml'
        & $Adb shell uiautomator dump /sdcard/_qa_ui.xml | Out-Null
        Pull-Temp '/sdcard/_qa_ui.xml' $out | Out-Null
        Write-Host "Дерево UI: $out" -ForegroundColor Green
        break
    }

    'audit' {
        Assert-Device
        $xmlPath = New-OutPath $null 'xml'
        & $Adb shell uiautomator dump /sdcard/_qa_ui.xml | Out-Null
        Pull-Temp '/sdcard/_qa_ui.xml' $xmlPath | Out-Null

        $size = (& $Adb shell wm size) -replace '.*:\s*', ''
        $dens = [int](((& $Adb shell wm density) -replace '.*:\s*', '').Trim())
        $wh = $size.Trim() -split 'x'
        $screenW = [int]$wh[0]; $screenH = [int]$wh[1]
        $minPx = [math]::Round(48 * $dens / 160)   # 48dp — мінімум за Material

        Write-Host ''
        Write-Host "Екран ${screenW}x${screenH}, щільність $dens dpi — мінімальний тап = $minPx px (48dp)" -ForegroundColor Cyan
        Write-Host ''

        [xml]$xml = Get-Content -Raw -Encoding UTF8 $xmlPath
        $nodes = $xml.SelectNodes('//node[@clickable="true"]')

        $small = @(); $offscreen = @()
        foreach ($n in $nodes) {
            if ($n.bounds -notmatch '\[(\d+),(\d+)\]\[(\d+),(\d+)\]') { continue }
            $x1 = [int]$Matches[1]; $y1 = [int]$Matches[2]
            $x2 = [int]$Matches[3]; $y2 = [int]$Matches[4]
            $w = $x2 - $x1; $h = $y2 - $y1
            if ($w -le 0 -or $h -le 0) { continue }
            $label = if ($n.text) { $n.text } elseif ($n.'content-desc') { $n.'content-desc' } else { $n.'resource-id' }
            $item = [pscustomobject]@{ Size = "${w}x${h}"; Label = $label; Class = $n.class; Bounds = $n.bounds }
            if ($w -lt $minPx -or $h -lt $minPx) { $small += $item }
            if ($x2 -gt $screenW -or $y2 -gt $screenH -or $x1 -lt 0 -or $y1 -lt 0) { $offscreen += $item }
        }

        Write-Host "Клікабельних елементів: $($nodes.Count)"
        Write-Host ''
        if ($small.Count) {
            Write-Host "Замалі для пальця (< $minPx px): $($small.Count)" -ForegroundColor Yellow
            $small | Format-Table Size, Label, Class -AutoSize
        } else {
            Write-Host 'Замалих тач-таргетів немає.' -ForegroundColor Green
        }
        if ($offscreen.Count) {
            Write-Host "Виходять за межі екрана: $($offscreen.Count)" -ForegroundColor Yellow
            $offscreen | Format-Table Size, Label, Bounds -AutoSize
        }
        Write-Host "Повне дерево: $xmlPath"
        Write-Host ''
        break
    }

    'log' {
        Assert-Device
        if ($Args[0]) { & $Adb logcat -v time | Select-String -Pattern $Args[0] }
        else { & $Adb logcat -v time '*:E' }
        break
    }

    'clearlog' { Assert-Device; & $Adb logcat -c; Write-Host 'Логи очищено.' -ForegroundColor Green; break }

    'inspect' {
        Assert-Device
        Write-Host ''
        Write-Host 'DevTools для Chrome на телефоні:' -ForegroundColor Cyan
        Write-Host '  1. На телефоні відкрий Chrome і потрібну сторінку'
        Write-Host '  2. На ПК у Chrome відкрий:  chrome://inspect/#devices'
        Write-Host '  3. Сторінка зʼявиться у списку — тисни "inspect"'
        Write-Host ''
        Write-Host 'Вкладки, відкриті зараз на телефоні:'
        & $Adb shell dumpsys activity activities | Select-String -Pattern 'taskAffinity|realActivity' | Select-Object -First 10
        Write-Host ''
        break
    }

    'pair'    { & $Adb pair $Args[0] $Args[1]; break }
    'connect' { & $Adb connect $Args[0]; break }
    'raw'     { & $Adb @Args; break }

    default {
        Get-Help $PSCommandPath -Detailed | Out-String | Write-Host
        Write-Host "adb: $Adb" -ForegroundColor DarkGray
    }
}
