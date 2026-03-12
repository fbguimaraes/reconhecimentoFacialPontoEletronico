"""
Script para popular o banco de dados com dados mocados para demonstração.
Execute: python manage.py shell < populate_mock_data.py
Ou: python populate_mock_data.py
"""
import os
import sys
import django
from datetime import datetime, timedelta, time
import random
import numpy as np
import pickle

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from employees.models import Employee, FaceEmbedding, TimeLog
from django.utils import timezone

def create_random_embedding():
    """Cria um embedding facial aleatório normalizado."""
    embedding = np.random.randn(128).astype(np.float32)
    # Normalizar
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding = embedding / norm
    return embedding

def populate_employees():
    """Cria funcionários de exemplo."""
    employees_data = [
        {"emp_id": "001", "name": "João Silva", "department": "TI", "position": "Desenvolvedor"},
        {"emp_id": "002", "name": "Maria Santos", "department": "RH", "position": "Gerente"},
        {"emp_id": "003", "name": "Pedro Costa", "department": "TI", "position": "DevOps"},
        {"emp_id": "004", "name": "Ana Oliveira", "department": "Financeiro", "position": "Analista"},
        {"emp_id": "005", "name": "Carlos Pereira", "department": "TI", "position": "Tech Lead"},
        {"emp_id": "006", "name": "Lucia Fernandes", "department": "Marketing", "position": "Coordenadora"},
        {"emp_id": "007", "name": "Roberto Alves", "department": "Vendas", "position": "Vendedor"},
        {"emp_id": "008", "name": "Fernanda Lima", "department": "TI", "position": "QA"},
        {"emp_id": "009", "name": "Paulo Souza", "department": "Operações", "position": "Supervisor"},
        {"emp_id": "010", "name": "Juliana Rocha", "department": "RH", "position": "Analista"},
        {"emp_id": "011", "name": "Ricardo Gomes", "department": "TI", "position": "Arquiteto"},
        {"emp_id": "012", "name": "Camila Dias", "department": "Financeiro", "position": "Controller"},
        {"emp_id": "013", "name": "Bruno Martins", "department": "TI", "position": "Estagiário"},
        {"emp_id": "014", "name": "Patricia Cunha", "department": "Marketing", "position": "Designer"},
        {"emp_id": "015", "name": "Marcos Ribeiro", "department": "Vendas", "position": "Gerente"},
    ]
    
    created = []
    for emp_data in employees_data:
        employee, created_flag = Employee.objects.get_or_create(
            emp_id=emp_data["emp_id"],
            defaults={
                "name": emp_data["name"],
                "department": emp_data["department"],
                "position": emp_data["position"],
                "is_active": True
            }
        )
        
        # Criar embedding facial
        if created_flag or not hasattr(employee, 'face_embedding'):
            embedding = create_random_embedding()
            FaceEmbedding.objects.update_or_create(
                employee=employee,
                defaults={'embedding_data': pickle.dumps(embedding)}
            )
        
        created.append(employee)
        status = "criado" if created_flag else "já existe"
        print(f"✓ Funcionário {employee.emp_id} - {employee.name} ({status})")
    
    return created

