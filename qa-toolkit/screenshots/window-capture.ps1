<#
    qa-toolkit/screenshots/window-capture.ps1

    Скріншот вікна браузера РАЗОМ з його інтерфейсом — панеллю вкладок,
    адресним рядком, рамкою вікна. Потрібен там, де доказ має показувати,
    у якому саме браузері перевірено: Chrome, Opera, Edge, Firefox.

    Ні Claude in Chrome, ні Playwright так не вміють — вони віддають лише
    вміст вкладки. Тут захват іде на рівні ОС через user32!PrintWindow,
    тому вікно не обовʼязково має бути на передньому плані.

    Запуск:
        powershell -ExecutionPolicy Bypass -File qa-toolkit\screenshots\window-capture.ps1 <команда> [ціль] [опції]

    Команди:
        list                      усі відкриті вікна (браузери — першими)
        shot <ціль>               зняти одне вікно
        all                       зняти по одному вікну кожного відкритого браузера

    Ціль — псевдонім браузера (chrome, opera, edge, firefox, brave, vivaldi)
    або будь-який шматок заголовка вікна ("Jira", "Foxtrot").

    Опції:
        -Task CMS-1234    покласти у qa-toolkit\tasks\CMS-1234\browsers\
        -Dir <папка>      покласти у вказану папку (за замовчуванням — поточна)
        -Out <файл.png>   конкретне імʼя файлу (тільки для shot)
        -Crop L,T,R,B     обрізати краї, px (напр. -Crop 0,0,0,200 — прибрати низ вікна).
                          Панель закладок обрізанням не прибрати — вона всередині,
                          між адресним рядком і сторінкою: ховай її в браузері (Ctrl+Shift+B)
        -Restore          розгорнути згорнуте вікно перед захватом
        -Screen           знімати з екрана (вікно виводиться на передній план) —
                          запасний шлях, якщо PrintWindow дав чорний кадр

    Приклади:
        ... window-capture.ps1 list
        ... window-capture.ps1 shot chrome -Task CMS-27643
        ... window-capture.ps1 shot "Foxtrot" -Out listing-opera.png
        ... window-capture.ps1 all -Task CMS-27643

    У кадр потрапляє все вікно — інші вкладки, панель закладок. Перед тим як
    класти скріншот у звіт, що йде в задачу, прибери зайве через -Crop.
    Номер задачі зверху не дописуємо — див. CLAUDE.md.
#>
param(
    [Parameter(Position = 0)][ValidateSet('list', 'shot', 'all')][string]$Command = 'list',
    [Parameter(Position = 1)][string]$Target,
    [string]$Task,
    [string]$Dir,
    [string]$Out,
    [string]$Crop,
    [switch]$Restore,
    [switch]$Screen
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

# ------------------------------------------------------------------ WinAPI
if (-not ('QaWin' -as [type])) {
    Add-Type -TypeDefinition @"
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;

public class QaWin {
    public struct RECT { public int Left, Top, Right, Bottom; }

    private delegate bool EnumProc(IntPtr hWnd, IntPtr lParam);

    [DllImport("user32.dll")] private static extern bool EnumWindows(EnumProc cb, IntPtr p);
    [DllImport("user32.dll")] private static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll")] private static extern int GetWindowTextLength(IntPtr h);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] private static extern int GetWindowText(IntPtr h, StringBuilder s, int max);
    [DllImport("user32.dll")] private static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);

    [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr h);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr hdc, uint flags);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
    [DllImport("dwmapi.dll")] public static extern int DwmGetWindowAttribute(IntPtr h, int attr, out RECT r, int size);

    public static List<object[]> Top() {
        List<object[]> found = new List<object[]>();
        EnumWindows(delegate(IntPtr h, IntPtr p) {
            if (!IsWindowVisible(h)) return true;
            int len = GetWindowTextLength(h);
            if (len == 0) return true;
            StringBuilder sb = new StringBuilder(len + 1);
            GetWindowText(h, sb, sb.Capacity);
            uint pid; GetWindowThreadProcessId(h, out pid);
            found.Add(new object[] { h, (int)pid, sb.ToString() });
            return true;
        }, IntPtr.Zero);
        return found;
    }
}
"@
}

