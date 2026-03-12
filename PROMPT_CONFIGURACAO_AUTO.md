# 🤖 PROMPT DE CONFIGURAÇÃO AUTOMÁTICA

**Copie e cole este prompt no GitHub Copilot para configurar o sistema automaticamente.**

---

## 📋 PROMPT PARA COPILOT

```
Configure automaticamente este sistema de reconhecimento facial para execução imediata.

CONTEXTO:
- Este é um sistema Django + Cliente Desktop de reconhecimento facial
- Pode ser primeira instalação OU repositório recém-clonado
- Preciso que tudo fique pronto para usar em poucos minutos

TAREFAS A EXECUTAR:

1. VERIFICAÇÃO INICIAL
   - Detectar se ambiente virtual existe (env/)
   - Verificar se config.ini existe
   - Verificar se django_backend/.env existe
   - Verificar se django_backend/db.sqlite3 existe
   - Listar o que falta configurar

2. CRIAR AMBIENTE VIRTUAL (se não existir)
   - python -m venv env
   - Confirmar criação

3. INSTALAR DEPENDÊNCIAS
   - Ativar ambiente virtual
   - pip install -r requirements.txt (raiz)
   - pip install -r django_backend/requirements.txt
   - Mostrar progresso

4. CONFIGURAR DJANGO BACKEND
   - Copiar .env.example para .env (se não existir)
   - Gerar SECRET_KEY automática
   - Atualizar .env com SECRET_KEY gerada
   - Configurar DEBUG=True
   - Detectar IP da rede e configurar ALLOWED_HOSTS
   - Executar: python manage.py migrate
   - Perguntar se quero criar superusuário (opcional)

5. CONFIGURAR CLIENTE DESKTOP
   - Copiar config.ini.example para config.ini (se não existir)
   - Detectar IP local automaticamente
   - Atualizar BASE_URL com IP detectado
   - Confirmar configuração de câmera (CAMERA_INDEX=0)

6. EXECUTAR SCRIPTS POWERSHELL (se existirem)
   - Verificar se IniciarServidorInteligente.ps1 existe
   - Perguntar se devo executar
   - Configurar inicialização automática (opcional)

7. TESTE FINAL
   - Testar importações Python essenciais
   - Verificar se modelos podem ser baixados
   - Verificar porta 8000 disponível
   - Criar relatório de status

8. INSTRUÇÕES FINAIS
   - Como iniciar servidor: cd django_backend && python manage.py runserver 0.0.0.0:8000
   - Como iniciar cliente: python main.py
   - URLs de acesso
   - Próximos passos

REGRAS:
✅ Execute comandos automaticamente quando seguro
✅ Pergunte apenas para decisões críticas (criar superusuário, etc)
✅ Use PowerShell no Windows
✅ Mostre progresso claro de cada etapa
✅ Se algo falhar, explique e sugira solução
✅ No final, mostre checklist do que foi feito
✅ Detecte e adapte-se ao SO (Windows/Linux/Mac)

FORMATO DE SAÍDA:
Para cada etapa, mostre:
[✅] ou [❌] Status
📝 Descrição do que foi feito
💡 Informações importantes

Ao final, forneça:
📊 Resumo completo
🚀 Comandos para iniciar o sistema
🔗 URLs de acesso
⚠️ Avisos importantes

COMECE AGORA A CONFIGURAÇÃO AUTOMÁTICA!
```

---

## 🎯 COMO USAR

### Opção 1: Copiar e Colar
1. Copie todo o bloco de prompt acima
2. Cole no chat do GitHub Copilot
3. Aguarde a configuração automática

### Opção 2: Prompt Curto
Se preferir um prompt mais direto:

```
Configure automaticamente todo este sistema de reconhecimento facial:
1. Crie ambiente virtual se não existir
2. Instale todas as dependências
3. Configure .env com SECRET_KEY gerada
4. Configure config.ini com IP local
5. Execute migrações Django
6. Teste tudo
7. Me diga como iniciar servidor e cliente

Faça tudo automaticamente e mostre progresso.
```

---

## 📱 PROMPT PARA APENAS RODAR (Sistema já configurado)

```
O sistema já está configurado. Preciso apenas iniciar tudo:

1. Ativar ambiente virtual (env/)
2. Iniciar servidor Django em background (django_backend/)
3. Aguardar servidor estar pronto (porta 8000)
4. Iniciar cliente desktop (main.py)
5. Mostrar URLs de acesso

Execute tudo agora!
```

