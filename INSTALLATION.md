# 🚀 Guia de Instalação Completa

Instruções passo a passo para instalar e executar o sistema após clonar o repositório.

## 📋 Pré-requisitos

- **Python 3.8+** instalado
- **Git** instalado
- **Webcam** funcional
- **Windows/Linux/Mac**

---

## 🔧 Instalação Rápida

### 1️⃣ Clonar o Repositório

```bash
git clone https://github.com/SEU-USUARIO/reconhecimento-facial.git
cd reconhecimento-facial
```

### 2️⃣ Criar Ambiente Virtual

**Windows:**
```powershell
python -m venv env
.\env\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python3 -m venv env
source env/bin/activate
```

### 3️⃣ Instalar Dependências do Servidor Django

```bash
cd django_backend
pip install -r requirements.txt
```

### 4️⃣ Configurar Django

**Copiar arquivo de exemplo:**
```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

**Editar `.env`** (dentro de `django_backend/`):
```ini
SECRET_KEY=sua-chave-secreta-super-segura-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.100
```

**Gerar SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5️⃣ Executar Migrações

```bash
python manage.py migrate
python manage.py createsuperuser  # Opcional - criar usuário admin
```

### 6️⃣ Iniciar Servidor Django

```bash
# Acessível apenas localmente
python manage.py runserver

# Ou acessível na rede local
python manage.py runserver 0.0.0.0:8000
```

O servidor estará rodando em: **http://localhost:8000/**

### 7️⃣ Instalar Dependências do Cliente (Nova Janela de Terminal)

**Voltar para raiz do projeto e ativar ambiente:**
```bash
# Windows
cd ..
.\env\Scripts\Activate.ps1

# Linux/Mac
cd ..
source env/bin/activate
```

**Instalar dependências:**
```bash
pip install -r requirements.txt
```

### 8️⃣ Configurar Cliente

**Copiar arquivo de exemplo:**
```bash
# Windows
copy config.ini.example config.ini

# Linux/Mac
cp config.ini.example config.ini
```

**Editar `config.ini`:**
```ini
[API]
BASE_URL = http://localhost:8000/api
TIMEOUT = 5

[CAMERA]
CAMERA_INDEX = 0
WIDTH = 640
HEIGHT = 480

[RECOGNITION]
THRESHOLD = 0.40
CAPTURE_FRAMES = 10
```

### 9️⃣ Iniciar Cliente Desktop

```bash
python main.py
```

---

## 📦 Instalação Detalhada

### Estrutura Após Instalação

```
reconhecimento-facial/
├── env/                    ← Ambiente virtual criado
├── django_backend/
│   ├── .env               ← Criado por você
│   ├── db.sqlite3         ← Criado após migrate
│   └── ...
├── config.ini             ← Criado por você
├── models/                ← Criado automaticamente
│   ├── face_landmarker.task
│   └── face_recognition_sface_2021dec.onnx
├── data/                  ← Criado automaticamente
│   ├── embeddings.pkl
│   └── registros.csv
└── ...
```

### Download Automático de Modelos

Na primeira execução, os modelos de ML (~4MB) serão baixados automaticamente:
- `face_landmarker.task` (MediaPipe)
- `face_recognition_sface_2021dec.onnx`

Não é necessário fazer download manual.

---

## 🎮 Executando o Sistema

### Opção 1: Scripts Automatizados (Windows)

**Servidor:**
```powershell
.\IniciarServidorInteligente.ps1
```

**Cliente:**
```bash
python main.py
```

### Opção 2: Manual

**Terminal 1 - Servidor Django:**
```bash
cd django_backend
python manage.py runserver 0.0.0.0:8000
```

**Terminal 2 - Cliente Desktop:**
```bash
python main.py
```

### Opção 3: Apenas API (sem cliente)

```bash
cd django_backend
python manage.py runserver
```

Acesse o dashboard em: **http://localhost:8000/**

---

## 🌐 Testando a Instalação

### 1. Testar API

**No navegador ou via curl:**
```bash
# Windows PowerShell
Invoke-WebRequest http://localhost:8000/api/employees/

# Linux/Mac
curl http://localhost:8000/api/employees/
```

### 2. Testar Dashboard

Abra no navegador: **http://localhost:8000/**

### 3. Testar Cliente Desktop

Execute `python main.py` e verifique:
- Interface gráfica abre
- Webcam é detectada
- API se conecta (status na interface)

---

## 🔧 Configurações Adicionais

### Popular Dados de Teste

```bash
cd django_backend
python populate_mock_data.py
```

### Coletar Arquivos Estáticos (Produção)

```bash
cd django_backend
python manage.py collectstatic
```

### Configurar IP Fixo do Servidor

Edite `config.ini` no cliente:
```ini
[API]
BASE_URL = http://192.168.1.100:8000/api
```

E configure `ALLOWED_HOSTS` no Django:
```python
# django_backend/.env
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.100
```

---

## 🐛 Solução de Problemas

### Erro: "ModuleNotFoundError"

```bash
# Certifique-se de ter ativado o ambiente virtual
# Windows:
.\env\Scripts\Activate.ps1