$SW_RESTORE = 9
$DWMWA_EXTENDED_FRAME_BOUNDS = 9

# ---------------------------------------------------------------- браузери
$Browsers = [ordered]@{
    chrome  = @{ Label = 'Google Chrome';   Proc = @('chrome') }
    opera   = @{ Label = 'Opera';           Proc = @('opera', 'opera_gx') }
    edge    = @{ Label = 'Microsoft Edge';  Proc = @('msedge') }
    firefox = @{ Label = 'Mozilla Firefox'; Proc = @('firefox') }
    brave   = @{ Label = 'Brave';           Proc = @('brave') }
    vivaldi = @{ Label = 'Vivaldi';         Proc = @('vivaldi') }
}

function Get-Windows {
    $procs = @{}
    foreach ($p in Get-Process) { $procs[[int]$p.Id] = $p }

    $list = @()
    foreach ($w in [QaWin]::Top()) {
        $handle = [IntPtr]$w[0]
        $processId = [int]$w[1]
        $title = [string]$w[2]
        $proc = $procs[$processId]
        if (-not $proc) { continue }
        $name = $proc.ProcessName.ToLower()

        $alias = $null
        foreach ($key in $Browsers.Keys) {
            if ($Browsers[$key].Proc -contains $name) { $alias = $key; break }
        }

        $rect = New-Object QaWin+RECT
        [void][QaWin]::GetWindowRect($handle, [ref]$rect)
        $width = $rect.Right - $rect.Left
        $height = $rect.Bottom - $rect.Top
        if ($width -lt 200 -or $height -lt 200) { continue }

        $version = $null
        try { $version = $proc.MainModule.FileVersionInfo.ProductVersion } catch { }

        $label = if ($alias) { $Browsers[$alias].Label } else { $proc.ProcessName }

        $list += [pscustomobject]@{
            Handle    = $handle
            ProcId    = $processId
            Process   = $proc.ProcessName
            Alias     = $alias
            Label     = $label
            Version   = $version
            Title     = $title
            Width     = $width
            Height    = $height
            Minimized = [QaWin]::IsIconic($handle)
        }
    }

    # браузери першими, всередині — більші вікна вище
    $list | Sort-Object @{ Expression = { if ($_.Alias) { 0 } else { 1 } } }, @{ Expression = { - ($_.Width * $_.Height) } }
}

function Resolve-Window {
    param([string]$Query)

    $all = Get-Windows
    if (-not $Query) {
        $first = $all | Where-Object { $_.Alias } | Select-Object -First 1
        if (-not $first) { throw 'Не знайдено жодного вікна браузера. Відкрий браузер або вкажи ціль явно.' }
        return $first
    }

    $key = $Query.ToLower()
    if ($Browsers.Contains($key)) {
        $hit = $all | Where-Object { $_.Alias -eq $key } | Select-Object -First 1
        if (-not $hit) { throw "Вікно '$($Browsers[$key].Label)' не відкрите. Запусти браузер і повтори." }
        return $hit
    }

    $hit = $all | Where-Object { $_.Title -like "*$Query*" } | Select-Object -First 1
    if (-not $hit) { throw "Вікно із заголовком '*$Query*' не знайдено. Подивись список: window-capture.ps1 list" }
    return $hit
}

function Get-TargetDir {
    if ($Task) {
        $root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
        $path = Join-Path $root "qa-toolkit\tasks\$Task\browsers"
    }
    elseif ($Dir) { $path = $Dir }
    else { $path = (Get-Location).Path }

    if (-not (Test-Path $path)) { New-Item -ItemType Directory -Path $path -Force | Out-Null }
    return (Resolve-Path $path).Path
}

