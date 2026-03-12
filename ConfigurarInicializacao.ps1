# ========================================
# Configurar Inicializacao Automatica do Servidor
# ========================================

$ps1Path = "C:\Users\fbznn\Documents\reconhecimento_facial\IniciarServidorInteligente.ps1"
$batPath = "C:\Users\fbznn\Documents\reconhecimento_facial\IniciarServidor.bat"
$startupPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
$shortcutPath = "$startupPath\ServidorReconhecimentoFacial.lnk"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CONFIGURAR INICIALIZACAO AUTOMATICA" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Escolha o modo de inicializacao:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1 - Script Inteligente (PowerShell)" -ForegroundColor White
Write-Host "    + Detecta IP automaticamente" -ForegroundColor Gray
Write-Host "    + Atualiza config.ini com IP correto" -ForegroundColor Gray
Write-Host "    + Atualiza Django ALLOWED_HOSTS" -ForegroundColor Gray
Write-Host "    + Cria arquivo SERVER_INFO.txt" -ForegroundColor Gray
Write-Host ""
Write-Host "2 - Script Simples (BAT)" -ForegroundColor White
Write-Host "    + Mais rapido" -ForegroundColor Gray
Write-Host "    + Detecta e mostra IP" -ForegroundColor Gray
Write-Host ""
$choice = Read-Host "Opcao (1 ou 2)"

if ($choice -eq "1") {
    $targetPath = "powershell.exe"
    $arguments = "-ExecutionPolicy Bypass -WindowStyle Minimized -File `"$ps1Path`""
    $description = "Inicia o servidor Django com deteccao automatica de IP"
    $scriptName = "IniciarServidorInteligente.ps1"
    Write-Host "`nUsando: Script Inteligente PowerShell" -ForegroundColor Green
} else {
    $targetPath = $batPath
    $arguments = ""
    $description = "Inicia o servidor Django de Reconhecimento Facial"
    $scriptName = "IniciarServidor.bat"
    Write-Host "`nUsando: Script BAT Simples" -ForegroundColor Green
}

# Remover atalho existente
if (Test-Path $shortcutPath) {
    Remove-Item $shortcutPath -Force
    Write-Host "Atalho anterior removido" -ForegroundColor Gray
}

# Criar atalho
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = $targetPath
$Shortcut.Arguments = $arguments
$Shortcut.WorkingDirectory = "C:\Users\fbznn\Documents\reconhecimento_facial"
$Shortcut.WindowStyle = 7  # Minimizado
$Shortcut.Description = $description
$Shortcut.Save()

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  CONFIGURACAO CONCLUIDA!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nAtalho criado em:" -ForegroundColor Yellow
Write-Host "  $shortcutPath" -ForegroundColor Gray

Write-Host "`nProxima vez que fizer login:" -ForegroundColor Yellow
Write-Host "  -> Servidor inicia automaticamente (minimizado)" -ForegroundColor White

Write-Host "`nPara testar agora:" -ForegroundColor Yellow
Write-Host "  -> Execute: .\$scriptName" -ForegroundColor White

Write-Host "`nPara remover da inicializacao:" -ForegroundColor Yellow
Write-Host "  -> Delete: $shortcutPath" -ForegroundColor Gray

Write-Host "`n========================================`n" -ForegroundColor Cyan
