"""
Script de migração de dados do formato CSV/Pickle para o Django.

Este script lê os dados existentes dos arquivos:
- data/embeddings.pkl (funcionários e embeddings faciais)
- data/registros.csv (logs de entrada/saída)

E os importa para o banco de dados Django via API.
"""

import os
import sys
import csv
import pickle
from pathlib import Path
from datetime import datetime
import requests

# Adicionar o diretório raiz ao path
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

# Configurações
DATA_DIR = BASE_DIR / "data"
EMBEDDINGS_PATH = DATA_DIR / "embeddings.pkl"
LOG_PATH = DATA_DIR / "registros.csv"
API_BASE_URL = "http://localhost:8000/api"


def load_legacy_data():
    """Carrega dados do formato antigo (pickle e CSV)."""
    # Carregar embeddings
    embeddings_db = {}
    if EMBEDDINGS_PATH.exists():
        try:
            with open(EMBEDDINGS_PATH, "rb") as f:
                embeddings_db = pickle.load(f)
            print(f"✓ Carregados {len(embeddings_db)} funcionários do arquivo embeddings.pkl")
        except Exception as e:
            print(f"✗ Erro ao carregar embeddings: {e}")
    else:
        print(f"✗ Arquivo {EMBEDDINGS_PATH} não encontrado")
    
    # Carregar logs CSV
    logs = []
    if LOG_PATH.exists():
        try:
            with open(LOG_PATH, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    logs.append(row)
            print(f"✓ Carregados {len(logs)} registros do arquivo registros.csv")
        except Exception as e:
            print(f"✗ Erro ao carregar logs: {e}")
    else:
        print(f"✗ Arquivo {LOG_PATH} não encontrado")
    
    return embeddings_db, logs


def migrate_employees(embeddings_db):
    """Migra funcionários e embeddings para o Django."""
    print("\n" + "="*60)
    print("MIGRANDO FUNCIONÁRIOS E EMBEDDINGS")
    print("="*60)
    
    url = f"{API_BASE_URL}/register-employee/"
    success_count = 0
    error_count = 0
    
    for emp_id, data in embeddings_db.items():
        name = data.get('nome', f'Funcionário {emp_id}')
        embedding = data.get('embedding')
        
        if embedding is None:
            print(f"✗ Funcionário {emp_id} ({name}) - sem embedding")
            error_count += 1
            continue
        
        # Preparar dados para a API
        # A API espera uma lista de embeddings (múltiplos frames), mas temos apenas um
        # Então enviamos o mesmo embedding 3 vezes para simular múltiplas capturas
        payload = {
            "emp_id": emp_id,
            "name": name,
            "embeddings": [embedding.tolist()] * 3,  # Triplicar para média
            "department": "",
            "position": ""
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 201:
                print(f"✓ Funcionário {emp_id} ({name}) migrado com sucesso")
                success_count += 1
            elif response.status_code == 400 and 'já existe' in response.text:
                print(f"⚠ Funcionário {emp_id} ({name}) já existe no banco")
                success_count += 1
            else:
                print(f"✗ Funcionário {emp_id} ({name}) - Erro {response.status_code}: {response.text[:100]}")
                error_count += 1
        except Exception as e:
            print(f"✗ Funcionário {emp_id} ({name}) - Erro de conexão: {e}")
            error_count += 1
    
    print(f"\nResumo: {success_count} sucessos, {error_count} erros")
    return success_count, error_count


def migrate_logs(logs):
    """Migra logs de ponto para o Django."""
    print("\n" + "="*60)
    print("MIGRANDO REGISTROS DE PONTO")
    print("="*60)
    
    # Precisamos criar os TimeLog objects diretamente via script Django
    # pois a API register-log funciona para tempo real, não para dados históricos
    print("\nAviso: Logs históricos devem ser migrados via Django Admin ou script manage.py")
    print("Criando arquivo de comandos SQL para importação manual...")
    
    # Agrupar logs por funcionário e data
    logs_grouped = {}
    for log in logs:
        emp_id = log.get('ID', '')
        date = log.get('Data', '')
        key = f"{emp_id}_{date}"
        
        if key not in logs_grouped:
            logs_grouped[key] = {
                'emp_id': emp_id,
                'name': log.get('Nome', ''),
                'date': date,
                'entry_time': log.get('Entrada', ''),
                'exit_time': log.get('Saida', ''),
            }
    
    print(f"\nTotal de {len(logs_grouped)} registros únicos para migrar")
    
    # Criar arquivo Python com script de migração Django
    migration_script = f"""
# Script de migração de logs - Execute com: python manage.py shell < migrate_logs.py
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from employees.models import Employee, TimeLog
from datetime import datetime

logs_data = {str(list(logs_grouped.values()))}

success = 0
errors = 0

for log in logs_data:
    try:
        # Buscar funcionário
        employee = Employee.objects.get(emp_id=log['emp_id'])
        
        # Converter data e horários
        date_obj = datetime.strptime(log['date'], '%Y-%m-%d').date()
        entry_time_obj = datetime.strptime(log['entry_time'], '%H:%M:%S').time() if log['entry_time'] else None
        exit_time_obj = datetime.strptime(log['exit_time'], '%H:%M:%S').time() if log['exit_time'] else None
        
        # Criar ou atualizar log
        time_log, created = TimeLog.objects.update_or_create(
            employee=employee,
            date=date_obj,
            defaults={{
                'entry_time': entry_time_obj,
                'exit_time': exit_time_obj,
                'entry_confidence': 0.5,
                'exit_confidence': 0.5 if exit_time_obj else None
            }}
        )
        
        print(f"{'Criado' if created else 'Atualizado'}: {{employee.name}} - {{date_obj}}")
        success += 1
    except Employee.DoesNotExist:
        print(f"Erro: Funcionário {{log['emp_id']}} não encontrado")
        errors += 1
    except Exception as e:
        print(f"Erro ao processar log: {{e}}")
        errors += 1

print(f"\\nResumo: {{success}} sucessos, {{errors}} erros")
"""
    
    script_path = BASE_DIR / "django_backend" / "migrate_logs.py"
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(migration_script)
    
    print(f"\n✓ Script de migração criado em: {script_path}")
    print("\nPara executar:")
    print(f"  cd {BASE_DIR / 'django_backend'}")
    print(f"  python manage.py shell < migrate_logs.py")
    
    return 0, 0


def check_api_connection():
    """Verifica se a API Django está acessível."""
    print("Verificando conexão com a API Django...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/employees/", timeout=5)
        if response.status_code == 200:
            print(f"✓ API Django está online em {API_BASE_URL}")
            return True
        else:
            print(f"✗ API retornou status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Não foi possível conectar à API: {e}")
        print("\nCertifique-se de que:")
        print("  1. O servidor Django está rodando (python manage.py runserver)")
        print("  2. A URL da API está correta (padrão: http://localhost:8000/api)")
        return False


def main():
    """Executa a migração completa."""
    print("="*60)
    print("MIGRAÇÃO DE DADOS - CSV/Pickle → Django")
    print("="*60)
    
    # Verificar conexão com API
    if not check_api_connection():
        print("\n✗ Migração abortada. Inicie o servidor Django primeiro.")
        return
    
    # Carregar dados antigos
    embeddings_db, logs = load_legacy_data()
    
    if not embeddings_db and not logs:
        print("\n✗ Nenhum dado encontrado para migrar")
        return
    
    # Migrar funcionários
    if embeddings_db:
        emp_success, emp_errors = migrate_employees(embeddings_db)
    else:
        emp_success, emp_errors = 0, 0
    
    # Migrar logs
    if logs:
        log_success, log_errors = migrate_logs(logs)
    else:
        log_success, log_errors = 0, 0
    
    # Resumo final
    print("\n" + "="*60)
    print("RESUMO DA MIGRAÇÃO")
    print("="*60)
    print(f"Funcionários migrados: {emp_success}")
    print(f"Logs preparados para migração: {len(logs)}")
    print(f"\n✓ Migração de funcionários concluída!")
    print(f"⚠ Execute o script de migração de logs conforme instruções acima")


if __name__ == "__main__":
    main()