function Test-MostlyBlack {
    param([System.Drawing.Bitmap]$Bitmap)

    $lit = 0
    $steps = 24
    for ($i = 1; $i -lt $steps; $i++) {
        for ($j = 1; $j -lt $steps; $j++) {
            $x = [int]($Bitmap.Width * $i / $steps)
            $y = [int]($Bitmap.Height * $j / $steps)
            $c = $Bitmap.GetPixel($x, $y)
            if ($c.R + $c.G + $c.B -gt 24) { $lit++ }
        }
    }
    return ($lit -lt (($steps - 1) * ($steps - 1) * 0.02))
}

function Save-Window {
    param([pscustomobject]$Window, [string]$Path)

    if ($Window.Minimized) {
        if ($Restore) {
            [void][QaWin]::ShowWindow($Window.Handle, $SW_RESTORE)
            Start-Sleep -Milliseconds 700
        }
        else {
            throw "Вікно '$($Window.Title)' згорнуте — у кадрі буде порожньо. Розгорни його або додай -Restore."
        }
    }

    $win = New-Object QaWin+RECT
    [void][QaWin]::GetWindowRect($Window.Handle, [ref]$win)
    $width = $win.Right - $win.Left
    $height = $win.Bottom - $win.Top

    # видима рамка без невидимих полів зміни розміру
    $dwm = New-Object QaWin+RECT
    $insetL = 0; $insetT = 0; $insetR = 0; $insetB = 0
    if ([QaWin]::DwmGetWindowAttribute($Window.Handle, $DWMWA_EXTENDED_FRAME_BOUNDS, [ref]$dwm, 16) -eq 0) {
        $insetL = [Math]::Max(0, $dwm.Left - $win.Left)
        $insetT = [Math]::Max(0, $dwm.Top - $win.Top)
        $insetR = [Math]::Max(0, $win.Right - $dwm.Right)
        $insetB = [Math]::Max(0, $win.Bottom - $dwm.Bottom)
    }

    $bmp = New-Object System.Drawing.Bitmap($width, $height)
    $gfx = [System.Drawing.Graphics]::FromImage($bmp)

    if ($Screen) {
        [void][QaWin]::SetForegroundWindow($Window.Handle)
        Start-Sleep -Milliseconds 500
        $gfx.CopyFromScreen($win.Left, $win.Top, 0, 0, (New-Object System.Drawing.Size($width, $height)))
    }
    else {
        $hdc = $gfx.GetHdc()
        # PW_RENDERFULLCONTENT = 2 — знімає навіть перекрите вікно
        [void][QaWin]::PrintWindow($Window.Handle, $hdc, 2)
        $gfx.ReleaseHdc($hdc)
    }
    $gfx.Dispose()

    if (-not $Screen -and (Test-MostlyBlack -Bitmap $bmp)) {
        $bmp.Dispose()
        throw "PrintWindow повернув чорний кадр для '$($Window.Title)'. Повтори з -Screen (вікно вийде на передній план)."
    }

    $cropL = $insetL; $cropT = $insetT; $cropR = $insetR; $cropB = $insetB
    if ($Crop) {
        # через -File аргумент приходить одним рядком, тому розбираємо самі
        $parts = @($Crop -split '[,\s]+' | Where-Object { $_ -ne '' })
        if ($parts.Count -ne 4) { $bmp.Dispose(); throw '-Crop очікує чотири числа: L,T,R,B (напр. -Crop 0,95,0,0)' }
        $insets = @($parts | ForEach-Object { [int]$_ })
        $cropL += $insets[0]; $cropT += $insets[1]; $cropR += $insets[2]; $cropB += $insets[3]
    }

    $finalW = $width - $cropL - $cropR
    $finalH = $height - $cropT - $cropB
    if ($finalW -lt 50 -or $finalH -lt 50) {
        $bmp.Dispose()
        throw "Після -Crop лишилось ${finalW}x${finalH} — обрізано забагато."
    }

    $rect = New-Object System.Drawing.Rectangle($cropL, $cropT, $finalW, $finalH)
    $cut = $bmp.Clone($rect, $bmp.PixelFormat)
    $cut.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png)
    $cut.Dispose()
    $bmp.Dispose()

    return [pscustomobject]@{
        File    = $Path
        Browser = $Window.Label
        Version = $Window.Version
        Title   = $Window.Title
        Size    = "${finalW}x${finalH}"
    }
}

