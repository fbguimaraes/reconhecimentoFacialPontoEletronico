# ========================================
# Script Inteligente de Inicializacao
# Detecta IP e atualiza configuracoes automaticamente
# ========================================

param(
    [switch]$ShowWindow = $false
)

$ErrorActionPreference = "SilentlyContinue"

# Cores
function Write-ColorOutput {
    param($Text, $Color = "White")
    Write-Host $Text -ForegroundColor $Color
}

Write-ColorOutput "`n========================================" "Cyan"
Write-ColorOutput "  SERVIDOR RECONHECIMENTO FACIAL" "Cyan"
Write-ColorOutput "========================================`n" "Cyan"

# Ir para diretorio do projeto
Set-Location "C:\Users\fbznn\Documents\reconhecimento_facial"

# 1. Detectar IP
Write-ColorOutput "[1/6] Detectando IP da rede..." "Yellow"
$SERVER_IP = (Get-NetIPConfiguration | Where-Object {$_.IPv4DefaultGateway -ne $null}).IPv4Address.IPAddress

if ($SERVER_IP) {
    Write-ColorOutput "  IP detectado: $SERVER_IP" "Green"
} else {
    $SERVER_IP = "localhost"
    Write-ColorOutput "  AVISO: Rede nao encontrada, usando localhost" "Yellow"
}

# 2. Atualizar config.ini
Write-ColorOutput "`n[2/6] Atualizando config.ini..." "Yellow"
$configPath = "dist_release\config.ini"
if (Test-Path $configPath) {
    $config = Get-Content $configPath -Raw
    $config = $config -replace "BASE_URL = http://.*?:8000/api", "BASE_URL = http://$SERVER_IP:8000/api"
    Set-Content -Path $configPath -Value $config
    Write-ColorOutput "  config.ini atualizado com IP: $SERVER_IP" "Green"
}

# 3. Atualizar ALLOWED_HOSTS do Django
Write-ColorOutput "`n[3/6] Atualizando Django ALLOWED_HOSTS..." "Yellow"
$settingsPath = "django_backend\config\settings.py"
if (Test-Path $settingsPath) {
    $settings = Get-Content $settingsPath -Raw
    
    # Verificar se IP ja esta nos ALLOWED_HOSTS
    if ($settings -notmatch [regex]::Escape($SERVER_IP)) {
        $settings = $settings -replace "(ALLOWED_HOSTS = \[.*?)(\])", "`$1, '$SERVER_IP'`$2"
        Set-Content -Path $settingsPath -Value $settings
        Write-ColorOutput "  Django configurado para aceitar IP: $SERVER_IP" "Green"
    } else {
        Write-ColorOutput "  IP ja configurado no Django" "Green"
    }
}

# 4. Criar arquivo com informacoes do servidor
Write-ColorOutput "`n[4/6] Criando arquivo de informacoes..." "Yellow"
$infoContent = @"
========================================
  INFORMACOES DO SERVIDOR
========================================

IP do Servidor: $SERVER_IP
Porta: 8000
Data/Hora Inicio: $(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')

URLs de Acesso:
  Dashboard:  http://$SERVER_IP:8000/
  API:        http://$SERVER_IP:8000/api/
  Admin:      http://$SERVER_IP:8000/admin/
  Localhost:  http://localhost:8000/

Configuracao dos Clientes (.exe):
  Editar config.ini:
    [API]
    BASE_URL = http://$SERVER_IP:8000/api

========================================
"@

Set-Content -Path "SERVER_INFO.txt" -Value $infoContent
Write-ColorOutput "  Arquivo SERVER_INFO.txt criado" "Green"

# 5. Ativar ambiente virtual
Write-ColorOutput "`n[5/6] Ativando ambiente virtual..." "Yellow"
& ".\env\Scripts\Activate.ps1"
Write-ColorOutput "  Ambiente virtual ativado" "Green"

# 6. Iniciar servidor
Write-ColorOutput "`n[6/6] Iniciando servidor Django..." "Yellow"

Write-ColorOutput "`n========================================" "Cyan"
Write-ColorOutput "  SERVIDOR RODANDO EM:" "Green"
Write-ColorOutput "========================================" "Cyan"
Write-ColorOutput "`n  Dashboard:  http://$SERVER_IP:8000/" "White"
Write-ColorOutput "  API:        http://$SERVER_IP:8000/api/" "White"
Write-ColorOutput "  Admin:      http://$SERVER_IP:8000/admin/" "White"
Write-ColorOutput "  Localhost:  http://localhost:8000/" "Gray"
Write-ColorOutput "`n========================================" "Cyan"
Write-ColorOutput "  Arquivo de info: SERVER_INFO.txt" "Yellow"
Write-ColorOutput "  Ctrl+C para parar o servidor" "Gray"
Write-ColorOutput "========================================`n" "Cyan"

# Iniciar servidor
Set-Location django_backend
python manage.py runserver 0.0.0.0:8000
