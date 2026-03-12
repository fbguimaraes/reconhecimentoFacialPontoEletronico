# 🔐 Sistema de Ponto Eletrônico — Reconhecimento Facial

Sistema completo de controle de ponto eletrônico baseado em reconhecimento facial usando **MediaPipe FaceLandmarker**, **OpenCV**, **Django REST Framework** e interface desktop com **Tkinter**.

---

## 🎯 Início Rápido

**Acabou de clonar o repositório?** Escolha sua opção:

### 🤖 **Opção 1: CONFIGURAÇÃO AUTOMÁTICA** (Recomendado)
Use o GitHub Copilot para configurar tudo automaticamente!

👉 **[PROMPT_CONFIGURACAO_AUTO.md](PROMPT_CONFIGURACAO_AUTO.md)** ⭐

Copie o prompt e cole no Copilot - ele fará toda a configuração para você!

### 📖 **Opção 2: Configuração Manual**
Prefere fazer passo a passo? 

👉 **[INSTALLATION.md](INSTALLATION.md)** - Guia completo detalhado

### ⚡ **Opção 3: Comandos Rápidos**

👉 **[QUICKSTART_CLONE.md](QUICKSTART_CLONE.md)** - 5 minutos para rodar

---

## 📋 Índice

- [🤖 Configuração Automática](PROMPT_CONFIGURACAO_AUTO.md) ← **Mais fácil!**
- [🚀 Instalação Manual](INSTALLATION.md) ← **Passo a passo**
- [⚡ Quick Start](QUICKSTART_CLONE.md) ← **5 minutos**
- [Visão Geral](#visão-geral)
- [Requisitos](#requisitos)
- [Instalação Rápida](#instalação-rápida)
- [Configuração](#configuração)
- [Execução](#execução)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Funcionalidades](#funcionalidades)
- [Tecnologias](#tecnologias)
- [Documentação Adicional](#documentação-adicional)

## 🎯 Visão Geral

O sistema é composto por duas partes principais:

1. **Servidor Django (Backend)**: API REST para gerenciamento de funcionários, registros de ponto e dashboard web
2. **Cliente Desktop (Frontend)**: Interface gráfica standalone para reconhecimento facial e registro de ponto

### Características

✅ Reconhecimento facial em tempo real  
✅ API REST completa com Django REST Framework  
✅ Dashboard web administrativo  
✅ Cliente desktop distribuível (.exe)  
✅ Detecção automática de IP na rede local  
✅ Configuração via arquivo .ini  
✅ Inicialização automática do servidor  

## 💻 Requisitos

### Servidor
- Python 3.8+
- Django 4.2+
- Django REST Framework

### Cliente
- Python 3.8+ (ou executável .exe compilado)
- Webcam funcional
- Conexão de rede com o servidor
 Rápida

> 📖 **Para guia completo passo a passo:** Veja [INSTALLATION.md](INSTALLATION.md)

### Resumo dos Comandos

```bash
# 1. Clonar repositório
git clone https://github.com/seu-usuario/reconhecimento_facial.git
cd reconhecimento_facial

# 2. Criar ambiente virtual
python -m venv env
.\env\Scripts\activate        # Windows
# source env/bin/activate     # Linux/Mac

# 3. Servidor Django
cd django_backend
pip install -r requirements.txt
copy .env.example .env        # Editar depois!
python manage.py migrate
python manage.py runserver 0.0.0.0:8000

# 4. Cliente Desktop (novo terminal)
cd ..
.\env\Scripts\activate
pip install -r requirements.txt
copy config.ini.example config.ini  # Editar depois!
python main.py
```

**Detalhes completos em:** **[INSTALLATION.md](INSTALLATION.md)** ⭐ditar config.ini e .env conforme necessário
```

## ⚙️ Configuração

### Servidor Django

1. **Editar `.env`** (dentro de `django_backend/`):
```ini
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.100
```

2. **Executar migrações**:
```bash
cd django_backend
python manage.py migrate
python manage.py createsuperuser  # Criar usuário admin
python manage.py collectstatic
```

### Cliente Desktop

Editar `config.ini`:
```ini
[API]
BASE_URL = http://192.168.1.100:8000/api
TIMEOUT = 5

[CAMERA]
CAMERA_INDEX = 0
WIDTH = 640
HEIGHT = 480

[RECOGNITION]
THRESHOLD = 0.40
CAPTURE_FRAMES = 10
```

## 🎮 Execução

### Iniciar Servidor (Automático)

**Windows - Script Inteligente:**
```powershell
.\IniciarServidorInteligente.ps1
```

**Ou script simples:**
```cmd
IniciarServidor.bat
```

O servidor:
- Detecta IP automaticamente
- Atualiza configurações
- Inicia na porta 8000
- Cria arquivo `SERVER_INFO.txt`

### Iniciar Servidor (Manual)

```bash
cd django_backend
python manage.py runserver 0.0.0.0:8000
```

### Iniciar Cliente Desktop

```bash
python main.py
```

### Acessar Dashboard Web

```
http://localhost:8000/
http://192.168.1.X:8000/  # IP da rede local
```

## 📁 Estrutura do Projeto

```
reconhecimento_facial/
├── main.py                          # Interface desktop (Tkinter)
├── face_engine.py                   # Motor de reconhecimento facial
├── face_engine_api.py               # Cliente API para comunicação com servidor
├── config.py                        # Gerenciador de configurações
├── requirements.txt                 # Dependências do cliente
├── config.ini.example               # Exemplo de configuração
├── .env.example                     # Exemplo de variáveis de ambiente
├── .gitignore                       # Arquivos ignorados pelo Git
│
├── django_backend/                  # Servidor Django
│   ├── manage.py
│   ├── requirements.txt
│   ├── db.sqlite3                   # Banco de dados (não versionado)
│   ├── config/                      # Configurações Django
│   │   ├── settings.py              # Configurações desenvolvimento
│   │   ├── settings_production.py  # Configurações produção
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── employees/                   # App de funcionários
│   │   ├── models.py                # Modelos (Employee, TimeRecord)
│   │   ├── serializers.py           # Serializers DRF
│   │   ├── views.py                 # ViewSets da API
│   │   └── urls.py
│   └── dashboard/                   # App do dashboard web
│       ├── views.py
│       ├── urls.py
│       └── templates/
│
├── models/                          # Modelos de ML (não versionados)
│   ├── face_landmarker.task         # MediaPipe FaceLandmarker
│   └── face_recognition_sface_2021dec.onnx
│
├── data/                            # Dados do sistema (não versionados)
│   ├── embeddings.pkl
│   └── registros.csv
│
├── logs/                            # Logs do sistema (não versionados)
│
├── scripts/                         # Scripts de inicialização
│   ├── IniciarServidor.bat
│   ├── IniciarServidorInteligente.ps1
│   └── ConfigurarInicializacao.ps1
│
└── docs/                            # Documentação
    ├── GUIA_RAPIDO.md
    ├── QUICKSTART.md
    └── PASSO_A_PASSO.txt
```

## Funcionalidades

### 🖥️ Cliente Desktop

**Cadastrar Funcionário:**
1. Clique em **"Cadastrar Novo Funcionário"**
2. Preencha o **ID** e o **Nome**
3. Clique em **"Iniciar Captura"**
4. Olhe para a câmera — o sistema captura múltiplos frames
5. Embedding facial é enviado para o servidor

**Reconhecimento em Tempo Real:**
1. Clique em **"Iniciar Reconhecimento"**
2. Webcam detecta rostos automaticamente
3. Sistema compara com base de dados via API
4. Registro de ponto automático ao reconhecer funcionário
5. Cooldown previne registros duplicados

**Ver Registros:**
- Visualiza histórico de pontos
- Filtragem por data e funcionário
- Exportação de relatórios

### 🌐 Dashboard Web

**Gerenciamento:**
- Lista de funcionários cadastrados
- Histórico completo de registros
- Estatísticas e relatórios
- Interface administrativa Django

**API REST:**
- `/api/employees/` - CRUD de funcionários
- `/api/employees/{id}/register_time/` - Registro de ponto
- `/api/time-records/` - Consulta de registros
- Documentação interativa (DRF Browsable API)

## 🛠️ Tecnologias

### Backend
- **Django 4.2** - Framework web
- **Django REST Framework** - API REST
- **SQLite/PostgreSQL** - Banco de dados
- **Whitenoise** - Servir arquivos estáticos

### Cliente Desktop
- **MediaPipe FaceLandmarker** - Detecção facial e landmarks 3D (478 pontos)
- **OpenCV (cv2)** - Captura e processamento de vídeo
- **NumPy** - Cálculos de similaridade (cosseno)
- **Tkinter** - Interface gráfica nativa
- **Pillow (PIL)** - Manipulação de imagens
- **Requests** - Comunicação HTTP com API

### Build e Deploy
- **PyInstaller** - Compilação para executável (.exe)
- **PowerShell Scripts** - Automação de inicialização
- **Configuração automática de IP** - Detecção de rede

## 📖 Documentação Adicional

- **[GUIA_RAPIDO.md](GUIA_RAPIDO.md)** - Guia rápido de configuração e uso
- **[QUICKSTART.md](QUICKSTART.md)** - Início rápido
- **[PASSO_A_PASSO.txt](PASSO_A_PASSO.txt)** - Tutorial passo a passo

### Parâmetros Configuráveis

**Face Engine (`face_engine.py`):**
- `SIMILARITY_THRESHOLD` (0.80) - Limiar de similaridade
- `COOLDOWN_SECONDS` (60) - Intervalo entre registros
- `NUM_CAPTURE_FRAMES` (15) - Frames para cadastro

**API Client (`config.ini`):**
- `BASE_URL` - Endereço do servidor
- `TIMEOUT` - Timeout de requisições
- `CAMERA_INDEX` - Índice da câmera
- `THRESHOLD` - Threshold de reconhecimento

## 🔒 Segurança

- ⚠️ **NUNCA** commite `config.ini`, `.env` ou `db.sqlite3`
- 🔑 Gere uma `SECRET_KEY` única para produção
- 🔐 Use HTTPS em produção
- 🛡️ Configure firewall adequadamente
- 🚫 Desabilite DEBUG em produção

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## ✨ Autor

Desenvolvido para controle de ponto eletrônico empresarial.

## 🐛 Problemas e Sugestões

Encontrou um bug ou tem uma sugestão? Abra uma [issue](https://github.com/seu-usuario/reconhecimento_facial/issues)!

---

**Nota:** Na primeira execução, modelos de ML (~4MB) serão baixados automaticamente do Google Storage.
