# 🚀 Comandos Git Rápidos

Comandos úteis para gerenciar o repositório no GitHub.

## 📦 Primeiro Push (Configuração Inicial)

```bash
# 1. Inicializar repositório (se ainda não foi)
git init

# 2. Adicionar todos os arquivos
git add .

# 3. Ver o que será commitado
git status

# 4. Commit inicial
git commit -m "feat: initial commit - sistema completo de reconhecimento facial"

# 5. Adicionar repositório remoto (criar no GitHub primeiro!)
git remote add origin https://github.com/SEU-USUARIO/reconhecimento-facial.git

# 6. Renomear branch para main
git branch -M main

# 7. Push inicial
git push -u origin main
```

## 🔄 Comandos Diários

### Adicionar e Commitar Mudanças

```bash
# Ver status
git status

# Adicionar arquivos específicos
git add arquivo.py outro_arquivo.py

# Ou adicionar tudo
git add .

# Commit com mensagem
git commit -m "feat: adiciona nova funcionalidade"

# Push para GitHub
git push
```

### Ver Histórico

```bash
# Histórico resumido
git log --oneline

# Histórico detalhado
git log

# Histórico gráfico
git log --graph --oneline --all
```

## 🌿 Branches

### Criar e Trabalhar com Branches

```bash
# Criar nova branch
git checkout -b feature/minha-feature

# Trocar de branch
git checkout main

# Listar branches
git branch

# Deletar branch local
git branch -d feature/minha-feature

# Push de branch para GitHub
git push -u origin feature/minha-feature
```

### Merge de Branches

```bash
# Voltar para main
git checkout main

# Atualizar main
git pull

# Fazer merge da feature
git merge feature/minha-feature

# Push do merge
git push
```

## 🔙 Desfazer Mudanças

### Antes do Commit

```bash
# Desfazer mudanças em arquivo específico
git checkout -- arquivo.py

# Remover arquivo do staging
git reset HEAD arquivo.py

# Desfazer tudo (cuidado!)
git reset --hard HEAD
```

### Depois do Commit (antes do push)

```bash
# Desfazer último commit (mantém mudanças)
git reset --soft HEAD~1

# Desfazer último commit (descarta mudanças)
git reset --hard HEAD~1

# Modificar último commit
git commit --amend -m "nova mensagem"
```

### Depois do Push

```bash
# Reverter commit específico (cria novo commit)
git revert <commit-hash>

# Push do revert
git push
```

## 🔍 Verificação e Limpeza

### Verificar Estado

```bash
# Ver mudanças não commitadas
git diff

# Ver mudanças entre commits
git diff HEAD~1 HEAD

# Ver arquivos que serão incluídos no próximo commit
git diff --cached
```

### Limpeza

```bash
# Remover arquivos não rastreados
git clean -n  # Ver o que será removido
git clean -f  # Remover

# Limpar branches remotas deletadas
git fetch --prune

# Ver tamanho do repositório
git count-objects -vH
```

## 🏷️ Tags e Releases

### Criar Tags

```bash
# Tag simples
git tag v1.0.0

# Tag anotada (recomendado)
git tag -a v1.0.0 -m "Versão 1.0.0 - Release inicial"

# Listar tags
git tag

# Push de tag específica
git push origin v1.0.0

# Push de todas as tags
git push --tags
```

### Deletar Tags

```bash
# Deletar tag local
git tag -d v1.0.0

# Deletar tag remota
git push origin --delete v1.0.0
```

## 🔄 Sincronização

### Atualizar seu Repositório Local

```bash
# Buscar mudanças do GitHub
git fetch

# Baixar e fazer merge
git pull

# Pull com rebase (mantém histórico limpo)
git pull --rebase
```

### Sincronizar Fork

```bash
# Adicionar upstream (fazer uma vez)
git remote add upstream https://github.com/ORIGINAL-REPO/reconhecimento-facial.git

# Buscar mudanças do upstream
git fetch upstream

# Merge do upstream/main no seu main
git checkout main
git merge upstream/main

# Push para seu fork
git push
```

## 🔥 Comandos Avançados

### Stash (Guardar Mudanças Temporariamente)

```bash
# Salvar mudanças
git stash

# Listar stashes
git stash list

# Aplicar último stash
git stash pop

# Aplicar stash específico
git stash apply stash@{0}

# Deletar stash
git stash drop stash@{0}
```

### Rebase Interativo

```bash
# Rebase dos últimos 3 commits
git rebase -i HEAD~3

# Durante rebase:
# pick = manter commit
# reword = mudar mensagem
# squash = juntar com anterior
# drop = descartar
```

### Cherry Pick

```bash
# Aplicar commit específico de outra branch
git cherry-pick <commit-hash>
```

## 🛡️ Segurança

### Remover Arquivo Sensível do Histórico

```bash
# Método 1: filter-branch (Git antigo)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch config.ini" \
  --prune-empty --tag-name-filter cat -- --all

# Método 2: filter-repo (recomendado)
# Instale: pip install git-filter-repo
git filter-repo --path config.ini --invert-paths

# Force push (cuidado!)
git push origin --force --all
git push origin --force --tags
```

### Verificar Arquivos Grandes

```bash
# Listar 10 maiores arquivos no histórico
git rev-list --objects --all | \
  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | \
  awk '/^blob/ {print substr($0,6)}' | \
  sort --numeric-sort --key=2 | \
  tail -10
```

## 🔧 Configuração

### Configurar Git

```bash
# Nome e email (global)
git config --global user.name "Seu Nome"
git config --global user.email "seu@email.com"

# Editor padrão
git config --global core.editor "code --wait"

# Cores
git config --global color.ui auto

# Lista todas as configurações
git config --list
```

### Aliases Úteis

```bash
# Criar aliases
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.last 'log -1 HEAD'
git config --global alias.unstage 'reset HEAD --'

# Usar: git st (ao invés de git status)
```

## 📊 Estatísticas

```bash
# Ver contribuições por autor
git shortlog -sn

# Ver número de commits por autor
git log --author="Seu Nome" --oneline | wc -l

# Ver mudanças por arquivo
git log --stat

# Ver autores de cada linha de arquivo
git blame arquivo.py
```

## 🚨 Solução de Problemas

### Conflito de Merge

```bash
# Ver arquivos em conflito
git status

# Após resolver conflitos manualmente:
git add arquivo_resolvido.py
git commit

# Abortar merge
git merge --abort
```

### Recuperar Commit Deletado

```bash
# Ver histórico de referências
git reflog

# Recuperar
git cherry-pick <commit-hash>
```

### Resolver "detached HEAD"

```bash
# Criar branch do estado atual
git checkout -b recuperar-trabalho

# Ou voltar para main
git checkout main
```

## 📖 Referências Rápidas

### Conventional Commits

```bash
feat:     nova funcionalidade
fix:      correção de bug
docs:     documentação
style:    formatação
refactor: refatoração
test:     testes
chore:    manutenção
```

### Gitignore Patterns

```
# Arquivo específico
config.ini

# Diretório
node_modules/

# Extensão
*.log

# Exceção
!important.log
```

---

💡 **Dica:** Use `git help <comando>` para ver documentação detalhada de qualquer comando!
