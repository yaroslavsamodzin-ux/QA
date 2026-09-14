# vpn-mtu-restore.ps1 - повертає MTU VPN-адаптера до стандартного значення (скасовує vpn-mtu-fix.ps1).
# ЗАПУСКАТИ ВІД ІМЕНІ АДМІНІСТРАТОРА.
#
#   .\vpn-mtu-restore.ps1              -> повертає MTU=1500 (стандарт Ethernet)
#   .\vpn-mtu-restore.ps1 -Mtu 1400    -> повертає конкретне значення
#   .\vpn-mtu-restore.ps1 -All         -> повертає 1500 на ВСІХ IPv4-інтерфейсах, де MTU інший

param(
  [int]$Mtu = 1500,
  [string]$Iface = "Ethernet 2",
  [switch]$All
)

chcp 65001 > $null

$p = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
  Write-Host "ПОТРІБНІ ПРАВА АДМІНІСТРАТОРА. Відкрий PowerShell через 'Запуск від імені адміністратора'." -ForegroundColor Red
  exit 1
}

$url = "http://foxtrot01-stage-kibana.foxtrot.local/login"

function Test-Http {
  try {
    $r = Invoke-WebRequest $url -UseBasicParsing -TimeoutSec 20
    return "OK ($($r.Content.Length) байт)"
  } catch { return "FAIL ($($_.Exception.Message))" }
}

function Restore-Mtu($name, $target) {
  $cur = (Get-NetIPInterface -InterfaceAlias $name -AddressFamily IPv4 -ErrorAction SilentlyContinue).NlMtu
  if ($null -eq $cur) {
    Write-Host "Інтерфейс '$name' не знайдено (VPN вимкнений?)." -ForegroundColor Yellow
    return
  }
  if ($cur -eq $target) {
    Write-Host "'$name': MTU вже $target - міняти нічого не треба." -ForegroundColor Green
    return
  }

  Write-Host "'$name': $cur -> $target ..." -NoNewline
  netsh interface ipv4 set subinterface "$name" mtu=$target store=persistent | Out-Null
  Start-Sleep -Seconds 2

  $new = (Get-NetIPInterface -InterfaceAlias $name -AddressFamily IPv4 -ErrorAction SilentlyContinue).NlMtu
  if ($new -eq $target) {
    Write-Host " OK (зараз $new)" -ForegroundColor Green
  } else {
    Write-Host " НЕ ЗАСТОСУВАЛОСЬ (зараз $new)" -ForegroundColor Red
  }
}

Write-Host "MTU до відкату:"
Get-NetIPInterface -AddressFamily IPv4 | Sort-Object InterfaceAlias |
  Format-Table InterfaceAlias, NlMtu, ConnectionState -AutoSize | Out-String | Write-Host

if ($All) {
  # loopback має NlMtu 4294967295 - його чіпати не можна, тому відсікаємо і його, і будь-які
  # нереалістичні значення
  $targets = (Get-NetIPInterface -AddressFamily IPv4 | Where-Object {
                $_.NlMtu -ne $Mtu -and $_.NlMtu -le 9000 -and $_.InterfaceAlias -notlike "Loopback*"
              }).InterfaceAlias | Select-Object -Unique
  if (-not $targets) {
    Write-Host "Усі IPv4-інтерфейси вже на MTU=$Mtu." -ForegroundColor Green
  } else {
    foreach ($t in $targets) { Restore-Mtu $t $Mtu }
  }
} else {
  Restore-Mtu $Iface $Mtu
}

Write-Host "`nMTU після відкату:"
Get-NetIPInterface -AddressFamily IPv4 | Sort-Object InterfaceAlias |
  Format-Table InterfaceAlias, NlMtu, ConnectionState -AutoSize | Out-String | Write-Host

Write-Host "Перевірка HTTP на $url ..." -NoNewline
Write-Host " $(Test-Http)"
Write-Host "`n(FAIL тут - очікувано: ми щойно прибрали обхідний MTU. Щоб повернути фікс - запусти vpn-mtu-fix.ps1)" -ForegroundColor DarkGray
