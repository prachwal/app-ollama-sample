#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Skrypt do czyszczenia zbędnych plików z projektu Ollama Basic Chat
    
.DESCRIPTION
    Ten skrypt usuwa pliki tymczasowe, cache, logi i inne zbędne pliki
    z projektu zachowując tylko niezbędne pliki źródłowe i konfiguracyjne.
    
.PARAMETER Force
    Wymusza usunięcie bez pytania o potwierdzenie
    
.PARAMETER DryRun
    Pokazuje co zostałoby usunięte bez faktycznego usuwania
    
.EXAMPLE
    .\cleanup.ps1
    .\cleanup.ps1 -Force
    .\cleanup.ps1 -DryRun
    
.NOTES
    Autor: Ollama Testing Team
    Wersja: 1.0.0
#>

param(
    [switch]$Force,
    [switch]$DryRun
)

# Kolory dla lepszej czytelności
$Colors = @{
    Info = 'Cyan'
    Success = 'Green'
    Warning = 'Yellow'
    Error = 'Red'
    Header = 'Magenta'
}

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = 'White'
    )
    
    $consoleColor = 'White'
    if ($Colors.ContainsKey($Color)) {
        $consoleColor = $Colors[$Color]
    }
    
    Write-Host $Message -ForegroundColor $consoleColor
}

function Get-FileSize {
    param([string]$Path)
    if (Test-Path $Path) {
        $size = (Get-ChildItem $Path -Recurse -File | Measure-Object -Property Length -Sum).Sum
        if ($size -gt 1MB) {
            return "{0:N2} MB" -f ($size / 1MB)
        } elseif ($size -gt 1KB) {
            return "{0:N2} KB" -f ($size / 1KB)
        } else {
            return "$size B"
        }
    }
    return "0 B"
}

function Remove-Files {
    param(
        [string[]]$Patterns,
        [string]$Description
    )
    
    Write-ColorOutput "🔍 Szukanie: $Description" 'Info'
    
    $foundFiles = @()
    foreach ($pattern in $Patterns) {
        $files = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue
        if ($files) {
            $foundFiles += $files
        }
    }
    
    if ($foundFiles.Count -eq 0) {
        Write-ColorOutput "   ✅ Brak plików do usunięcia" 'Success'
        return 0
    }
    
    $totalSize = ($foundFiles | Measure-Object -Property Length -Sum).Sum
    $sizeText = Get-FileSize -Path "."
    
    Write-ColorOutput "   📁 Znaleziono: $($foundFiles.Count) plików" 'Warning'
    
    foreach ($file in $foundFiles) {
        $fileSize = if ($file.Length -gt 1MB) { 
            "{0:N2} MB" -f ($file.Length / 1MB)
        } elseif ($file.Length -gt 1KB) {
            "{0:N2} KB" -f ($file.Length / 1KB)  
        } else {
            "$($file.Length) B"
        }
        Write-ColorOutput "      📄 $($file.Name) ($fileSize)" 'Warning'
    }
    
    if ($DryRun) {
        Write-ColorOutput "   🔍 [DRY RUN] Zostałoby usuniętych: $($foundFiles.Count) plików" 'Info'
        return $foundFiles.Count
    }
    
    if (-not $Force) {
        $response = Read-Host "   ❓ Czy usunąć te pliki? [y/N]"
        if ($response -notmatch '^[yY]') {
            Write-ColorOutput "   ⏭️  Pominięto" 'Info'
            return 0
        }
    }
    
    $removedCount = 0
    foreach ($file in $foundFiles) {
        try {
            Remove-Item $file.FullName -Force
            $removedCount++
        } catch {
            Write-ColorOutput "   ❌ Błąd usuwania: $($file.Name) - $($_.Exception.Message)" 'Error'
        }
    }
    
    Write-ColorOutput "   ✅ Usunięto: $removedCount plików" 'Success'
    return $removedCount
}

# Nagłówek
Clear-Host
Write-ColorOutput "🧹 Skrypt czyszczenia projektu Ollama Basic Chat" 'Header'
Write-ColorOutput "=" * 50 'Header'

if ($DryRun) {
    Write-ColorOutput "🔍 TRYB PODGLĄDU - żadne pliki nie zostaną usunięte" 'Info'
    Write-ColorOutput ""
}

# Sprawdź czy jesteśmy w katalogu projektu
if (-not (Test-Path "ollama_basic_chat_gui.py")) {
    Write-ColorOutput "❌ Błąd: Nie znaleziono pliku ollama_basic_chat_gui.py" 'Error'
    Write-ColorOutput "   Upewnij się, że uruchamiasz skrypt z katalogu projektu" 'Error'
    exit 1
}

$totalRemoved = 0
$startTime = Get-Date

# 1. Pliki tymczasowe Python
$totalRemoved += Remove-Files @(
    "*.pyc",
    "**/*.pyc", 
    "__pycache__",
    "**/__pycache__"
) "Pliki cache Python (.pyc, __pycache__)"

