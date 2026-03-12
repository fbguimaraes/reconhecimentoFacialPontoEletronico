# ========================================
# Configurar Firewall - Django API
# EXECUTE COMO ADMINISTRADOR
# ========================================

param(
    [int]$Port = 8000
)

# Verificar se esta rodando como admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERRO: Este script requer privilegios de Administrador!" -ForegroundColor Red
    Write-Host "`nComo executar:" -ForegroundColor Yellow
    Write-Host "1. Fechar este PowerShell" -ForegroundColor White
    Write-Host "2. Buscar 'PowerShell' no menu Iniciar" -ForegroundColor White
    Write-Host "3. Clicar com botao direito > 'Executar como administrador'" -ForegroundColor White
    Write-Host "4. Navegar ate: $PSScriptRoot" -ForegroundColor White
    Write-Host "5. Executar: .\configurar_firewall.ps1" -ForegroundColor White
    Write-Host "`nOu copie e execute este comando no PowerShell Admin:" -ForegroundColor Yellow
    Write-Host "  cd $PSScriptRoot; .\configurar_firewall.ps1" -ForegroundColor Cyan
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CONFIGURACAO DE FIREWALL" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$ruleName = "Django API - Reconhecimento Facial"

# Verificar regra existente
Write-Host "Verificando regra existente..." -ForegroundColor Yellow
$existingRule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue

if ($existingRule) {
    Write-Host "  Regra ja existe! Removendo para recriar..." -ForegroundColor Gray
    Remove-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
}

# Criar nova regra
Write-Host "Criando regra de firewall..." -ForegroundColor Yellow
try {
    New-NetFirewallRule `
        -DisplayName $ruleName `
        -Direction Inbound `
        -LocalPort $Port `
        -Protocol TCP `
        -Action Allow `
        -Enabled True `
        -Profile Any `
        -Description "Permite conexoes para o servidor Django de Reconhecimento Facial" | Out-Null
    
    Write-Host "  Regra criada com sucesso!" -ForegroundColor Green
} catch {
    Write-Host "  ERRO: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Verificar
Write-Host "`nVerificando configuracao..." -ForegroundColor Yellow
$rule = Get-NetFirewallRule -DisplayName $ruleName

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  FIREWALL CONFIGURADO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nDetalhes da Regra:" -ForegroundColor Yellow
Write-Host "  Nome:      $($rule.DisplayName)" -ForegroundColor White
Write-Host "  Porta:     $Port (TCP)" -ForegroundColor White
Write-Host "  Direcao:   Entrada (Inbound)" -ForegroundColor White
Write-Host "  Acao:      Permitir" -ForegroundColor White
Write-Host "  Status:    $($rule.Enabled)" -ForegroundColor White
Write-Host "  Perfis:    Todos (Domain, Private, Public)" -ForegroundColor White

Write-Host "`nAgora outros computadores na rede podem acessar:" -ForegroundColor Yellow
Write-Host "  http://SEU_IP:$Port/" -ForegroundColor Cyan

Write-Host "`n========================================`n" -ForegroundColor Cyan
