# 🚀 GUIA RÁPIDO DE INÍCIO

## Setup Inicial (Primeira vez)

### 1. Instalar Django Backend

```powershell
.\setup_django.ps1
```

Depois crie o superusuário:

```powershell
cd django_backend
python manage.py createsuperuser
```

### 2. Iniciar o Servidor Django

```powershell
.\start_django.ps1
```

Ou manualmente:

```powershell
cd django_backend
python manage.py runserver
```

### 3. Acessar o Sistema

- **Dashboard**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/
- **API REST**: http://localhost:8000/api/

### 4. Iniciar Interface de Reconhecimento

```powershell
.\start_facial_recognition.ps1
```

Ou manualmente:

```powershell
python main.py
```

---

## Migrar Dados Antigos (Opcional)

Se você já tem dados no formato CSV/Pickle:

```powershell
# 1. Certifique-se que Django está rodando
.\start_django.ps1

# 2. Em outro terminal, execute a migração
python migrate_to_django.py

# 3. Migrar logs históricos
cd django_backend
python manage.py shell < migrate_logs.py
```

---

## Usar API em vez de CSV/Pickle

Edite o arquivo `main.py` na linha 18:

**DE:**
```python
from face_engine import FaceEngine
```

**PARA:**
```python
from face_engine_api import FaceEngine
```

---

## Integração com BitDogLab (MQTT)

### 1. Instalar broker MQTT

**Windows:**
- Download: https://mosquitto.org/download/
- Instalar e executar

**Python (alternativa):**
```powershell
pip install paho-mqtt
```

### 2. Configurar MicroPython na BitDogLab

1. Abra o arquivo `bitdoglab_mqtt_subscriber.py`
2. Configure WiFi (linhas 20-21):
   ```python
   WIFI_SSID = "SUA_REDE"
   WIFI_PASSWORD = "SUA_SENHA"
   ```
3. Configure IP do broker (linha 24):
   ```python
   MQTT_BROKER = "192.168.1.XXX"  # IP do PC com Django
   ```
4. Upload para BitDogLab usando Thonny IDE

### 3. Habilitar MQTT no Sistema

Adicione no início do `face_engine_api.py`:

```python
from mqtt_integration import MQTTPublisher

class FaceEngine:
    def __init__(self, api_url=None):
        # ... código existente ...
        
        # Inicializar MQTT
        try:
            self.mqtt = MQTTPublisher(broker_host="localhost")
        except:
            self.mqtt = None
```

E nos métodos de log:

```python
def log_entry(self, emp_id, name, confidence):
    response = self._register_log(emp_id, 'entrada', confidence)
    if self.mqtt:
        self.mqtt.publish_recognition_success(emp_id, name, 'entrada', confidence)
    return response
```

---

## Estrutura do Projeto

```
reconhecimento_facial/
├── django_backend/          # Backend Django
│   ├── config/             # Configurações Django
│   ├── employees/          # App de funcionários e API
│   ├── dashboard/          # App do dashboard web
│   ├── manage.py
│   └── db.sqlite3
│
├── data/                   # Dados legados (CSV/Pickle)
├── models/                 # Modelos de ML baixados
│
├── face_engine.py          # Engine legado (CSV/Pickle)
├── face_engine_api.py      # Engine com Django API
├── main.py                 # Interface Tkinter
│
├── mqtt_integration.py     # Integração MQTT
├── bitdoglab_mqtt_subscriber.py  # Código para BitDogLab
│
├── setup_django.ps1        # Setup automático
├── start_django.ps1        # Iniciar Django
├── start_facial_recognition.ps1  # Iniciar interface
│
└── migrate_to_django.py    # Migração de dados
```

---

## Comandos Úteis

### Django

```powershell
# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Shell interativo
python manage.py shell

# Coletar arquivos estáticos
python manage.py collectstatic
```

### API REST

```powershell
# Listar funcionários
Invoke-WebRequest http://localhost:8000/api/employees/

# Ver logs de hoje
Invoke-WebRequest http://localhost:8000/api/logs/today/

# Estatísticas do dashboard
Invoke-WebRequest http://localhost:8000/api/dashboard/stats/
```

---

## Troubleshooting

### Erro: "API não está acessível"

1. Verifique se Django está rodando: `.\start_django.ps1`
2. Teste a API: http://localhost:8000/api/

### Erro: "CSRF token missing"

- Configure `CORS_ALLOW_ALL_ORIGINS = True` em `settings.py`

### Erro: "No module named 'employees'"

- Execute as migrações: `python manage.py migrate`

### Dashboard em branco

- Cadastre funcionários primeiro via Admin ou API
- Faça alguns registros de ponto

---

## Próximos Passos

1. ✅ Setup inicial concluído
2. ✅ Dashboard funcionando
3. ⬜ Integrar com MQTT/BitDogLab
4. ⬜ Deploy em produção
5. ⬜ Configurar PostgreSQL
6. ⬜ Adicionar autenticação JWT

---

## Suporte

- Documentação completa: `DJANGO_INTEGRATION.md`
- Admin Django: http://localhost:8000/admin/
- API Browsable: http://localhost:8000/api/

**Sistema pronto para uso industrial! 🎉**
