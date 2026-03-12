# 📦 Preparação para GitHub - Checklist

Este arquivo contém todos os passos necessários para preparar o projeto para ser publicado no GitHub.

## ✅ Checklist Completa

### 1. Limpeza de Arquivos

- [x] `.gitignore` criado e configurado
- [ ] Remover arquivos temporários e builds:
  ```powershell
  # Remover builds
  Remove-Item -Recurse -Force build, dist, *.egg-info -ErrorAction SilentlyContinue
  
  # Remover caches Python
  Get-ChildItem -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force
  Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force
  
  # Remover dados locais (se existirem)
  Remove-Item -Recurse -Force data -ErrorAction SilentlyContinue
  Remove-Item -Recurse -Force logs -ErrorAction SilentlyContinue
  ```

### 2. Arquivos Sensíveis

- [x] `.env.example` criado
- [x] `config.ini.example` criado
- [ ] Verificar que NÃO existem no repositório:
  - [ ] `config.ini`
  - [ ] `.env`
  - [ ] `db.sqlite3`
  - [ ] `SECRET_KEY` hardcoded
  - [ ] Senhas ou tokens
  - [ ] Dados pessoais

### 3. Documentação

- [x] `README.md` principal atualizado
- [x] `django_backend/README.md` criado
- [x] `LICENSE` criado
- [x] `CONTRIBUTING.md` criado
- [ ] Verificar se todos os links estão corretos
- [ ] Revisar gramática e ortografia

### 4. Configuração Git

- [ ] Inicializar repositório (se ainda não foi):
  ```bash
  git init
  ```

- [ ] Adicionar arquivos:
  ```bash
  git add .
  ```

- [ ] Primeiro commit:
  ```bash
  git commit -m "feat: initial commit - sistema de reconhecimento facial"
  ```

### 5. Criar Repositório no GitHub

- [ ] Acessar https://github.com/new
- [ ] Nome: `reconhecimento-facial` ou similar
- [ ] Descrição: "Sistema de Ponto Eletrônico com Reconhecimento Facial usando MediaPipe, Django e OpenCV"
- [ ] Público ou Privado (sua escolha)
- [ ] **NÃO** adicionar README, .gitignore ou LICENSE (já temos)

### 6. Conectar ao Repositório Remoto

```bash
# Adicionar remote
git remote add origin https://github.com/SEU-USUARIO/reconhecimento-facial.git

# Verificar remote
git remote -v

# Push inicial
git branch -M main
git push -u origin main
```

### 7. Configurações do Repositório no GitHub

- [ ] Adicionar Topics/Tags:
  - `facial-recognition`
  - `time-tracking`
  - `django`
  - `mediapipe`
  - `opencv`
  - `python`
  - `rest-api`
  - `attendance-system`

- [ ] Adicionar descrição curta

- [ ] Habilitar Issues

- [ ] Habilitar Discussions (opcional)

- [ ] Adicionar imagem social (screenshot do sistema)

### 8. Proteção de Branch

- [ ] Proteger branch `main`:
  - Settings → Branches → Add rule
  - Branch name pattern: `main`
  - ✅ Require pull request reviews
  - ✅ Require status checks to pass

### 9. Secrets (se usar GitHub Actions)

- [ ] Adicionar secrets necessários:
  - Settings → Secrets and variables → Actions
  - Adicionar: `DJANGO_SECRET_KEY`, etc.

### 10. Verificação Final

- [ ] Clone em outro diretório para testar:
  ```bash
  cd ..
  git clone https://github.com/SEU-USUARIO/reconhecimento-facial.git teste
  cd teste
  ```

- [ ] Seguir passos do README para instalação
- [ ] Verificar se tudo funciona
- [ ] Verificar se nenhum arquivo sensível foi commitado

## 🚀 Comandos Resumidos

```powershell
# 1. Limpar projeto
Get-ChildItem -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force
Remove-Item -Force SERVER_INFO.txt -ErrorAction SilentlyContinue

# 2. Inicializar Git (se necessário)
git init

# 3. Adicionar arquivos
git add .

# 4. Commit inicial
git commit -m "feat: initial commit - sistema de reconhecimento facial"

# 5. Conectar ao GitHub (criar repo primeiro!)
git remote add origin https://github.com/SEU-USUARIO/reconhecimento-facial.git
git branch -M main
git push -u origin main
```

## 📝 Depois do Push

### README.md no GitHub

Atualize as URLs no README:
- Substitua `seu-usuario` pelo seu username real
- Verifique badges (se adicionar CI/CD)

### Adicionar Badges (Opcional)

No topo do README.md:

```markdown
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![Django Version](https://img.shields.io/badge/django-4.2%2B-green)
![License](https://img.shields.io/badge/license-MIT-blue)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)
```

### Screenshot

Adicione screenshots do sistema:

1. Crie pasta `screenshots/`
2. Adicione imagens (dashboard, cliente desktop)
3. Inclua no README:
```markdown
## 📸 Screenshots

![Dashboard](screenshots/dashboard.png)
![Cliente Desktop](screenshots/cliente.png)
```

### Wiki (Opcional)

Crie páginas wiki para:
- Guia de instalação detalhado
- Configuração avançada
- Troubleshooting
- FAQ

## ⚠️ Avisos Importantes

### NUNCA commite:

- ❌ Arquivos com SECRET_KEY real
- ❌ Senhas ou tokens de API
- ❌ Dados pessoais (fotos, embeddings)
- ❌ Banco de dados com dados reais
- ❌ Configurações locais (`config.ini`)
- ❌ Ambiente virtual (`env/`)
- ❌ Builds compilados grandes

### Se commitou acidentalmente:

```bash
# Remove arquivo do histórico
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch ARQUIVO_SENSIVEL" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (cuidado!)
git push origin --force --all
```

Ou use: `git-filter-repo` (mais seguro)

## 📧 Contato

Se precisar de ajuda, abra uma issue no repositório!

---

**Data de preparação:** 11/03/2026
**Status:** ✅ Pronto para GitHub
