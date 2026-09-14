# vpn-diag.ps1 - знімок стану VPN/мережі.
# ВАЖЛИВО: перед кожним запуском зроби у AnyConnect Disconnect -> Connect,
# інакше IKEv2/MOBIKE перенесе стару сесію і порівняння буде недійсним.
# Використання:  powershell -ExecutionPolicy Bypass -File vpn-diag.ps1 wifi
param([string]$Label = "run")

chcp 65001 > $null
$out = Join-Path $PSScriptRoot "vpn-diag-$Label.txt"
$sb = [System.Text.StringBuilder]::new()
function W($t) { [void]$sb.AppendLine($t); Write-Host $t }

W "===== $Label | $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ====="

W "`n--- AnyConnect stats (Duration має бути малий = свіжий реконект!) ---"
$cli = @(
  "C:\Program Files (x86)\Cisco\Cisco AnyConnect Secure Mobility Client\vpncli.exe",
  "C:\Program Files (x86)\Cisco\Cisco Secure Client\vpncli.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1
if ($cli) {
  & $cli stats 2>&1 | Select-String -Pattern "Protocol|Cipher|Tunnel Mode|Client Address|Server Address|Duration|Lost|MTU" |
    ForEach-Object { W "    $_" }
} else { W "    vpncli.exe не знайдено" }

W "`n--- Локальна мережа ---"
Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.254.*" } |
  ForEach-Object { W ("    {0,-16} {1}/{2}" -f $_.InterfaceAlias, $_.IPAddress, $_.PrefixLength) }
try { W ("    Публічна IP: " + (Invoke-WebRequest "https://api.ipify.org" -UseBasicParsing -TimeoutSec 10).Content) } catch { W "    Публічна IP: н/д" }

W "`n--- Маршрути RFC1918 (дублікати = конфлікт) ---"
Get-NetRoute -AddressFamily IPv4 | Where-Object { $_.DestinationPrefix -match '^(10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.)' } |
  Sort-Object DestinationPrefix |
  ForEach-Object { W ("    {0,-20} via {1,-15} {2,-14} metric {3}" -f $_.DestinationPrefix, $_.NextHop, $_.InterfaceAlias, ($_.RouteMetric + $_.InterfaceMetric)) }

W "`n--- DNS ---"
foreach ($h in "foxtrot01-stage-kibana.foxtrot.local","jira.entri.com.ua","foxtrot01-dev-dyn-kibana-g.foxtrot.cloud") {
  try { $ip = (Resolve-DnsName $h -Type A -ErrorAction Stop | Where-Object {$_.IPAddress}).IPAddress -join "," } catch { $ip = "DNS FAIL" }
  W "    $h -> $ip"
}

W "`n--- Доступність (TCP) ---"
$targets = @(
  @{n="AD/DNS        10.128.1.3";  h="10.128.1.3";  p=53},
  @{n="Jira          10.128.60.5"; h="10.128.60.5"; p=443},
  @{n="Kibana STAGE  10.5.2.252";  h="10.5.2.252";  p=80},
  @{n="Kibana STAGE  by name";     h="foxtrot01-stage-kibana.foxtrot.local"; p=80},
  @{n="Kibana dev-dyn 10.5.2.230"; h="10.5.2.230";  p=80}
)
foreach ($t in $targets) {
  $r = Test-NetConnection -ComputerName $t.h -Port $t.p -WarningAction SilentlyContinue
  W ("    {0,-28} :{1,-5} -> {2}" -f $t.n, $t.p, $(if ($r.TcpTestSucceeded) {"OK"} else {"FAIL"}))
}

W "`n--- HTTP-відповідь від робочої Kibana ---"
try {
  $resp = Invoke-WebRequest "http://foxtrot01-stage-kibana.foxtrot.local/login" -UseBasicParsing -TimeoutSec 20 -MaximumRedirection 3
  W "    HTTP $($resp.StatusCode), довжина $($resp.Content.Length) байт -> ПРАЦЮЄ"
} catch { W "    ПОМИЛКА: $($_.Exception.Message)" }

W "`n--- Path MTU до VPN-шлюзу 195.135.197.250 ---"
foreach ($sz in 1372,1422,1472) {
  $o = ping -n 1 -f -l $sz 195.135.197.250 2>&1 | Out-String
  $res = if ($o -match "TTL=") {"OK"} elseif ($o -match "fragment|Packet needs") {"TOO BIG"} else {"no reply"}
  W "    payload $sz -> $res"
}

$sb.ToString() | Out-File -FilePath $out -Encoding utf8
Write-Host "`nЗбережено у: $out"
