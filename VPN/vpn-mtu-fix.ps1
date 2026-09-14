# vpn-mtu-fix.ps1 - підбирає робочий MTU для VPN-адаптера і перевіряє реальним HTTP-запитом.
# ЗАПУСКАТИ ВІД ІМЕНІ АДМІНІСТРАТОРА, при активному VPN.
chcp 65001 > $null

$p = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
  Write-Host "ПОТРІБНІ ПРАВА АДМІНІСТРАТОРА. Відкрий PowerShell через 'Запуск від імені адміністратора'." -ForegroundColor Red
  exit 1
}

$iface = "Ethernet 2"          # VPN-адаптер Cisco AnyConnect
$url   = "http://foxtrot01-stage-kibana.foxtrot.local/login"
$orig  = (Get-NetIPInterface -InterfaceAlias $iface -AddressFamily IPv4).NlMtu
Write-Host "Поточний MTU на '$iface': $orig`n"

function Test-Http {
  try {
    $r = Invoke-WebRequest $url -UseBasicParsing -TimeoutSec 20
    return "OK ($($r.Content.Length) байт)"
  } catch { return "FAIL ($($_.Exception.Message))" }
}

Write-Host "Базова перевірка на MTU=$orig ..." -NoNewline
Write-Host " $(Test-Http)"

$works = $null
foreach ($m in 1400,1350,1300,1250,1200,1100) {
  Write-Host "`nСтавлю MTU=$m ..." -NoNewline
  netsh interface ipv4 set subinterface "$iface" mtu=$m store=persistent | Out-Null
  Start-Sleep -Seconds 2
  $res = Test-Http
  Write-Host " $res"
  if ($res -like "OK*") { $works = $m; break }
}

Write-Host ""
if ($works) {
  Write-Host "ЗНАЙДЕНО РОБОЧИЙ MTU: $works" -ForegroundColor Green
  Write-Host "Закріплено командою:"
  Write-Host "  netsh interface ipv4 set subinterface `"$iface`" mtu=$works store=persistent"
  Write-Host "`nУВАГА: AnyConnect може скинути це значення при перепідключенні VPN."
  Write-Host "Якщо проблема повернеться - просто запусти цей скрипт знову."
} else {
  Write-Host "Жодне значення не допомогло - справа не в MTU. Повертаю $orig" -ForegroundColor Yellow
  netsh interface ipv4 set subinterface "$iface" mtu=$orig store=persistent | Out-Null
}
