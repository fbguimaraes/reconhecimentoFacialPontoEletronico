# ========================================
# GUIA RAPIDO - SERVIDOR COM DETECCAO AUTOMATICA DE IP
# ========================================

## O QUE FOI CONFIGURADO

Seu servidor agora:
✅ Detecta o IP automaticamente ao iniciar
✅ Atualiza config.ini com IP correto
✅ Atualiza Django ALLOWED_HOSTS
✅ Cria arquivo SERVER_INFO.txt com informações
✅ Inicia automaticamente quando você faz login no Windows

---

## ARQUIVOS CRIADOS

1. **IniciarServidor.bat**
   - Script BAT rápido
   - Detecta e mostra IP na tela
   - Atualiza config.ini automaticamente

2. **IniciarServidorInteligente.ps1**
   - Script PowerShell completo
   - Atualiza todas as configurações
   - Cria arquivo SERVER_INFO.txt

3. **ConfigurarInicializacao.ps1**
   - Escolhe qual script usar na inicialização
   - Cria atalho na pasta Startup

4. **SERVER_INFO.txt** (criado ao iniciar)
   - Informações do servidor
   - IP detectado
   - URLs de acesso
   - Configuração dos clientes

---

## COMO USAR

### Iniciar Servidor Manualmente

**Opção 1 (Inteligente - Recomendado):**
```powershell
.\IniciarServidorInteligente.ps1
```

**Opção 2 (Rápido):**
```
IniciarServidor.bat
```

### Ver Informações do Servidor

Abra o arquivo:
```
SERVER_INFO.txt
```

Contém:
- IP atual do servidor
- URLs de acesso
- Configuração para clientes

### Reconfigurar Inicialização

```powershell
.\ConfigurarInicializacao.ps1
```

Escolha entre:
- Script Inteligente (mais recursos)
- Script Simples (mais rápido)

---

## O QUE ACONTECE AO LIGAR O PC

1. 🔍 Windows faz login
2. 📡 Script detecta IP da rede
3. 📝 Atualiza config.ini
4. ⚙️  Atualiza Django ALLOWED_HOSTS
5. 📄 Cria SERVER_INFO.txt
6. 🚀 Inicia servidor Django
7. ✅ Servidor disponível na rede!

---

## VER IP DO SERVIDOR

### Método 1: Arquivo SERVER_INFO.txt
```
Abrir: SERVER_INFO.txt
```

### Método 2: Janela do Servidor
Quando o servidor inicia, mostra:
```
  SERVIDOR RODANDO EM:
  Dashboard:  http://192.168.1.X:8000/
```

### Método 3: PowerShell
```powershell
(Get-NetIPConfiguration | Where-Object {$_.IPv4DefaultGateway -ne $null}).IPv4Address.IPAddress
```

---

## ATUALIZAR CLIENTES (.exe)

Quando o IP mudar, você tem 2 opções:

### Opção 1: Recriar ZIP
```powershell
# O config.ini já está atualizado automaticamente!
$tempPath = "$env:TEMP\dist_release_temp"
Remove-Item $tempPath -Recurse -Force -ErrorAction SilentlyContinue
Copy-Item "dist_release" $tempPath -Recurse
Compress-Archive -Path $tempPath -DestinationPath "ReconhecimentoFacial_Teste.zip" -Force
Remove-Item $tempPath -Recurse -Force
```

### Opção 2: Instrução Manual para Clientes
Diga aos clientes para editarem `config.ini`:
```ini
[API]
BASE_URL = http://NOVO_IP:8000/api
```

---

## LOGS E DIAGNÓSTICO

### Ver IP Atual
```powershell
type SERVER_INFO.txt
```

### Testar Servidor
```powershell
# Teste local
Invoke-WebRequest http://localhost:8000/

# Teste pelo IP
Invoke-WebRequest http://192.168.1.X:8000/
```

### Reiniciar Servidor
1. Fechar janela do servidor (ou Ctrl+C)
2. Executar novamente:
   - `.\IniciarServidorInteligente.ps1` ou
   - `IniciarServidor.bat`

---

## FIXAR IP (PARA EVITAR MUDANÇAS)

### No Router (Recomendado)
1. Acessar painel do router (192.168.1.1)
2. Procurar "DHCP Reservation" ou "IP Estático"
3. Vincular MAC Address ao IP desejado

### No Windows
1. Painel de Controle → Rede
2. Propriedades do Adaptador
3. IPv4 → Usar o seguinte endereço IP
4. Definir IP fixo (ex: 192.168.1.5)

---

## COMANDOS ÚTEIS

```powershell
# Ver IP atual
ipconfig

# Testar porta 8000
Test-NetConnection localhost -Port 8000

# Parar todos os Python (parar servidor)
Stop-Process -Name python -Force

# Ver processos Python rodando
Get-Process python

# Abrir dashboard
Start-Process http://localhost:8000/

# Ver arquivo de info
notepad SERVER_INFO.txt
```

---

## SOLUÇÃO DE PROBLEMAS

### Servidor não inicia automaticamente
- Verificar se atalho existe em Startup
- Reexecutar: `.\ConfigurarInicializacao.ps1`

### IP continua errado
- Abrir SERVER_INFO.txt para ver IP detectado
- Verificar conexão de rede
- Reexecutar script manualmente

### Clientes não conectam
- Verificar se estão na mesma rede Wi-Fi
- Confirmar IP em SERVER_INFO.txt
- Atualizar config.ini nos clientes
- Testar: `http://IP_SERVIDOR:8000/` no navegador

---

Dúvidas? Execute `.\IniciarServidorInteligente.ps1` e veja SERVER_INFO.txt!
