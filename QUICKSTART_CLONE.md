# ⚡ QUICK START

Guia ultra-rápido para rodar o sistema após clonar.

## 🎯 5 Minutos Para Rodar

```bash
# 1. Clone e entre na pasta
git clone https://github.com/SEU-USUARIO/reconhecimento-facial.git
cd reconhecimento-facial

# 2. Crie ambiente virtual
python -m venv env

# 3. Ative o ambiente
.\env\Scripts\Activate.ps1  # Windows
# source env/bin/activate    # Linux/Mac

# 4. Instale dependências do servidor
cd django_backend
pip install -r requirements.txt

# 5. Configure (copie e edite)
copy .env.example .env
# Edite .env e adicione SECRET_KEY

# 6. Inicie banco de dados
python manage.py migrate

# 7. Rode o servidor
python manage.py runserver 0.0.0.0:8000
```

**Servidor rodando em:** http://localhost:8000/

---

## 🖥️ Cliente Desktop (Opcional)

**Novo terminal:**

```bash
cd reconhecimento-facial
.\env\Scripts\Activate.ps1
pip install -r requirements.txt
copy config.ini.example config.ini
python main.py
```

---

## 🔑 Gerar SECRET_KEY

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copie o resultado e cole no `.env`:
```ini
SECRET_KEY=resultado-aqui
```

---

## 📖 Documentação Completa

- **[INSTALLATION.md](INSTALLATION.md)** - Guia completo passo a passo
- **[README.md](README.md)** - Visão geral do projeto

---

**Pronto! 🚀**
