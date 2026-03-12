# ========================================
# Verificar Sistema Antes de Instalar Servico
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VERIFICACAO DO SISTEMA" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$allOk = $true
$checks = @()

# Funcao auxiliar para verificacoes
function Test-Component {
    param($name, $condition, $message, $fixHint)
    
    Write-Host "Verificando: $name..." -ForegroundColor Yellow -NoNewline
    
    if ($condition) {
        Write-Host " OK" -ForegroundColor Green
        return @{Name=$name; Status="OK"; Message=$message}
    } else {
        Write-Host " FALHOU" -ForegroundColor Red
        Write-Host "  $message" -ForegroundColor Gray
        if ($fixHint) {
            Write-Host "  Fix: $fixHint" -ForegroundColor Yellow
        }
        $script:allOk = $false
        return @{Name=$name; Status="FALHOU"; Message=$message; Fix=$fixHint}
    }
}

# 1. Python
$pythonPath = ".\env\Scripts\python.exe"
$checks += Test-Component `
    -name "Ambiente Virtual Python" `
    -condition (Test-Path $pythonPath) `
    -message "Python encontrado em: $pythonPath" `
    -fixHint "Execute: python -m venv env"

# 2. Django
if (Test-Path $pythonPath) {
    $djangoInstalled = & $pythonPath -c "import django; print(django.get_version())" 2>$null
    $checks += Test-Component `
        -name "Django Framework" `
        -condition ($null -ne $djangoInstalled) `
        -message "Django versao: $djangoInstalled" `
        -fixHint "Execute: pip install Django"
}

# 3. Waitress
if (Test-Path $pythonPath) {
    $waitressPath = ".\env\Scripts\waitress-serve.exe"
    $checks += Test-Component `
        -name "Waitress (Servidor Producao)" `
        -condition (Test-Path $waitressPath) `
        -message "Waitress instalado" `
        -fixHint "Execute: pip install waitress"
}

# 4. Banco de dados
$dbPath = ".\django_backend\db.sqlite3"
$checks += Test-Component `
    -name "Banco de Dados" `
    -condition (Test-Path $dbPath) `
    -message "Banco SQLite: $dbPath" `
    -fixHint "Execute: cd django_backend; python manage.py migrate"

# 5. Modelos de ML
$model1 = ".\models\face_landmarker.task"
$model2 = ".\models\face_recognition_sface_2021dec.onnx"
$checks += Test-Component `
    -name "Modelos de ML" `
    -condition ((Test-Path $model1) -and (Test-Path $model2)) `
    -message "Modelos encontrados em .\models\" `
    -fixHint "Verifique se os arquivos .task e .onnx estao na pasta models/"

# 6. Configuracao Django
$settingsPath = ".\django_backend\config\settings.py"
$settings = Get-Content $settingsPath -Raw
$allowedHosts = $settings -match "ALLOWED_HOSTS\s*=\s*\[(.*?)\]"
$checks += Test-Component `
    -name "Configuracao Django" `
    -condition ($allowedHosts) `
    -message "settings.py configurado" `
    -fixHint "Execute: .\django_backend\deploy_server.ps1"

# 7. NSSM (necessario para servico)
$nssmPaths = @(
    "C:\nssm\win64\nssm.exe",
    "C:\nssm\nssm.exe",
    ".\nssm.exe"
)
$nssmFound = $false
$nssmPath = ""
foreach ($path in $nssmPaths) {
    if (Test-Path $path) {
        $nssmFound = $true
        $nssmPath = $path
        break
    }
}
$checks += Test-Component `
    -name "NSSM (Gerenciador de Servicos)" `
    -condition $nssmFound `
    -message "NSSM em: $nssmPath" `
    -fixHint "Baixe em https://nssm.cc/download e extraia para C:\nssm\"

# 8. Firewall
$ruleName = "Django API - Reconhecimento Facial"
$firewallRule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
$checks += Test-Component `
    -name "Regra de Firewall" `
    -condition ($null -ne $firewallRule) `
    -message "Porta 8000 liberada" `
    -fixHint "Execute: .\django_backend\deploy_server.ps1"

# 9. Executavel cliente (.exe)
$exePath = ".\dist_release\SistemaReconhecimentoFacial.exe"
$checks += Test-Component `
    -name "Executavel Cliente (.exe)" `
    -condition (Test-Path $exePath) `
    -message "Executavel gerado em: dist_release\" `
    -fixHint "Execute: .\build_exe.ps1"

# 10. Configuracao cliente
$configPath = ".\dist_release\config.ini"
if (Test-Path $configPath) {
    $configContent = Get-Content $configPath -Raw
    $hasApiUrl = $configContent -match "BASE_URL"
    $checks += Test-Component `
        -name "Configuracao Cliente (config.ini)" `
        -condition $hasApiUrl `
        -message "config.ini configurado" `
        -fixHint "Edite dist_release\config.ini com o IP do servidor"
}

# Resumo
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  RESUMO DA VERIFICACAO" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$okCount = ($checks | Where-Object { $_.Status -eq "OK" }).Count
$totalCount = $checks.Count

Write-Host "Componentes verificados: $totalCount" -ForegroundColor White
Write-Host "OK:     $okCount" -ForegroundColor Green
Write-Host "FALHOU: $($totalCount - $okCount)" -ForegroundColor $(if($allOk){"Green"}else{"Red"})

if ($allOk) {
    Write-Host "`n SISTEMA PRONTO PARA INSTALACAO!" -ForegroundColor Green
    Write-Host "`nProximos passos:" -ForegroundColor Yellow
    Write-Host "1. Baixar NSSM se nao tiver:" -ForegroundColor White
    Write-Host "   https://nssm.cc/download" -ForegroundColor Cyan
    Write-Host "   Extrair para: C:\nssm\" -ForegroundColor Gray
    Write-Host "`n2. Instalar servico:" -ForegroundColor White
    Write-Host "   cd django_backend" -ForegroundColor Gray
    Write-Host "   .\install_service_windows.ps1" -ForegroundColor Gray
    Write-Host "`n3. Distribuir cliente:" -ForegroundColor White
    Write-Host "   Editar dist_release\config.ini com IP do servidor" -ForegroundColor Gray
    Write-Host "   Copiar pasta dist_release para cada PC" -ForegroundColor Gray
} else {
    Write-Host "`n CORRIJA OS PROBLEMAS ACIMA PRIMEIRO!" -ForegroundColor Red
    Write-Host "`nComponentes faltando:" -ForegroundColor Yellow
    $checks | Where-Object { $_.Status -eq "FALHOU" } | ForEach-Object {
        Write-Host "  - $($_.Name)" -ForegroundColor Red
        if ($_.Fix) {
            Write-Host "    $($_.Fix)" -ForegroundColor Gray
        }
    }
    
    Write-Host "`nScript de correcao rapida:" -ForegroundColor Yellow
    Write-Host "  .\django_backend\deploy_server.ps1  # Configura Django" -ForegroundColor Gray
    Write-Host "  .\build_exe.ps1                     # Gera executavel" -ForegroundColor Gray
}

Write-Host "`n========================================`n" -ForegroundColor Cyan