function New-Name {
    param([pscustomobject]$Window)
    $base = if ($Window.Alias) { $Window.Alias } else { ($Window.Process -replace '[^\w\-]', '_') }
    return "$base-$(Get-Date -Format 'yyyyMMdd-HHmmss').png"
}

# ----------------------------------------------------------------- команди
switch ($Command) {

    'list' {
        $all = Get-Windows
        Write-Host ''
        Write-Host '  Браузери' -ForegroundColor Cyan
        $browsers = $all | Where-Object { $_.Alias }
        if (-not $browsers) { Write-Host '    (жодного відкритого)' -ForegroundColor DarkGray }
        foreach ($w in $browsers) {
            $flag = if ($w.Minimized) { ' [згорнуте]' } else { '' }
            Write-Host ('    {0,-8} {1,-16} {2,9}  {3}{4}' -f $w.Alias, $w.Label, "$($w.Width)x$($w.Height)", $w.Title, $flag)
            if ($w.Version) { Write-Host ('             версія {0}' -f $w.Version) -ForegroundColor DarkGray }
        }
        Write-Host ''
        Write-Host '  Інші вікна' -ForegroundColor Cyan
        foreach ($w in ($all | Where-Object { -not $_.Alias } | Select-Object -First 15)) {
            Write-Host ('    {0,-24} {1,9}  {2}' -f $w.Process, "$($w.Width)x$($w.Height)", $w.Title) -ForegroundColor DarkGray
        }
        Write-Host ''
    }

    'shot' {
        $window = Resolve-Window -Query $Target
        $dir = Get-TargetDir
        $name = if ($Out) { $Out } else { New-Name -Window $window }
        $path = if ([System.IO.Path]::IsPathRooted($name)) { $name } else { Join-Path $dir $name }

        $result = Save-Window -Window $window -Path $path
        $version = if ($result.Version) { " $($result.Version)" } else { '' }
        Write-Host ''
        Write-Host ('  {0}{1}' -f $result.Browser, $version) -ForegroundColor Green
        Write-Host ('  {0}' -f $result.Title) -ForegroundColor DarkGray
        Write-Host ('  {0}  {1}' -f $result.Size, $result.File)
        Write-Host ''
    }

    'all' {
        $dir = Get-TargetDir
        $seen = @{}
        $results = @()
        foreach ($w in (Get-Windows | Where-Object { $_.Alias })) {
            if ($seen[$w.Alias]) { continue }
            $seen[$w.Alias] = $true
            $path = Join-Path $dir "$($w.Alias).png"
            try {
                $results += Save-Window -Window $w -Path $path
                Write-Host ('  OK         {0,-16} {1}' -f $w.Label, $path) -ForegroundColor Green
            }
            catch {
                Write-Host ('  ПРОПУЩЕНО  {0,-16} {1}' -f $w.Label, $_.Exception.Message) -ForegroundColor Yellow
            }
        }

        if ($results.Count -eq 0) {
            throw 'Жодного вікна браузера не знято. Перевір список: window-capture.ps1 list'
        }

        $meta = Join-Path $dir 'browsers.json'
        ConvertTo-Json -InputObject @($results) -Depth 4 | Set-Content -Path $meta -Encoding UTF8
        Write-Host ''
        Write-Host "  Знято: $($results.Count). Перелік з версіями — $meta"
        Write-Host ''
    }
}