def populate_time_logs(employees):
    """Cria registros de ponto para os últimos 30 dias."""
    today = timezone.now().date()
    
    # Horários de entrada típicos (com variação)
    entry_times = [
        time(8, 0), time(8, 15), time(8, 30), time(8, 45),
        time(9, 0), time(9, 15), time(7, 45), time(7, 30)
    ]
    
    # Horários de saída típicos (com variação)
    exit_times = [
        time(17, 0), time(17, 30), time(18, 0), time(18, 30),
        time(19, 0), time(17, 15), time(18, 45), time(19, 30)
    ]
    
    logs_created = 0
    
    # Criar logs para os últimos 30 dias
    for days_ago in range(30):
        date = today - timedelta(days=days_ago)
        
        # Pular finais de semana
        if date.weekday() >= 5:  # 5=sábado, 6=domingo
            continue
        
        for employee in employees:
            # 85% de chance de ter registro (simula faltas ocasionais)
            if random.random() < 0.85:
                # Escolher horário aleatório
                entry = random.choice(entry_times)
                exit = random.choice(exit_times)
                
                # Adicionar pequena variação
                entry_minutes = entry.hour * 60 + entry.minute + random.randint(-10, 10)
                exit_minutes = exit.hour * 60 + exit.minute + random.randint(-15, 15)
                
                # Garantir valores válidos
                entry_minutes = max(0, min(1439, entry_minutes))
                exit_minutes = max(0, min(1439, exit_minutes))
                
                entry_time = time(entry_minutes // 60, entry_minutes % 60)
                exit_time = time(exit_minutes // 60, exit_minutes % 60)
                
                # 10% de chance de não ter saída registrada (trabalho em andamento)
                has_exit = random.random() > 0.1 or days_ago > 0  # Sempre completo se não for hoje
                
                # Criar ou atualizar log
                TimeLog.objects.update_or_create(
                    employee=employee,
                    date=date,
                    defaults={
                        'entry_time': entry_time,
                        'exit_time': exit_time if has_exit else None,
                        'entry_confidence': round(random.uniform(0.75, 0.99), 2),
                        'exit_confidence': round(random.uniform(0.75, 0.99), 2) if has_exit else None
                    }
                )
                logs_created += 1
    
    print(f"\n✓ {logs_created} registros de ponto criados para os últimos 30 dias")
    return logs_created

def create_today_varied_status(employees):
    """Cria diferentes status para hoje (alguns entraram, outros não, etc)."""
    today = timezone.now().date()
    
    # Limpar registros de hoje primeiro
    TimeLog.objects.filter(date=today).delete()
    
    scenarios = [
        # 40% entrou e saiu
        ("completed", 6),
        # 30% só entrou
        ("only_entry", 5),
        # 30% ausente
        ("absent", 4),
    ]
    
    employee_index = 0
    
    for scenario_type, count in scenarios:
        for _ in range(min(count, len(employees) - employee_index)):
            employee = employees[employee_index]
            
            if scenario_type == "completed":
                # Entrada e saída
                entry = time(random.randint(7, 9), random.randint(0, 59))
                exit = time(random.randint(17, 19), random.randint(0, 59))
                TimeLog.objects.create(
                    employee=employee,
                    date=today,
                    entry_time=entry,
                    exit_time=exit,
                    entry_confidence=round(random.uniform(0.80, 0.99), 2),
                    exit_confidence=round(random.uniform(0.80, 0.99), 2)
                )
                print(f"  {employee.name}: ENTRADA {entry.strftime('%H:%M')} | SAÍDA {exit.strftime('%H:%M')}")
                
            elif scenario_type == "only_entry":
                # Só entrada
                entry = time(random.randint(7, 9), random.randint(0, 59))
                TimeLog.objects.create(
                    employee=employee,
                    date=today,
                    entry_time=entry,
                    exit_time=None,
                    entry_confidence=round(random.uniform(0.80, 0.99), 2),
                    exit_confidence=None
                )
                print(f"  {employee.name}: ENTRADA {entry.strftime('%H:%M')} (sem saída)")
                
            # Se absent, não cria nada
            else:
                print(f"  {employee.name}: AUSENTE")
            
            employee_index += 1
    
    print(f"\n✓ Status variados criados para hoje")

def main():
    print("========================================")
    print("   POPULANDO BANCO COM DADOS MOCADOS")
    print("========================================\n")
    
    print("1. Criando funcionários...")
    employees = populate_employees()
    
    print(f"\n2. Criando registros históricos (últimos 30 dias)...")
    populate_time_logs(employees)
    
    print(f"\n3. Criando cenários variados para hoje...")
    create_today_varied_status(employees)
    
    print("\n========================================")
    print("   ✅ DADOS MOCADOS CRIADOS COM SUCESSO!")
    print("========================================")
    print(f"\n📊 Total de funcionários: {Employee.objects.count()}")
    print(f"📋 Total de registros: {TimeLog.objects.count()}")
    print(f"👥 Presentes hoje: {TimeLog.objects.filter(date=timezone.now().date(), entry_time__isnull=False).count()}")
    print(f"\n🌐 Acesse o dashboard em: http://localhost:8000/")
    print(f"🔧 Admin panel em: http://localhost:8000/admin/")

if __name__ == '__main__':
    main()
