# ExamPilot Shortcut Installation Script
# GT InnoX LLP

$wsh = New-Object -ComObject WScript.Shell

$desktopDir = [Environment]::GetFolderPath("Desktop")
$startMenuDir = [System.IO.Path]::Combine([Environment]::GetFolderPath("StartMenu"), "Programs")
$installRoot = Split-Path -Parent $PSScriptRoot

$targetExe = Join-Path $installRoot "dist\ExamPilot\ExamPilot.exe"
$iconFile = Join-Path $installRoot "assets\icons\app_icon.ico"

$canRunExe = $false
if (Test-Path $targetExe) {
    try {
        $p = Start-Process -FilePath $targetExe -ArgumentList "--version" -PassThru -WindowStyle Hidden -ErrorAction Stop
        Start-Sleep -Milliseconds 300
        if (-not $p.HasExited -or $p.ExitCode -eq 0) {
            $canRunExe = $true
        }
        if (-not $p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
    } catch {
        $canRunExe = $false
    }
}

if ($canRunExe) {
    Write-Host "[*] Using verified standalone executable: $targetExe"
    $targetPath = $targetExe
    $arguments = ""
    $workingDir = Join-Path $installRoot "dist\ExamPilot"
} else {
    Write-Host "[*] Executable blocked by system Device Guard policy; using signed Python runtime launcher"
    $targetPath = "pythonw.exe"
    $arguments = '"' + (Join-Path $installRoot "desktop\main.py") + '"'
    $workingDir = $installRoot
}

# 1. Desktop Shortcut
$desktopShortcut = $wsh.CreateShortcut((Join-Path $desktopDir "ExamPilot.lnk"))
$desktopShortcut.TargetPath = $targetPath
if ($arguments) { $desktopShortcut.Arguments = $arguments }
$desktopShortcut.WorkingDirectory = $workingDir
$desktopShortcut.IconLocation = "$iconFile,0"
$desktopShortcut.Description = "ExamPilot - Understand Questions. Learn the Answers."
$desktopShortcut.Save()
Write-Host "[OK] Desktop shortcut created at: $(Join-Path $desktopDir 'ExamPilot.lnk')"

# 2. Start Menu Shortcut
$startMenuShortcut = $wsh.CreateShortcut((Join-Path $startMenuDir "ExamPilot.lnk"))
$startMenuShortcut.TargetPath = $targetPath
if ($arguments) { $startMenuShortcut.Arguments = $arguments }
$startMenuShortcut.WorkingDirectory = $workingDir
$startMenuShortcut.IconLocation = "$iconFile,0"
$startMenuShortcut.Description = "ExamPilot - Understand Questions. Learn the Answers."
$startMenuShortcut.Save()
Write-Host "[OK] Start Menu shortcut created at: $(Join-Path $startMenuDir 'ExamPilot.lnk')"
