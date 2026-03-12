"""
Views da API REST para o sistema de reconhecimento facial.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone
from django.db.models import Count, Q, Sum, F
from datetime import datetime, timedelta
import numpy as np

from .models import Employee, FaceEmbedding, TimeLog
from .serializers import (
    EmployeeSerializer, 
    FaceEmbeddingSerializer,
    TimeLogSerializer,
    RecognitionRequestSerializer,
    RecognitionResponseSerializer,
    RegisterLogSerializer,
    EmployeeRegistrationSerializer
)


class EmployeeViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar funcionários."""
    
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Employee.objects.all()
        
        # Filtros opcionais
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        emp_id = self.request.query_params.get('emp_id', None)
        if emp_id:
            queryset = queryset.filter(emp_id=emp_id)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """Retorna todos os logs de ponto de um funcionário."""
        employee = self.get_object()
        logs = TimeLog.objects.filter(employee=employee)
        
        # Filtros opcionais
        date_from = request.query_params.get('date_from', None)
        date_to = request.query_params.get('date_to', None)
        
        if date_from:
            logs = logs.filter(date__gte=date_from)
        if date_to:
            logs = logs.filter(date__lte=date_to)
        
        serializer = TimeLogSerializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Retorna estatísticas de um funcionário."""
        employee = self.get_object()
        
        # Total de registros
        total_logs = TimeLog.objects.filter(employee=employee).count()
        
        # Registros do mês atual
        now = timezone.now()
        month_logs = TimeLog.objects.filter(
            employee=employee,
            date__year=now.year,
            date__month=now.month
        )
        
        total_month_logs = month_logs.count()
        total_hours_month = employee.get_total_hours_month()
        
        # Dias trabalhados no mês
        days_worked = month_logs.filter(exit_time__isnull=False).count()
        
        return Response({
            'total_logs': total_logs,
            'total_month_logs': total_month_logs,
            'days_worked_month': days_worked,
            'total_hours_month': round(total_hours_month, 2),
            'today_status': employee.get_today_status()
        })


class TimeLogViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar registros de ponto."""
    
    queryset = TimeLog.objects.all().select_related('employee')
    serializer_class = TimeLogSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = TimeLog.objects.all().select_related('employee')
        
        # Filtros
        employee_id = self.request.query_params.get('employee_id', None)
        date = self.request.query_params.get('date', None)
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        if date:
            queryset = queryset.filter(date=date)
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Retorna todos os logs de hoje."""
        today = timezone.now().date()
        logs = TimeLog.objects.filter(date=today).select_related('employee')
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Retorna logs pendentes (sem saída registrada)."""
        logs = TimeLog.objects.filter(exit_time__isnull=True).select_related('employee')
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)


@api_view(['POST'])
def recognize_face(request):
    """
    Endpoint para reconhecimento facial.
    Recebe um embedding e procura o melhor match na base de dados.
    """
    serializer = RecognitionRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    embedding_list = serializer.validated_data['embedding']
    threshold = serializer.validated_data['threshold']
    
    # Converter para numpy array
    query_embedding = np.array(embedding_list, dtype=np.float32)
    
    # Buscar melhor match
    best_match = None
    best_similarity = -1.0
    
    for face_embedding in FaceEmbedding.objects.select_related('employee').all():
        stored_embedding = face_embedding.get_embedding()
        
        # Calcular similaridade de cosseno
        similarity = cosine_similarity(query_embedding, stored_embedding)
        
        if similarity > best_similarity:
            best_similarity = similarity
            if similarity >= threshold:
                best_match = face_embedding.employee
    
    # Preparar resposta
    if best_match:
        response_data = {
            'recognized': True,
            'employee': EmployeeSerializer(best_match).data,
            'similarity': float(best_similarity),
            'message': f'Funcionário reconhecido: {best_match.name}'
        }
    else:
        response_data = {
            'recognized': False,
            'employee': None,
            'similarity': float(best_similarity) if best_similarity > 0 else None,
            'message': 'Nenhum funcionário reconhecido'
        }
    
    return Response(response_data)


