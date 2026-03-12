# Contribuindo para o Sistema de Reconhecimento Facial

Agradecemos seu interesse em contribuir! Este documento fornece diretrizes para contribuições.

## 🤝 Como Contribuir

### 1. Reportar Bugs

Encontrou um bug? Abra uma [issue](https://github.com/seu-usuario/reconhecimento_facial/issues) incluindo:

- Descrição clara do problema
- Passos para reproduzir
- Comportamento esperado vs. atual
- Screenshots (se aplicável)
- Ambiente (OS, versão Python, versão do projeto)

### 2. Sugerir Melhorias

Tem uma ideia? Abra uma issue com:

- Descrição da funcionalidade
- Justificativa (por que seria útil)
- Exemplos de uso
- Possíveis alternativas consideradas

### 3. Enviar Pull Requests

#### Processo

1. **Fork** o repositório
2. **Clone** seu fork:
   ```bash
   git clone https://github.com/seu-usuario/reconhecimento_facial.git
   ```
3. **Crie uma branch** para sua feature:
   ```bash
   git checkout -b feature/MinhaFeature
   ```
4. **Faça suas alterações** seguindo os padrões do projeto
5. **Commit** suas mudanças:
   ```bash
   git commit -m "feat: adiciona MinhaFeature"
   ```
6. **Push** para sua branch:
   ```bash
   git push origin feature/MinhaFeature
   ```
7. **Abra um Pull Request** no repositório original

#### Commits Semânticos

Use conventional commits:

- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `docs:` - Documentação
- `style:` - Formatação, ponto e vírgula, etc
- `refactor:` - Refatoração de código
- `test:` - Adição de testes
- `chore:` - Manutenção, build, etc

Exemplos:
```
feat: adiciona autenticação JWT na API
fix: corrige erro ao capturar frame da webcam
docs: atualiza README com instruções de deploy
refactor: simplifica lógica de reconhecimento facial
```

## 📝 Padrões de Código

### Python

- **PEP 8**: Siga as diretrizes [PEP 8](https://pep8.org/)
- **Type Hints**: Use quando possível
- **Docstrings**: Documente funções e classes
- **Imports**: Organize usando isort

Exemplo:
```python
from typing import List, Optional
import numpy as np
from django.db import models


class Employee(models.Model):
    """
    Modelo representando um funcionário no sistema.
    
    Attributes:
        employee_id: Identificador único do funcionário
        name: Nome completo
        embedding: Vetor de características faciais
    """
    employee_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    embedding = models.JSONField(null=True, blank=True)
    
    def __str__(self) -> str:
        return f"{self.employee_id} - {self.name}"
```

### Django

- Use **Class-Based Views** quando apropriado
- **Serializers** para validação de dados
- **Migrations** para mudanças no banco
- Siga convenções do Django REST Framework

### JavaScript/Frontend

- Use **ES6+** sintaxe moderna
- **Async/await** para operações assíncronas
- Comentários claros quando necessário

## 🧪 Testes

### Executar Testes

```bash
# Backend
cd django_backend
python manage.py test

# Cliente (quando disponível)
pytest
```

### Escrever Testes

- **Cobertura**: Novos recursos devem incluir testes
- **Nomenclatura**: Use nomes descritivos
- **Isolamento**: Testes devem ser independentes

Exemplo:
```python
from django.test import TestCase
from employees.models import Employee


class EmployeeModelTestCase(TestCase):
    """Testes para o modelo Employee."""
    
    def setUp(self):
        self.employee = Employee.objects.create(
            employee_id="001",
            name="João Teste"
        )
    
    def test_employee_str_representation(self):
        """Testa representação em string do funcionário."""
        self.assertEqual(
            str(self.employee),
            "001 - João Teste"
        )
    
    def test_employee_id_unique(self):
        """Testa unicidade do employee_id."""
        with self.assertRaises(Exception):
            Employee.objects.create(
                employee_id="001",
                name="Maria Teste"
            )
```

## 📚 Documentação

### Atualizar Documentação

Ao adicionar funcionalidades, atualize:

- `README.md` - Visão geral do projeto
- `django_backend/README.md` - Documentação do backend
- `GUIA_RAPIDO.md` - Guia de uso rápido
- Docstrings no código
- Comentários em código complexo

### Estilo de Documentação

- **Clareza**: Use linguagem simples e direta
- **Exemplos**: Inclua exemplos práticos
- **Formatação**: Use Markdown adequadamente
- **Atualização**: Mantenha sincronizado com código

## 🔍 Code Review

### O que esperamos

- ✅ Código limpo e legível
- ✅ Testes passando
- ✅ Documentação atualizada
- ✅ Sem conflitos com main/master
- ✅ Commits bem descritos

### O que evitar

- ❌ Mudanças não relacionadas ao propósito do PR
- ❌ Código comentado (dead code)
- ❌ Logs de debug
- ❌ Arquivos de configuração pessoais
- ❌ Dependências desnecessárias

## 🏗️ Estrutura de Branches

- `main` - Produção estável
- `develop` - Desenvolvimento ativo
- `feature/*` - Novas funcionalidades
- `fix/*` - Correções de bugs
- `hotfix/*` - Correções urgentes em produção
- `docs/*` - Atualizações de documentação

## 📋 Checklist para PR

Antes de enviar seu Pull Request:

- [ ] Código segue padrões do projeto
- [ ] Testes adicionados/atualizados
- [ ] Todos os testes passando
- [ ] Documentação atualizada
- [ ] Commits seguem convenção semântica
- [ ] Sem conflitos com branch principal
- [ ] Descrição clara do PR
- [ ] Issues relacionadas linkadas

## 💬 Comunicação

- **Issues**: Para bugs e features
- **Pull Requests**: Para discussões sobre código
- **Discussions**: Para perguntas gerais

## 📜 Código de Conduta

- Seja respeitoso e profissional
- Aceite críticas construtivas
- Foque no que é melhor para o projeto
- Ajude outros contribuidores

## ❓ Dúvidas

Tem dúvidas sobre como contribuir? Abra uma issue com a tag `question` ou consulte a documentação existente.

---

**Obrigado por contribuir! 🎉**
