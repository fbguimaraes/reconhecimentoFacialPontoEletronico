# Django Backend - Sistema de Reconhecimento Facial

Backend Django REST API para o Sistema de Ponto Eletrônico com Reconhecimento Facial.

## 🚀 Início Rápido

### 1. Instalar Dependências

```bash
cd django_backend
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

Copie `.env.example` para `.env` e ajuste:

```bash
copy .env.example .env
```

Edite `.env`:
```ini
SECRET_KEY=sua-chave-secreta-unica
DEBUG=False
ALLOWED_HOSTS=localhost,192.168.1.100
```

### 3. Executar Migrações

```bash
python manage.py migrate
```

### 4. Criar Superusuário

```bash
python manage.py createsuperuser
```

### 5. Coletar Arquivos Estáticos

```bash
python manage.py collectstatic
```

### 6. Iniciar Servidor

```bash
# Desenvolvimento (localhost apenas)
python manage.py runserver

# Produção (todas as interfaces)
python manage.py runserver 0.0.0.0:8000
```

## 📊 Apps

### `employees`
Gerenciamento de funcionários e registros de ponto.

**Models:**
- `Employee` - Dados do funcionário (nome, matricula, foto, embedding facial)
- `TimeRecord` - Registros de entrada/saída

**Endpoints:**
- `GET /api/employees/` - Listar funcionários
- `POST /api/employees/` - Criar funcionário
- `GET /api/employees/{id}/` - Detalhes do funcionário
- `PUT/PATCH /api/employees/{id}/` - Atualizar funcionário
- `DELETE /api/employees/{id}/` - Remover funcionário
- `POST /api/employees/{id}/register_time/` - Registrar ponto
- `GET /api/time-records/` - Listar registros de ponto

### `dashboard`
Dashboard web administrativo.

**URLs:**
- `/` - Dashboard principal
- `/admin/` - Interface administrativa Django

## ⚙️ Configurações

### Arquivos de Configuração

- `config/settings.py` - Desenvolvimento
- `config/settings_production.py` - Produção

### Variáveis de Ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `SECRET_KEY` | - | Chave secreta Django (obrigatório) |
| `DEBUG` | False | Modo debug |
| `ALLOWED_HOSTS` | localhost | Hosts permitidos (separados por vírgula) |
| `DB_ENGINE` | sqlite3 | Engine do banco de dados |
| `DB_NAME` | db.sqlite3 | Nome do banco |
| `DB_USER` | - | Usuário do banco (opcional) |
| `DB_PASSWORD` | - | Senha do banco (opcional) |
| `DB_HOST` | - | Host do banco (opcional) |
| `DB_PORT` | - | Porta do banco (opcional) |

## 🗄️ Banco de Dados

### SQLite (Padrão)
Configurado automaticamente, ideal para desenvolvimento.

### PostgreSQL (Produção)

1. Instale psycopg2:
```bash
pip install psycopg2-binary
```

2. Configure no `.env`:
```ini
DB_ENGINE=django.db.backends.postgresql
DB_NAME=reconhecimento_facial
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=5432
```

3. Execute migrações:
```bash
python manage.py migrate
```

## 📝 Scripts Úteis

### Popular Dados de Teste

```bash
python populate_mock_data.py
```

### Configurar Firewall (Windows)

```powershell
.\configurar_firewall.ps1
```

### Deploy do Servidor

```powershell
.\deploy_server.ps1
```

## 🔒 Segurança em Produção

- ✅ Gere SECRET_KEY única:
  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```
- ✅ Configure `DEBUG=False`
- ✅ Defina `ALLOWED_HOSTS` corretamente
- ✅ Use HTTPS (configure reverse proxy como Nginx)
- ✅ Configure CORS apropriadamente
- ✅ Use PostgreSQL em vez de SQLite
- ✅ Configure backup do banco de dados

## 📡 API REST

### Autenticação
Por padrão, a API está aberta. Para produção, considere adicionar:
- Token Authentication
- JWT
- OAuth2

### Formato de Resposta

**Sucesso:**
```json
{
  "id": 1,
  "employee_id": "001",
  "name": "João Silva",
  "created_at": "2026-03-11T10:00:00Z"
}
```

**Erro:**
```json
{
  "detail": "Not found."
}
```

## 🧪 Testes

```bash
python manage.py test
```

## 📦 Dependências Principais

- Django 4.2+
- djangorestframework
- django-cors-headers
- Pillow
- whitenoise

## 🔧 Manutenção

### Backup do Banco

```bash
# SQLite
copy db.sqlite3 db.backup.sqlite3

# PostgreSQL
pg_dump reconhecimento_facial > backup.sql
```

### Ver Logs

```bash
# Windows
type ..\logs\server.log

# Linux
tail -f ../logs/server.log
```

## 🐛 Troubleshooting

### Porta 8000 já em uso
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux
lsof -ti:8000 | xargs kill -9
```

### Migrações com conflito
```bash
python manage.py migrate --fake
```

### Limpar sessões antigas
```bash
python manage.py clearsessions
```

---

Para mais informações, consulte a [documentação principal](../README.md).