# 2. Pliki testów i logów
$totalRemoved += Remove-Files @(
    "*test*.txt",
    "*test*.json", 
    "*test*.md",
    "*test*.csv",
    "chat_*.txt",
    "*.log"
) "Pliki testów i logów"

# 3. Pliki tymczasowe systemu
$totalRemoved += Remove-Files @(
    ".DS_Store",
    "**/.DS_Store",
    "Thumbs.db",
    "**/Thumbs.db", 
    "*.tmp",
    "*.temp"
) "Pliki tymczasowe systemu"

# 4. Pliki IDE/edytorów
$totalRemoved += Remove-Files @(
    ".vscode/settings.json",
    "*.swp",
    "*.swo", 
    "*~"
) "Pliki tymczasowe IDE"

# 5. Pliki backupów
$totalRemoved += Remove-Files @(
    "*.bak",
    "*.backup",
    "*.old"
) "Pliki backupów"

# 6. Pliki wirtualnego środowiska (jeśli istnieją)
if (Test-Path "venv" -PathType Container) {
    Write-ColorOutput "🔍 Szukanie: Środowisko wirtualne Python" 'Info'
    if ($DryRun) {
        Write-ColorOutput "   🔍 [DRY RUN] Zostałby usunięty katalog: venv" 'Info'
    } else {
        if ($Force -or (Read-Host "   ❓ Czy usunąć katalog venv? [y/N]") -match '^[yY]') {
            try {
                Remove-Item "venv" -Recurse -Force
                Write-ColorOutput "   ✅ Usunięto katalog venv" 'Success'
                $totalRemoved += 1
            } catch {
                Write-ColorOutput "   ❌ Błąd usuwania venv: $($_.Exception.Message)" 'Error'
            }
        }
    }
}

# 7. Sprawdź nietypowe pliki Python (duplikaty, wersje rozwojowe)
$pythonFiles = Get-ChildItem "*.py" | Where-Object { 
    $_.Name -match "_old|_backup|_copy|_test|_dev" -or
    $_.Name -match "\d+\.py$" -or  # pliki z numerami
    $_.Name -match "test_.*\.py$"   # pliki testowe
}

if ($pythonFiles) {
    Write-ColorOutput "🔍 Szukanie: Podejrzane pliki Python" 'Info'
    foreach ($file in $pythonFiles) {
        Write-ColorOutput "      📄 $($file.Name)" 'Warning'
    }
    
    if ($DryRun) {
        Write-ColorOutput "   🔍 [DRY RUN] Zostałoby usuniętych: $($pythonFiles.Count) plików Python" 'Info'
    } else {
        if ($Force -or (Read-Host "   ❓ Czy usunąć te pliki Python? [y/N]") -match '^[yY]') {
            foreach ($file in $pythonFiles) {
                try {
                    Remove-Item $file.FullName -Force
                    $totalRemoved++
                    Write-ColorOutput "      ✅ Usunięto: $($file.Name)" 'Success'
                } catch {
                    Write-ColorOutput "      ❌ Błąd: $($file.Name)" 'Error'
                }
            }
        }
    }
}

# Podsumowanie
$endTime = Get-Date
$duration = ($endTime - $startTime).TotalSeconds

Write-ColorOutput "" 
Write-ColorOutput "📊 PODSUMOWANIE:" 'Header'
Write-ColorOutput "=" * 20 'Header'

if ($DryRun) {
    Write-ColorOutput "🔍 Tryb podglądu - pliki do usunięcia: $totalRemoved" 'Info'
} else {
    Write-ColorOutput "✅ Usunięto plików: $totalRemoved" 'Success'
}

Write-ColorOutput "⏱️  Czas wykonania: $([math]::Round($duration, 2)) sekund" 'Info'

# Pokaż pozostałe pliki
Write-ColorOutput ""
Write-ColorOutput "📁 Pozostałe pliki w projekcie:" 'Info'
$remainingFiles = Get-ChildItem -File | Sort-Object Name
foreach ($file in $remainingFiles) {
    $size = Get-FileSize -Path $file.FullName
    Write-ColorOutput "   📄 $($file.Name) ($size)" 'Info'
}

$totalSize = Get-FileSize -Path "."
Write-ColorOutput ""
Write-ColorOutput "📦 Całkowity rozmiar projektu: $totalSize" 'Success'

if ($totalRemoved -gt 0 -and -not $DryRun) {
    Write-ColorOutput "🎉 Czyszczenie zakończone pomyślnie!" 'Success'
} elseif ($DryRun) {
    Write-ColorOutput "🔍 Podgląd zakończony. Użyj bez -DryRun aby wykonać czyszczenie." 'Info'
} else {
    Write-ColorOutput "✨ Projekt już jest czysty!" 'Success'
}

Write-ColorOutput ""