@api_view(['POST'])
def register_log(request):
    """
    Registra entrada ou saída de um funcionário.
    """
    serializer = RegisterLogSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    emp_id = serializer.validated_data['emp_id']
    mode = serializer.validated_data['mode']
    confidence = serializer.validated_data['confidence']
    
    try:
        employee = Employee.objects.get(emp_id=emp_id, is_active=True)
    except Employee.DoesNotExist:
        return Response(
            {'error': 'Funcionário não encontrado ou inativo'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    today = timezone.now().date()
    now_local = timezone.localtime()  # Usar horário local
    
    # Verificar status atual
    today_status = employee.get_today_status()
    
    if mode == 'entrada':
        if today_status == 'entered':
            return Response(
                {'error': 'Entrada já registrada hoje. Registre a saída primeiro.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if today_status == 'exited':
            return Response(
                {'error': 'Entrada e saída já registradas hoje.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Criar novo log de entrada
        time_log = TimeLog.objects.create(
            employee=employee,
            date=today,
            entry_time=now_local.time(),
            entry_confidence=confidence
        )
        
        message = f'Entrada registrada com sucesso para {employee.name}'
    
    else:  # saida
        if today_status == 'absent':
            return Response(
                {'error': 'Registre a entrada primeiro.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if today_status == 'exited':
            return Response(
                {'error': 'Saída já registrada hoje.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Atualizar log existente com saída
        time_log = TimeLog.objects.get(employee=employee, date=today)
        time_log.exit_time = now_local.time()
        time_log.exit_confidence = confidence
        time_log.save()
        
        message = f'Saída registrada com sucesso para {employee.name}'
    
    return Response({
        'success': True,
        'message': message,
        'log': TimeLogSerializer(time_log).data
    })


@api_view(['POST'])
def register_employee(request):
    """
    Cadastra um novo funcionário com embeddings faciais.
    """
    serializer = EmployeeRegistrationSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Verificar se emp_id já existe
    emp_id = serializer.validated_data['emp_id']
    if Employee.objects.filter(emp_id=emp_id).exists():
        return Response(
            {'error': f'Funcionário com ID {emp_id} já existe'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Criar funcionário e embedding
    employee = serializer.save()
    
    return Response({
        'success': True,
        'message': f'Funcionário {employee.name} cadastrado com sucesso',
        'employee': EmployeeSerializer(employee).data
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def check_duplicate_face(request):
    """
    Verifica se um embedding facial já está cadastrado.
    Útil para evitar duplicatas durante o cadastro.
    """
    embedding_list = request.data.get('embedding', [])
    threshold = request.data.get('threshold', 0.40)
    exclude_emp_id = request.data.get('exclude_emp_id', None)
    
    if not embedding_list:
        return Response(
            {'error': 'embedding é obrigatório'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    query_embedding = np.array(embedding_list, dtype=np.float32)
    
    # Buscar duplicatas
    for face_embedding in FaceEmbedding.objects.select_related('employee').all():
        if exclude_emp_id and face_embedding.employee.emp_id == exclude_emp_id:
            continue
        
        stored_embedding = face_embedding.get_embedding()
        similarity = cosine_similarity(query_embedding, stored_embedding)
        
        if similarity >= threshold:
            return Response({
                'is_duplicate': True,
                'employee': EmployeeSerializer(face_embedding.employee).data,
                'similarity': float(similarity)
            })
    
    return Response({
        'is_duplicate': False,
        'similarity': None
    })


@api_view(['GET'])
def dashboard_stats(request):
    """
    Retorna estatísticas gerais para o dashboard.
    """
    # Total de funcionários
    total_employees = Employee.objects.filter(is_active=True).count()
    
    # Logs de hoje
    today = timezone.now().date()
    today_logs = TimeLog.objects.filter(date=today)
    
    employees_present_today = today_logs.count()
    employees_entered = today_logs.filter(exit_time__isnull=True).count()
    employees_exited = today_logs.filter(exit_time__isnull=False).count()
    
    # Logs da semana
    week_start = today - timedelta(days=today.weekday())
    week_logs = TimeLog.objects.filter(date__gte=week_start, date__lte=today)
    
    # Logs do mês
    month_logs = TimeLog.objects.filter(
        date__year=today.year,
        date__month=today.month
    )
    
    # Total de horas do mês (todos os funcionários)
    total_hours_month = 0
    for log in month_logs.filter(exit_time__isnull=False):
        hours = log.get_worked_hours()
        if hours:
            total_hours_month += hours
    
    return Response({
        'total_employees': total_employees,
        'employees_present_today': employees_present_today,
        'employees_entered': employees_entered,
        'employees_exited': employees_exited,
        'week_logs_count': week_logs.count(),
        'month_logs_count': month_logs.count(),
        'total_hours_month': round(total_hours_month, 2),
    })


def cosine_similarity(a, b):
    """Calcula similaridade de cosseno entre dois vetores."""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a < 1e-8 or norm_b < 1e-8:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))
