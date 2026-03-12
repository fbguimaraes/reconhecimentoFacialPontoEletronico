"""
Views do Dashboard - Interface web para visualização de dados.
"""
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db.models import Count, Q, Sum
from datetime import datetime, timedelta
from employees.models import Employee, TimeLog


def index(request):
    """Dashboard principal com estatísticas gerais."""
    
    today = timezone.now().date()
    
    # Estatísticas gerais
    total_employees = Employee.objects.filter(is_active=True).count()
    
    # Logs de hoje
    today_logs = TimeLog.objects.filter(date=today).select_related('employee')
    employees_present = today_logs.count()
    employees_entered = today_logs.filter(exit_time__isnull=True).count()
    employees_exited = today_logs.filter(exit_time__isnull=False).count()
    
    # Últimos registros
    recent_logs = TimeLog.objects.select_related('employee').order_by('-date', '-entry_time')[:10]
    
    # Logs da semana (para gráfico)
    week_start = today - timedelta(days=6)
    week_data = []
    for i in range(7):
        day = week_start + timedelta(days=i)
        count = TimeLog.objects.filter(date=day).count()
        week_data.append({
            'date': day.strftime('%d/%m'),
            'count': count
        })
    
    # Logs do mês (por dia)
    month_start = today.replace(day=1)
    month_logs = TimeLog.objects.filter(
        date__gte=month_start,
        date__lte=today
    ).values('date').annotate(count=Count('id')).order_by('date')
    
    month_data = []
    for log in month_logs:
        month_data.append({
            'date': log['date'].strftime('%d/%m'),
            'count': log['count']
        })
    
    # Top 5 funcionários mais presentes no mês
    top_employees = TimeLog.objects.filter(
        date__gte=month_start,
        date__lte=today
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
    today = timezone.now().date()
    employees_data = []
    
    for emp in employees:
        status = emp.get_today_status()
        total_hours = emp.get_total_hours_month()
        
        employees_data.append({
            'employee': emp,
            'status': status,
            'total_hours_month': round(total_hours, 2)
        })
    
    context = {
        'employees_data': employees_data,
    }
    
    return render(request, 'dashboard/employees.html', context)


def employee_detail(request, pk):
    """Detalhes de um funcionário específico."""
    
    employee = get_object_or_404(Employee, pk=pk)
    
    today = timezone.now().date()
    month_start = today.replace(day=1)
    
    # Logs do mês atual
    month_logs = TimeLog.objects.filter(
        employee=employee,
        date__gte=month_start,
        date__lte=today
    ).order_by('-date')
    
    # Calcular total de horas
    total_hours = 0
    for log in month_logs:
        hours = log.get_worked_hours()
        if hours:
            total_hours += hours
    
    # Últimos 30 dias de registro
    last_30_days = today - timedelta(days=29)
    logs_30_days = TimeLog.objects.filter(
        employee=employee,
        date__gte=last_30_days,
        date__lte=today
    ).order_by('date')
    
    # Dados para gráfico de presença
    presence_data = []
    for i in range(30):
        day = last_30_days + timedelta(days=i)
        has_log = logs_30_days.filter(date=day).exists()
        presence_data.append({
            'date': day.strftime('%d/%m'),
            'present': 1 if has_log else 0
        })
    
    context = {
        'employee': employee,
        'status': employee.get_today_status(),
        'month_logs': month_logs,
        'total_hours': round(total_hours, 2),
        'total_days': month_logs.count(),
        'presence_data': presence_data,
    }
    
    return render(request, 'dashboard/employee_detail.html', context)


def logs_list(request):
    """Lista de todos os registros de ponto."""
    
    # Filtros
    date_from = request.GET.get('date_from', None)
    date_to = request.GET.get('date_to', None)
    employee_id = request.GET.get('employee_id', None)
    
    logs = TimeLog.objects.select_related('employee').order_by('-date', '-entry_time')
    
    if date_from:
        logs = logs.filter(date__gte=date_from)
    if date_to:
        logs = logs.filter(date__lte=date_to)
    if employee_id:
        logs = logs.filter(employee_id=employee_id)
    
    # Paginação simples: últimos 100 registros
    logs = logs[:100]
    
    employees = Employee.objects.filter(is_active=True).order_by('name')
    
    context = {
        'logs': logs,
        'employees': employees,
        'date_from': date_from,
        'date_to': date_to,
        'employee_id': employee_id,
    }
    
    return render(request, 'dashboard/logs.html', context)


def reports(request):
    """Relatórios e análises."""
    
    today = timezone.now().date()
    month_start = today.replace(day=1)
    
    # Relatório do mês
    month_logs = TimeLog.objects.filter(
        date__gte=month_start,
        date__lte=today
    ).select_related('employee')
    
    # Horas trabalhadas por funcionário
    employee_hours = {}
    for log in month_logs:
        emp_name = log.employee.name
        hours = log.get_worked_hours()
        if hours:
            if emp_name not in employee_hours:
                employee_hours[emp_name] = 0
            employee_hours[emp_name] += hours
    
    # Ordenar por horas
    employee_hours_sorted = sorted(
        employee_hours.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    # Dias com mais registros
    days_count = month_logs.values('date').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Média de horas por dia
    total_hours = sum(employee_hours.values())
    working_days = month_logs.values('date').distinct().count()
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
