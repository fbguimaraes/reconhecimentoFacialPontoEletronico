@echo off
title Servidor Reconhecimento Facial
color 0A

echo ========================================
echo   SERVIDOR RECONHECIMENTO FACIAL
echo ========================================
echo.

cd /d C:\Users\fbznn\Documents\reconhecimento_facial

echo [1/5] Detectando IP da rede...
powershell -Command "$ip = (Get-NetIPConfiguration | Where-Object {$_.IPv4DefaultGateway -ne $null}).IPv4Address.IPAddress; if ($ip) { Write-Host '  IP DETECTADO: ' -NoNewline -ForegroundColor Green; Write-Host $ip -ForegroundColor Cyan; echo $ip > temp_ip.txt } else { Write-Host '  AVISO: Usando localhost' -ForegroundColor Yellow; echo 'localhost' > temp_ip.txt }"

set /p SERVER_IP=<temp_ip.txt
del temp_ip.txt

echo.
echo [2/5] Atualizando configuracoes...
powershell -Command "(Get-Content 'dist_release\config.ini') -replace 'BASE_URL = http://.*?:8000/api', 'BASE_URL = http://%SERVER_IP%:8000/api' | Set-Content 'dist_release\config.ini'"
echo   config.ini atualizado!

echo.
echo [3/5] Ativando ambiente virtual...
call env\Scripts\activate.bat

echo.
echo [4/5] Navegando para django_backend...
cd django_backend

echo.
echo [5/5] Iniciando servidor Django...
echo ========================================
echo.
echo   SERVIDOR RODANDO EM:
echo.
echo   Dashboard:  http://%SERVER_IP%:8000/
echo   API:        http://%SERVER_IP%:8000/api/
echo   Admin:      http://%SERVER_IP%:8000/admin/
echo   Localhost:  http://localhost:8000/
echo.
echo ========================================
echo   PRESSIONE CTRL+C PARA PARAR
echo ========================================
echo.

python manage.py runserver 0.0.0.0:8000