---

## 🔧 PROMPT PARA RECONFIGURAÇÃO (Algo deu errado)

```
Preciso reconfigurar o sistema do zero:

PROBLEMAS:
- [Liste aqui o que não está funcionando]

AÇÕES:
1. Verificar e corrigir config.ini
2. Verificar e corrigir .env
3. Reexecutar migrações Django
4. Limpar cache Python
5. Reinstalar dependências se necessário
6. Testar cada componente

Diagnostique o problema e corrija automaticamente.
```

---

## 🎓 PROMPT PARA APRENDER (Primeiro uso)

```
Sou iniciante e acabei de clonar este repositório.

Explique E execute:
1. O que é este sistema
2. Pré-requisitos necessários
3. Instalar e configurar TUDO automaticamente
4. Como usar cada funcionalidade
5. Como resolver problemas comuns

Seja didático mas execute as configurações automaticamente.
```

---

## 🚀 PROMPT ULTRA-RÁPIDO (1 Comando)

```
Setup completo automático agora! Configure ambiente, dependências, .env, config.ini, migrations e me diga os comandos finais para rodar.
```

---

## 📊 O QUE O COPILOT VAI FAZER

Quando você usar o prompt, o Copilot irá:

### ✅ Verificações
- [x] Checar se Python está instalado
- [x] Verificar versão do Python (3.8+)
- [x] Detectar sistema operacional
- [x] Verificar se Git está instalado
- [x] Checar porta 8000 disponível

### 🔧 Configuração
- [x] Criar ambiente virtual
- [x] Instalar dependências do servidor
- [x] Instalar dependências do cliente
- [x] Gerar SECRET_KEY única
- [x] Detectar IP da rede
- [x] Criar arquivos de configuração
- [x] Executar migrações Django

### 🧪 Testes
- [x] Testar importações críticas
- [x] Verificar conectividade API
- [x] Testar acesso à webcam
- [x] Validar configurações

### 📝 Documentação
- [x] Gerar relatório de instalação
- [x] Listar comandos para execução
- [x] Mostrar URLs de acesso
- [x] Fornecer troubleshooting

---

## 🎯 CENÁRIOS ESPECÍFICOS

### Para quem acabou de clonar (Git Clone Fresh)

```
Acabei de clonar: https://github.com/fbguimaraes/reconhecimentoFacialPontoEletronico

Configure tudo do absoluto zero:
✅ Ambiente virtual
✅ Todas as dependências
✅ Arquivos de configuração com valores corretos
✅ Banco de dados Django
✅ Detectar meu IP automaticamente
✅ Executar todos os scripts necessários
✅ Testar instalação

Ao final, me diga EXATAMENTE os comandos para:
1. Iniciar o servidor
2. Iniciar o cliente desktop
3. Acessar o dashboard

EXECUTE TUDO AGORA!
```

### Para atualização após Pull

```
Acabei de fazer git pull. 

Verifique e atualize:
1. Novas dependências (requirements.txt)
2. Novas migrações Django
3. Mudanças em configuração
4. Reinstalar se necessário

Execute automaticamente o que for preciso.
```

### Para limpar e reconfigurar

```
Quero limpar tudo e reconfigurar do zero:

1. Remover db.sqlite3
2. Remover __pycache__
3. Limpar migrações (exceto __init__.py)
4. Recriar migrações
5. Reconfigurar .env e config.ini
6. Testar tudo novamente

Faça backup do necessário e execute.
```

---

## 💡 DICAS

1. **Primeira vez**: Use o prompt completo
2. **Já configurado**: Use o prompt "apenas rodar"
3. **Deu erro**: Use o prompt de reconfiguração
4. **Após git pull**: Use o prompt de atualização

---

## 🔍 VERIFICAÇÃO MANUAL (Se preferir)

Se quiser verificar manualmente antes:

```powershell
# Verificar Python
python --version

# Verificar se é clone fresco
Test-Path env/
Test-Path config.ini
Test-Path django_backend/.env

# Verificar dependências instaladas
pip list | Select-String django
```

---

## 📞 SUPORTE

Se o Copilot não conseguir configurar automaticamente:

1. Consulte [INSTALLATION.md](INSTALLATION.md)
2. Veja [QUICKSTART_CLONE.md](QUICKSTART_CLONE.md)
3. Abra uma issue: https://github.com/fbguimaraes/reconhecimentoFacialPontoEletronico/issues

---

**🤖 Desenvolvido para máxima automação com GitHub Copilot**
