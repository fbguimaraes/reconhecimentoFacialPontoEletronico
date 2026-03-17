"""
Views do Dashboard - Interface web para visualização de dados.
"""
import csv
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Count, Max
from datetime import datetime, timedelta
from employees.models import Employee, TimeLog


def index(request):
    """Dashboard principal com estatísticas gerais."""
    
    today = timezone.localdate()
    
    # Estatísticas gerais
    total_employees = Employee.objects.filter(is_active=True).count()
    
    # Funcionários que registraram algo hoje
    today_logs = TimeLog.objects.filter(data=today).select_related('employee')
    employees_present = today_logs.values('employee').distinct().count()

    # Último registro de cada funcionário hoje
    ultimos = TimeLog.objects.filter(data=today).values('employee').annotate(
        ultimo_id=Max('id')
    )
    ultimos_ids = [registro['ultimo_id'] for registro in ultimos]
    ultimos_logs = TimeLog.objects.filter(id__in=ultimos_ids)

    employees_entered = ultimos_logs.filter(tipo='entrada').count()
    employees_exited = ultimos_logs.filter(tipo='saida').count()
    
    # Últimos registros
    recent_logs = TimeLog.objects.select_related('employee').order_by('-horario')[:10]
    
    # Logs da semana (para gráfico)
    week_start = today - timedelta(days=6)
    week_data = []
    for i in range(7):
        day = week_start + timedelta(days=i)
        count = TimeLog.objects.filter(data=day).count()
        week_data.append({
            'date': day.strftime('%d/%m'),
            'count': count
        })
    
    # Logs do mês (por dia)
    month_start = today.replace(day=1)
    month_logs = TimeLog.objects.filter(
        data__gte=month_start,
        data__lte=today
    ).values('data').annotate(count=Count('id')).order_by('data')
    
    month_data = []
    for log in month_logs:
        month_data.append({
            'date': log['data'].strftime('%d/%m'),
            'count': log['count']
        })
    
    # Top 5 funcionários mais presentes no mês
    top_employees = TimeLog.objects.filter(
        data__gte=month_start,
        data__lte=today
    ).values('employee__name').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    context = {
        'total_employees': total_employees,
        'employees_present': employees_present,
        'employees_entered': employees_entered,
        'employees_exited': employees_exited,
        'recent_logs': recent_logs,
        'week_data': week_data,
        'month_data': month_data,
        'top_employees': list(top_employees),
    }
    
    return render(request, 'dashboard/index.html', context)


def employees_list(request):
    """Lista de todos os funcionários."""
    
    employees = Employee.objects.filter(is_active=True).order_by('name')
    
    # Adicionar informações de hoje para cada funcionário
    employees_data = []
    
    for emp in employees:
        status = emp.get_today_status()
        
        employees_data.append({
            'employee': emp,
            'status': status,
            'total_hours_month': 0.0
        })
    
    context = {
        'employees_data': employees_data,
    }
    
    return render(request, 'dashboard/employees.html', context)


def employee_detail(request, pk):
    """Detalhes de um funcionário específico."""
    
    employee = get_object_or_404(Employee, pk=pk)
    
    today = timezone.localdate()
    month_start = today.replace(day=1)
    
    # Logs do mês atual
    month_logs = TimeLog.objects.filter(
        employee=employee,
        data__gte=month_start,
        data__lte=today
    ).order_by('-horario')
    
    # Últimos 30 dias de registro
    last_30_days = today - timedelta(days=29)
    logs_30_days = TimeLog.objects.filter(
        employee=employee,
        data__gte=last_30_days,
        data__lte=today
    ).order_by('data')
    
    # Dados para gráfico de presença
    presence_data = []
    for i in range(30):
        day = last_30_days + timedelta(days=i)
        has_log = logs_30_days.filter(data=day).exists()
        presence_data.append({
            'date': day.strftime('%d/%m'),
            'present': 1 if has_log else 0
        })
    
    context = {
        'employee': employee,
        'status': employee.get_today_status(),
        'month_logs': month_logs,
        'total_events': month_logs.count(),
        'total_days': month_logs.values('data').distinct().count(),
        'presence_data': presence_data,
    }
    
    return render(request, 'dashboard/employee_detail.html', context)


def logs_list(request):
    """Lista de todos os registros de ponto."""

    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    emp_id = request.GET.get('employee_id')

    logs = TimeLog.objects.select_related('employee').order_by('-horario')

    if date_from:
        logs = logs.filter(data__gte=date_from)
    if date_to:
        logs = logs.filter(data__lte=date_to)
    if emp_id:
        logs = logs.filter(employee__id=emp_id)

    employees = Employee.objects.filter(is_active=True).order_by('name')

    context = {
        'logs': logs[:200],
        'employees': employees,
        'date_from': date_from or '',
        'date_to': date_to or '',
        'selected_employee': emp_id or '',
    }

    return render(request, 'dashboard/logs.html', context)


def export_csv(request):
    """Exporta registros filtrados em CSV."""
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    emp_id = request.GET.get('employee_id')

    logs = TimeLog.objects.select_related('employee').order_by('-horario')
    if date_from:
        logs = logs.filter(data__gte=date_from)
    if date_to:
        logs = logs.filter(data__lte=date_to)
    if emp_id:
        logs = logs.filter(employee__id=emp_id)

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="registros_ponto.csv"'
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow(['Funcionário', 'ID', 'Tipo', 'Data', 'Horário', 'Confiança'])

    for log in logs:
        writer.writerow([
            log.employee.name,
            log.employee.emp_id,
            log.tipo,
            log.data.strftime('%d/%m/%Y'),
            log.horario.strftime('%H:%M:%S'),
            f"{log.confidence:.2f}",
        ])

    return response


def reports(request):
    """Relatórios e análises."""
    
    today = timezone.localdate()
    month_start = today.replace(day=1)
    
    # Relatório do mês
    month_logs = TimeLog.objects.filter(
        data__gte=month_start,
        data__lte=today
    ).select_related('employee')
    
    # Horas trabalhadas por funcionário
    employee_hours = {}
    for log in month_logs:
        emp_name = log.employee.name
        if emp_name not in employee_hours:
            employee_hours[emp_name] = 0
    
    # Ordenar por horas
    employee_hours_sorted = sorted(
        employee_hours.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    # Dias com mais registros
    days_count = month_logs.values('data').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Média de horas por dia
    total_hours = 0.0
    working_days = month_logs.values('data').distinct().count()
    avg_hours_per_day = total_hours / working_days if working_days > 0 else 0
    
    context = {
        'month_start': month_start,
        'total_logs': month_logs.count(),
        'total_hours': round(total_hours, 2),
        'working_days': working_days,
        'avg_hours_per_day': round(avg_hours_per_day, 2),
        'employee_hours': employee_hours_sorted[:10],
        'days_count': days_count,
    }
    
    return render(request, 'dashboard/reports.html', context)
