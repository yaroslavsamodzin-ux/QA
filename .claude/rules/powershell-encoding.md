---
paths:
  - "qa-toolkit/**/*.ps1"
  - "**/*.ps1"
---

# PowerShell-скрипти: UTF-8 **з BOM**

Windows PowerShell 5.1 без BOM читає кирилицю як ANSI і падає з `ParserError`
та абракадаброю в повідомленні. Тому кожен `.ps1` у репо зберігається в UTF-8
з BOM — і після будь-якого редагування це треба відновити.

Перезбереження після правки:

```powershell
$p = "qa-toolkit\android\adb.ps1"
$c = Get-Content -Raw -Encoding UTF8 $p
[System.IO.File]::WriteAllText($p, $c, (New-Object System.Text.UTF8Encoding $true))
```

Перевірка, що BOM на місці (перші три байти — `EF BB BF`):

```bash
head -c 3 qa-toolkit/android/adb.ps1 | od -An -tx1
```

Якщо BOM зник — це не «дивна помилка PowerShell», а саме цей випадок.
