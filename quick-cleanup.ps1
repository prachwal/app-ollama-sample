# Quick cleanup script - prosty skrypt czyszczenia
# Szybko usuwa najczęstsze śmieci z projektu

Write-Host "🧹 Szybkie czyszczenie projektu..." -ForegroundColor Cyan

$removed = 0

# Cache Python
$pyCache = Get-ChildItem -Path "*.pyc", "**/*.pyc", "__pycache__", "**/__pycache__" -ErrorAction SilentlyContinue
if ($pyCache) {
    $pyCache | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    $removed += $pyCache.Count
    Write-Host "✅ Usunięto cache Python: $($pyCache.Count) elementów" -ForegroundColor Green
}

# Pliki testów
$testFiles = Get-ChildItem -Path "*test*.txt", "*test*.json", "chat_*.txt" -ErrorAction SilentlyContinue
if ($testFiles) {
    $testFiles | Remove-Item -Force -ErrorAction SilentlyContinue
    $removed += $testFiles.Count
    Write-Host "✅ Usunięto pliki testów: $($testFiles.Count) plików" -ForegroundColor Green
}

# Pliki tymczasowe
$tempFiles = Get-ChildItem -Path "*.tmp", "*.temp", ".DS_Store", "Thumbs.db" -ErrorAction SilentlyContinue
if ($tempFiles) {
    $tempFiles | Remove-Item -Force -ErrorAction SilentlyContinue  
    $removed += $tempFiles.Count
    Write-Host "✅ Usunięto pliki tymczasowe: $($tempFiles.Count) plików" -ForegroundColor Green
}

if ($removed -eq 0) {
    Write-Host "✨ Projekt już jest czysty!" -ForegroundColor Yellow
} else {
    Write-Host "🎉 Zakończono! Usunięto łącznie: $removed elementów" -ForegroundColor Green
}

# Pokaż rozmiar projektu
$totalSize = (Get-ChildItem -File -Recurse | Measure-Object -Property Length -Sum).Sum
$sizeText = if ($totalSize -gt 1MB) { 
    "{0:N2} MB" -f ($totalSize / 1MB)
} else { 
    "{0:N2} KB" -f ($totalSize / 1KB)
}
Write-Host "📦 Rozmiar projektu: $sizeText" -ForegroundColor Cyan
