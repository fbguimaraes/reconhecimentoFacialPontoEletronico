# 🤖 PROMPT PARA COPILOT - CONFIGURAÇÃO AUTOMÁTICA

Copie e cole este prompt no GitHub Copilot para configurar tudo automaticamente:

---

## 📋 PROMPT COMPLETO

```
Preciso que você configure completamente o Sistema de Reconhecimento Facial para uso imediato. 

TAREFAS A EXECUTAR AUTOMATICAMENTE:

1. VERIFICAÇÃO DE DOCUMENTAÇÃO:
   - Leia todos os arquivos .md do projeto (README.md, INSTALLATION.md, QUICKSTART_CLONE.md, etc.)
   - Identifique todos os pré-requisitos e passos necessários
   - Crie um plano de execução baseado na documentação

2. VERIFICAÇÃO DE AMBIENTE:
   - Verifique se Python está instalado e qual versão
   - Verifique se o ambiente virtual 'env' existe
   - Verifique quais dependências já estão instaladas
   - Liste o que falta configurar

3. CONFIGURAÇÃO AUTOMÁTICA:
   - Crie ou ative o ambiente virtual se necessário
   - Copie arquivos .example para arquivos de configuração (.env, config.ini)
   - Gere SECRET_KEY do Django automaticamente e insira no .env
   - Configure ALLOWED_HOSTS com IPs relevantes (localhost, 127.0.0.1, IP da rede local)
   - Configure config.ini com valores padrão apropriados

4. INSTALAÇÃO DE DEPENDÊNCIAS:
   - Instale todas as dependências do django_backend (pip install -r requirements.txt)
   - Instale todas as dependências do cliente (pip install -r requirements.txt na raiz)
   - Confirme que todas as instalações foram bem-sucedidas

5. CONFIGURAÇÃO DO BANCO DE DADOS:
   - Execute python manage.py migrate
   - Ofereça criar superusuário (perguntar antes)
   - Execute python manage.py collectstatic (se necessário)

6. SCRIPTS POWERSHELL:
   - Identifique todos os scripts .ps1 disponíveis
   - Execute ConfigurarInicializacao.ps1 (se existir e for apropriado)
   - Configure firewall se necessário (configurar_firewall.ps1)

7. VERIFICAÇÃO FINAL:
   - Teste se o servidor Django inicia sem erros
   - Teste se o cliente desktop abre sem erros
   - Verifique conectividade com a API
   - Verifique se a webcam é detectada
   - Liste o IP da rede local detectado

8. RELATÓRIO FINAL:
   - Mostre um resumo de tudo que foi configurado
   - Liste os comandos para iniciar servidor e cliente
   - Indique possíveis problemas encontrados
   - Forneça próximos passos

IMPORTANTE:
- Execute tudo automaticamente sempre que possível
- Pergunte apenas quando necessário (ex: criar superusuário)
- Use PowerShell para executar comandos no Windows
- Confirme cada etapa antes de prosseguir para a próxima
- Se encontrar erros, tente resolver automaticamente primeiro
- Ao final, deixe o sistema 100% pronto para uso imediato

OBJETIVO FINAL:
Após executar este prompt, eu devo poder apenas:
1. Executar um comando para iniciar o servidor
2. Executar um comando para iniciar o cliente
3. Começar a usar o sistema imediatamente

Comece agora pela verificação da documentação e prossiga com todas as etapas.
```

---

## 🎯 VERSÃO RESUMIDA (Alternativa)

Se preferir um prompt mais curto:

```
Leia toda a documentação .md do projeto (README.md, INSTALLATION.md, etc.), execute TODOS os passos de instalação e configuração automaticamente, incluindo:

- Criar/ativar ambiente virtual
- Instalar todas as dependências (servidor + cliente)
- Copiar e configurar .env e config.ini com valores apropriados
- Gerar SECRET_KEY automaticamente
- Executar migrações Django
- Executar scripts .ps1 necessários
- Testar se tudo funciona

Deixe o sistema 100% pronto para uso. Ao final, me diga apenas quais comandos executar para iniciar servidor e cliente.
```

---

## 📝 COMO USAR

1. **Copie o prompt acima** (versão completa ou resumida)
2. **Cole no chat do GitHub Copilot**
3. **Aguarde a execução automática**
4. **Siga as instruções finais** para iniciar o sistema

---

## ⚙️ CONFIGURAÇÕES QUE SERÃO FEITAS AUTOMATICAMENTE

### .env (django_backend/)
```ini
SECRET_KEY=<gerado automaticamente>
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,<IP-rede-local>
```

### config.ini (raiz)
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

---

## 🚀 RESULTADO ESPERADO

Após executar o prompt, você terá:

✅ Ambiente virtual criado e ativado
✅ Todas as dependências instaladas
✅ Arquivos de configuração criados e preenchidos
✅ SECRET_KEY gerada automaticamente
✅ Banco de dados migrado
✅ Sistema testado e funcionando
✅ Comandos prontos para iniciar servidor e cliente

---

## 💡 DICA

Se o Copilot pedir confirmação em algum ponto:
- **Criar superusuário?** → Responda "sim" se quiser acessar o admin Django
- **Executar script de firewall?** → Responda "sim" se for usar em rede local
- **Executar ConfigurarInicializacao.ps1?** → Responda "sim" se quiser inicialização automática

---

## 🔄 SE ALGO DER ERRADO

Use este prompt adicional:

```
Algo deu errado na configuração. Por favor:

1. Verifique os logs de erro
2. Resolva automaticamente os problemas encontrados
3. Continue de onde parou
4. Me informe o que foi corrigido

Continue até deixar o sistema funcionando 100%.
```

---

**Pronto! Copie e cole no Copilot e deixe a mágica acontecer! 🪄✨**
