# ========================================
# Script de Deploy do Servidor Django
# Execute no servidor central
# ========================================

param(
    [string]$ServerIP = "0.0.0.0",
    [int]$Port = 8000
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DEPLOY - Servidor Django" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# 1. Verificar ambiente
Write-Host "[1/8] Verificando ambiente..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "  $pythonVersion" -ForegroundColor Green

# 2. Ativar ambiente virtual
Write-Host "`n[2/8] Ativando ambiente virtual..." -ForegroundColor Yellow
if (Test-Path "..\env\Scripts\Activate.ps1") {
    & ..\env\Scripts\Activate.ps1
    Write-Host "  Ambiente ativado" -ForegroundColor Green
} else {
    Write-Host "  Criando ambiente virtual..." -ForegroundColor Gray
    python -m venv ..\env
    & ..\env\Scripts\Activate.ps1
}

# 3. Instalar dependencias
Write-Host "`n[3/8] Instalando dependencias..." -ForegroundColor Yellow
pip install -q Django==4.2.11 djangorestframework==3.14.0 django-cors-headers==4.3.1 waitress==3.0.2
Write-Host "  Dependencias instaladas" -ForegroundColor Green

# 4. Configurar settings
Write-Host "`n[4/8] Configurando Django..." -ForegroundColor Yellow

$localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*"} | Select-Object -First 1).IPAddress
Write-Host "  IP local detectado: $localIP" -ForegroundColor Gray

# Adicionar IP aos ALLOWED_HOSTS se nao existir
$settingsFile = "config\settings.py"
$settingsContent = Get-Content $settingsFile -Raw

if ($settingsContent -notmatch $localIP) {
    Write-Host "  Adicionando $localIP aos ALLOWED_HOSTS..." -ForegroundColor Gray
    $settingsContent = $settingsContent -replace "ALLOWED_HOSTS = \[(.*?)\]", "ALLOWED_HOSTS = [`$1, '$localIP']"
    Set-Content -Path $settingsFile -Value $settingsContent
    Write-Host "  Configuracao atualizada" -ForegroundColor Green
}

# 5. Migracoes
Write-Host "`n[5/8] Aplicando migracoes..." -ForegroundColor Yellow
python manage.py makemigrations 2>&1 | Out-Null
python manage.py migrate --noinput
Write-Host "  Migracoes aplicadas" -ForegroundColor Green

# 6. Coletar arquivos estaticos
Write-Host "`n[6/8] Coletando arquivos estaticos..." -ForegroundColor Yellow
python manage.py collectstatic --noinput 2>&1 | Out-Null
Write-Host "  Arquivos estaticos coletados" -ForegroundColor Green

# 7. Criar superuser (se nao existir)
Write-Host "`n[7/8] Verificando superuser..." -ForegroundColor Yellow
$hasSuperuser = python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(is_superuser=True).exists())" 2>&1
if ($hasSuperuser -like "*True*") {
    Write-Host "  Superuser ja existe" -ForegroundColor Green
} else {
    Write-Host "  Criando superuser..." -ForegroundColor Gray
    Write-Host "`n  ====================================" -ForegroundColor Cyan
    python manage.py createsuperuser
    Write-Host "  ====================================" -ForegroundColor Cyan
}

# 8. Configurar firewall
Write-Host "`n[8/8] Configurando firewall..." -ForegroundColor Yellow
$ruleName = "Django API - Reconhecimento Facial"
$existingRule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue

if (-not $existingRule) {
    try {
        New-NetFirewallRule -DisplayName $ruleName -Direction Inbound -LocalPort $Port -Protocol TCP -Action Allow -ErrorAction Stop | Out-Null
        Write-Host "  Regra de firewall criada (porta $Port)" -ForegroundColor Green
    } catch {
        Write-Host "  AVISO: Nao foi possivel criar regra de firewall" -ForegroundColor Yellow
        Write-Host "  Motivo: Requer privilegios de Administrador" -ForegroundColor Gray
        Write-Host "  Servidor funcionara localmente, mas talvez nao aceite conexoes externas" -ForegroundColor Gray
        Write-Host "`n  Para liberar firewall manualmente (PowerShell Admin):" -ForegroundColor Cyan
        Write-Host "    New-NetFirewallRule -DisplayName '$ruleName' -Direction Inbound -LocalPort $Port -Protocol TCP -Action Allow" -ForegroundColor Gray
    }
} else {
    Write-Host "  Regra de firewall ja existe" -ForegroundColor Green
}

# Resumo
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  DEPLOY CONCLUIDO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nServidor configurado:" -ForegroundColor Yellow
Write-Host "  IP: $localIP" -ForegroundColor White
Write-Host "  Porta: $Port" -ForegroundColor White

Write-Host "`nURLs de acesso:" -ForegroundColor Yellow
Write-Host "  Dashboard: http://$localIP`:$Port/" -ForegroundColor Cyan
Write-Host "  API:       http://$localIP`:$Port/api/" -ForegroundColor Cyan
Write-Host "  Admin:     http://$localIP`:$Port/admin/" -ForegroundColor Cyan

Write-Host "`nPara iniciar o servidor:" -ForegroundColor Yellow
Write-Host "  Producao (Waitress):" -ForegroundColor White
Write-Host "    waitress-serve --host=$ServerIP --port=$Port config.wsgi:application" -ForegroundColor Gray
Write-Host "`n  Desenvolvimento:" -ForegroundColor White
Write-Host "    python manage.py runserver $ServerIP`:$Port" -ForegroundColor Gray

Write-Host "`nConfiguracao dos clientes (.exe):" -ForegroundColor Yellow
Write-Host "  Editar config.ini:" -ForegroundColor White
Write-Host "    [API]" -ForegroundColor Gray
Write-Host "    BASE_URL = http://$localIP`:$Port/api" -ForegroundColor Gray

Write-Host "`n========================================`n" -ForegroundColor Cyan

# Perguntar se quer iniciar agora
$start = Read-Host "Deseja iniciar o servidor agora? (S/N)"
if ($start -eq "S" -or $start -eq "s") {
    Write-Host "`nIniciando servidor..." -ForegroundColor Cyan
    Write-Host "Pressione Ctrl+C para parar`n" -ForegroundColor Yellow
    waitress-serve --host=$ServerIP --port=$Port config.wsgi:application
}
