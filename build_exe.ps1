# ========================================
# Build Script - Reconhecimento Facial
# Gera executável .exe para ambiente industrial
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  BUILD - Sistema de Reconhecimento Facial" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Ativar ambiente virtual
Write-Host "[1/6] Ativando ambiente virtual..." -ForegroundColor Yellow
& .\env\Scripts\Activate.ps1

# Instalar PyInstaller se necessário
Write-Host "`n[2/6] Verificando PyInstaller..." -ForegroundColor Yellow
$pyinstaller = pip show pyinstaller 2>$null
if (-not $pyinstaller) {
    Write-Host "  Instalando PyInstaller..." -ForegroundColor Gray
    pip install pyinstaller
} else {
    Write-Host "  PyInstaller ja instalado" -ForegroundColor Green
}

# Limpar builds anteriores
Write-Host "`n[3/6] Limpando builds anteriores..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "*.spec") { Remove-Item -Force "*.spec" }
Write-Host "  Diretórios limpos" -ForegroundColor Green

# Criar diretório de distribuição
Write-Host "`n[4/6] Criando estrutura de distribuição..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "dist_release" -Force | Out-Null

# Build do executável
Write-Host "`n[5/6] Compilando executável (isso pode demorar alguns minutos)..." -ForegroundColor Yellow
Write-Host "  Processando dependências..." -ForegroundColor Gray

pyinstaller --noconfirm `
    --onefile `
    --windowed `
    --name "SistemaReconhecimentoFacial" `
    --icon="assets/icon.ico" `
    --add-data "models;models" `
    --hidden-import "mediapipe" `
    --hidden-import "cv2" `
    --hidden-import "PIL" `
    --hidden-import "numpy" `
    --hidden-import "requests" `
    --hidden-import "tkinter" `
    --collect-all mediapipe `
    --collect-all cv2 `
    main.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "  Build concluido com sucesso!" -ForegroundColor Green
} else {
    Write-Host "  ERRO no build!" -ForegroundColor Red
    exit 1
}

# Copiar arquivos necessários
Write-Host "`n[6/6] Preparando distribuição final..." -ForegroundColor Yellow

# Criar estrutura de pastas
New-Item -ItemType Directory -Path "dist_release\models" -Force | Out-Null
New-Item -ItemType Directory -Path "dist_release\data" -Force | Out-Null
New-Item -ItemType Directory -Path "dist_release\logs" -Force | Out-Null

# Copiar executável
Copy-Item "dist\SistemaReconhecimentoFacial.exe" "dist_release\" -Force
Write-Host "  Executavel copiado" -ForegroundColor Green

# Copiar modelos (se existirem)
if (Test-Path "models") {
    Copy-Item "models\*" "dist_release\models\" -Force -ErrorAction SilentlyContinue
    Write-Host "  Modelos copiados" -ForegroundColor Green
}

# Criar arquivo de configuração
$configContent = @"
# Configuracao do Sistema de Reconhecimento Facial
# Edite este arquivo para configurar a URL do servidor Django

[API]
# URL do servidor Django (altere para o IP do servidor em producao)
BASE_URL = http://localhost:8000/api

# Timeout das requisicoes (em segundos)
TIMEOUT = 5

[CAMERA]
# Indice da camera (0 = padrao, 1 = segunda camera, etc)
CAMERA_INDEX = 0

# Resolucao da camera
WIDTH = 640
HEIGHT = 480

[RECOGNITION]
# Limiar de similaridade (0.0 a 1.0, maior = mais restritivo)
THRESHOLD = 0.40

# Numero de frames para captura de cadastro
CAPTURE_FRAMES = 10
"@

Set-Content -Path "dist_release\config.ini" -Value $configContent
Write-Host "  Arquivo de configuracao criado" -ForegroundColor Green

# Criar README
$readmeContent = @"
========================================
  Sistema de Reconhecimento Facial
  Versao Industrial v2.0
========================================

INSTALACAO
----------

1. Copie a pasta 'dist_release' para o local desejado
2. Certifique-se de que o servidor Django esta rodando
3. Execute 'SistemaReconhecimentoFacial.exe'


CONFIGURACAO
------------

Edite o arquivo 'config.ini' para:

- Alterar URL do servidor Django (producao)
- Configurar camera
- Ajustar parametros de reconhecimento


SERVIDOR DJANGO
---------------

O sistema precisa de um servidor Django rodando para funcionar.

Para iniciar o servidor Django:

1. Abra PowerShell na pasta do projeto
2. Execute: cd django_backend
3. Execute: python manage.py runserver 0.0.0.0:8000