# Linux/Mac:
source env/bin/activate

# Reinstale dependências
pip install -r requirements.txt
```

### Erro: "Port 8000 already in use"

```powershell
# Windows - Ver processo usando porta 8000
netstat -ano | findstr :8000

# Matar processo
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Erro: "No module named 'django'"

```bash
# Certifique-se de estar na pasta correta
cd django_backend

# Instalar dependências
pip install -r requirements.txt
```

### Erro: "Camera not found"

Verifique `config.ini`:
```ini
[CAMERA]
CAMERA_INDEX = 0  # Tente 0, 1, 2...
```

### Erro: "Connection refused" no cliente

1. Verifique se o servidor Django está rodando
2. Verifique `config.ini` - URL deve estar correta
3. Teste: `curl http://localhost:8000/api/employees/`

### Erro de Migração Django

```bash
cd django_backend
python manage.py migrate --run-syncdb
```

### Modelos não baixam automaticamente

Download manual:
```bash
# Criar pasta models
mkdir models

# Baixar face_landmarker.task
# URL: https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task
# Salvar em: models/face_landmarker.task
```

---

## 📊 Verificação Final

Execute este checklist:

- [ ] Ambiente virtual ativado
- [ ] Servidor Django rodando (http://localhost:8000/)
- [ ] Dashboard acessível no navegador
- [ ] API respondendo (/api/employees/)
- [ ] config.ini configurado
- [ ] Cliente desktop abre sem erros
- [ ] Webcam detectada no cliente
- [ ] Consegue cadastrar funcionário
- [ ] Consegue fazer reconhecimento facial

---

## 🚀 Após Instalação

### Próximos Passos

1. **Criar funcionários:**
   - Via dashboard: http://localhost:8000/
   - Via cliente desktop: botão "Cadastrar Funcionário"

2. **Registrar ponto:**
   - Usar cliente desktop: "Iniciar Reconhecimento"

3. **Ver relatórios:**
   - Dashboard web: http://localhost:8000/

### Uso em Rede Local

Para usar em múltiplos computadores:

1. **Servidor** rode em uma máquina fixa:
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

2. **Clientes** apontem para o IP do servidor:
   ```ini
   # config.ini em cada cliente
   [API]
   BASE_URL = http://192.168.1.100:8000/api
   ```

3. **Firewall:** Libere porta 8000 no servidor

---

## 📖 Documentação Adicional

- **[README.md](README.md)** - Visão geral do projeto
- **[GUIA_RAPIDO.md](GUIA_RAPIDO.md)** - Guia rápido de uso
- **[django_backend/README.md](django_backend/README.md)** - Documentação do backend
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Como contribuir

---

## 💡 Dicas

### Desenvolvimento

```bash
# Ativar debug no Django
# .env: DEBUG=True

# Ver logs detalhados
python manage.py runserver --verbosity 2
```

### Produção

```bash
# Desativar debug
# .env: DEBUG=False

# Usar PostgreSQL em vez de SQLite
# .env: DB_ENGINE=django.db.backends.postgresql

# Configurar HTTPS (use Nginx/Apache)
```

### Performance

- Use índices no banco de dados
- Configure cache do Django
- Otimize queries (use select_related/prefetch_related)

---

## ✅ Resumo dos Comandos

```bash
# 1. Clonar
git clone https://github.com/SEU-USUARIO/reconhecimento-facial.git
cd reconhecimento-facial

# 2. Ambiente virtual
python -m venv env
.\env\Scripts\Activate.ps1  # Windows
# source env/bin/activate    # Linux/Mac

# 3. Servidor Django
cd django_backend
pip install -r requirements.txt
copy .env.example .env  # Editar depois
python manage.py migrate
python manage.py runserver 0.0.0.0:8000

# 4. Cliente (novo terminal)
cd ..
.\env\Scripts\Activate.ps1  # Ativar env novamente
pip install -r requirements.txt
copy config.ini.example config.ini  # Editar depois
python main.py
```

---

**Pronto! 🎉 Seu sistema está rodando!**

Se encontrar problemas, consulte a seção [Solução de Problemas](#-solução-de-problemas) ou abra uma [issue](https://github.com/SEU-USUARIO/reconhecimento-facial/issues).