Para acesso remoto, configure ALLOWED_HOSTS no Django.


REQUISITOS
----------

- Windows 10/11 (64-bit)
- Webcam conectada
- Servidor Django ativo e acessivel
- Conexao de rede com o servidor


ESTRUTURA DE PASTAS
-------------------

dist_release/
  ├── SistemaReconhecimentoFacial.exe  # Executavel principal
  ├── config.ini                        # Configuracoes
  ├── models/                           # Modelos de IA (baixados automaticamente)
  ├── data/                             # Dados locais
  └── logs/                             # Logs do sistema


SUPORTE
-------

Em caso de problemas:

1. Verifique se o servidor Django esta rodando
2. Teste a conexao: http://localhost:8000/
3. Verifique os logs em 'logs/'
4. Certifique-se de que a camera esta conectada


DASHBOARD WEB
-------------

Acesse o dashboard em: http://localhost:8000/
Admin panel: http://localhost:8000/admin/


ATUALIZACOES
------------

Para atualizar o sistema:

1. Mantenha a pasta 'data/' (seus dados)
2. Substitua apenas o .exe e arquivos de configuracao
3. Reinicie o aplicativo


========================================
Desenvolvido para ambiente industrial
Data: $(Get-Date -Format "dd/MM/yyyy")
========================================
"@

Set-Content -Path "dist_release\README.txt" -Value $readmeContent
Write-Host "  README.txt criado" -ForegroundColor Green

# Criar script de instalação do servidor
$serverScript = @"
# ========================================
# Instalacao do Servidor Django
# ========================================

Write-Host "Instalando servidor Django..." -ForegroundColor Cyan

# Copiar pasta django_backend
Copy-Item -Recurse "..\django_backend" "." -Force

# Instalar dependencias
pip install Django==4.2.11 djangorestframework==3.14.0 django-cors-headers==4.3.1

Write-Host "Servidor instalado!" -ForegroundColor Green
Write-Host "Para iniciar: cd django_backend; python manage.py runserver 0.0.0.0:8000" -ForegroundColor Yellow
"@

Set-Content -Path "dist_release\instalar_servidor.ps1" -Value $serverScript
Write-Host "  Script de instalacao do servidor criado" -ForegroundColor Green

# Criar script de inicialização rápida
$startScript = @"
# ========================================
# Inicializacao Rapida - Sistema Completo
# ========================================

Write-Host "Iniciando Sistema de Reconhecimento Facial..." -ForegroundColor Cyan

# Verificar se Django esta instalado
if (-not (Test-Path "django_backend")) {
    Write-Host "ERRO: Django nao encontrado!" -ForegroundColor Red
    Write-Host "Execute 'instalar_servidor.ps1' primeiro" -ForegroundColor Yellow
    pause
    exit 1
}

# Iniciar servidor Django em background
Write-Host "Iniciando servidor Django..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd django_backend; python manage.py runserver 0.0.0.0:8000"

# Aguardar servidor iniciar
Start-Sleep -Seconds 3

# Iniciar aplicação
Write-Host "Iniciando aplicacao..." -ForegroundColor Yellow
.\SistemaReconhecimentoFacial.exe

Write-Host "Sistema encerrado." -ForegroundColor Gray
"@

Set-Content -Path "dist_release\iniciar_sistema.ps1" -Value $startScript
Write-Host "  Script de inicializacao criado" -ForegroundColor Green

# Resumo final
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  BUILD CONCLUIDO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nArquivos gerados em: dist_release\" -ForegroundColor White
Write-Host "`nConteudo:" -ForegroundColor Yellow
Write-Host "  - SistemaReconhecimentoFacial.exe" -ForegroundColor White
Write-Host "  - config.ini (configuracoes)" -ForegroundColor White
Write-Host "  - README.txt (documentacao)" -ForegroundColor White
Write-Host "  - iniciar_sistema.ps1 (start completo)" -ForegroundColor White
Write-Host "  - instalar_servidor.ps1 (setup Django)" -ForegroundColor White

Write-Host "`nProximos passos:" -ForegroundColor Cyan
Write-Host "  1. Teste: cd dist_release; .\SistemaReconhecimentoFacial.exe" -ForegroundColor Gray
Write-Host "  2. Configure config.ini para producao" -ForegroundColor Gray
Write-Host "  3. Distribua a pasta 'dist_release' completa" -ForegroundColor Gray

Write-Host "`n========================================`n" -ForegroundColor Cyan
