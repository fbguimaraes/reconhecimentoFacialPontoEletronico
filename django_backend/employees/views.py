"""
Views da API REST para o sistema de reconhecimento facial.
"""
import base64
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone
from django.db import transaction
from django.db.models import Count, Q, Sum, F
from datetime import datetime, timedelta
import cv2
import numpy as np

from .models import Employee, FaceEmbedding, TimeLog
from .auth import check_admin_password
from .face_engine_wrapper import get_engine
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
            logs = logs.filter(data__gte=date_from)
        if date_to:
            logs = logs.filter(data__lte=date_to)
        
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
            data__year=now.year,
            data__month=now.month
        )
        
        total_month_logs = month_logs.count()
        days_worked = month_logs.values('data').distinct().count()
        
        return Response({
            'total_logs': total_logs,
            'total_month_logs': total_month_logs,
            'days_worked_month': days_worked,
            'total_hours_month': 0.0,
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
            queryset = queryset.filter(data=date)
        if date_from:
            queryset = queryset.filter(data__gte=date_from)
        if date_to:
            queryset = queryset.filter(data__lte=date_to)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Retorna todos os logs de hoje."""
        today = timezone.localdate()
        logs = TimeLog.objects.filter(data=today).select_related('employee')
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Retorna registros de entrada do dia atual."""
        logs = TimeLog.objects.filter(data=timezone.localdate(), tipo='entrada').select_related('employee')
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
def recognize_image(request):
    """Recebe imagem base64, extrai embedding e reconhece o funcionário."""
    image_b64 = request.data.get('image_base64')
    threshold = request.data.get('threshold', 0.40)

    if not image_b64:
        return Response({'error': 'image_base64 obrigatório'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        threshold = float(threshold)
    except (TypeError, ValueError):
        return Response({'error': 'threshold inválido'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        img_bytes = base64.b64decode(image_b64)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if frame_bgr is None:
            raise ValueError('Falha ao decodificar imagem')
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    except Exception as exc:
        return Response({'error': f'Imagem inválida: {str(exc)}'}, status=status.HTTP_400_BAD_REQUEST)

    engine = get_engine()
    embedding = engine.detect_and_embed(frame_rgb)

    if embedding is None:
        return Response({'recognized': False, 'message': 'Nenhum rosto detectado'})

    best_match = None
    best_similarity = -1.0

    for face_embedding in FaceEmbedding.objects.select_related('employee').all():
        stored_embedding = face_embedding.get_embedding()
        similarity = cosine_similarity(embedding, stored_embedding)

        if similarity > best_similarity:
            best_similarity = similarity
            if similarity >= threshold:
                best_match = face_embedding.employee

    if best_match:
        return Response({
            'recognized': True,
            'employee': EmployeeSerializer(best_match).data,
            'similarity': float(best_similarity),
        })

    return Response({
        'recognized': False,
        'similarity': float(best_similarity) if best_similarity > 0 else None,
    })


def _next_emp_id():
    """Gera próximo emp_id incremental no formato 001, 002, ..."""
    ids = Employee.objects.values_list('emp_id', flat=True)
    numeric_ids = [int(emp_id) for emp_id in ids if str(emp_id).isdigit()]
    if numeric_ids:
        return f"{max(numeric_ids) + 1:03d}"
    return f"{Employee.objects.count() + 1:03d}"


@api_view(['POST'])
def register_employee_image(request):
    """Cadastra funcionário a partir de uma imagem base64 com validação de duplicidade."""
    if not check_admin_password(request):
        return Response(
            {'error': 'Senha admin incorreta', 'error_code': 'invalid_admin_password'},
            status=status.HTTP_403_FORBIDDEN,
        )

    name = (request.data.get('name') or '').strip()
    image_b64 = request.data.get('image_base64')
    threshold = request.data.get('threshold', 0.40)
    department = (request.data.get('department') or '').strip()

    if not name:
        return Response(
            {'error': 'name é obrigatório', 'error_code': 'missing_name'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not image_b64:
        return Response(
            {'error': 'image_base64 é obrigatório', 'error_code': 'missing_image'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        threshold = float(threshold)
    except (TypeError, ValueError):
        return Response(
            {'error': 'threshold inválido', 'error_code': 'invalid_threshold'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        if isinstance(image_b64, str) and ',' in image_b64:
            image_b64 = image_b64.split(',', 1)[1]
        img_bytes = base64.b64decode(image_b64)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if frame_bgr is None:
            raise ValueError('Falha ao decodificar imagem')
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    except Exception as exc:
        return Response(
            {'error': f'Imagem inválida: {str(exc)}', 'error_code': 'invalid_image'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    engine = get_engine()
    embedding = engine.detect_and_embed(frame_rgb)

    if embedding is None:
        return Response(
            {'error': 'Nenhum rosto detectado', 'error_code': 'no_face_detected'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    best_match = None
    best_similarity = -1.0
    for face_embedding in FaceEmbedding.objects.select_related('employee').all():
        stored_embedding = face_embedding.get_embedding()
        similarity = cosine_similarity(embedding, stored_embedding)
        if similarity > best_similarity:
            best_similarity = similarity
            if similarity >= threshold:
                best_match = face_embedding.employee

    if best_match:
        return Response(
            {
                'error': f'Rosto já cadastrado para {best_match.name}',
                'error_code': 'duplicate_face',
                'employee': EmployeeSerializer(best_match).data,
                'similarity': float(best_similarity),
            },
            status=status.HTTP_409_CONFLICT,
        )

    with transaction.atomic():
        employee = Employee.objects.create(
            emp_id=_next_emp_id(),
            name=name,
            department=department or None,
            is_active=True,
        )
        face_embedding = FaceEmbedding(employee=employee)
        face_embedding.set_embedding(embedding.astype(np.float32))
        face_embedding.save()

    return Response(
        {
            'success': True,
            'message': f'Funcionário {employee.name} cadastrado com sucesso',
            'employee': EmployeeSerializer(employee).data,
        },
        status=status.HTTP_201_CREATED,
    )


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
            {'error': 'Funcionário não encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )

    time_log = TimeLog.objects.create(
        employee=employee,
        tipo=mode,
        confidence=confidence
    )
    message = f'{mode.capitalize()} registrada para {employee.name}'
    
    return Response({
        'success': True,
        'message': message,
        'log': TimeLogSerializer(time_log).data
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def register_employee(request):
    """
    Cadastra um novo funcionário com embeddings faciais.
    """
    if not check_admin_password(request):
        return Response({'error': 'Senha admin incorreta'}, status=status.HTTP_403_FORBIDDEN)

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
    today = timezone.localdate()
    today_logs = TimeLog.objects.filter(data=today)
    
    employees_present_today = today_logs.values('employee').distinct().count()
    employees_entered = today_logs.filter(tipo='entrada').count()
    employees_exited = today_logs.filter(tipo='saida').count()
    
    # Logs da semana
    week_start = today - timedelta(days=today.weekday())
    week_logs = TimeLog.objects.filter(data__gte=week_start, data__lte=today)
    
    # Logs do mês
    month_logs = TimeLog.objects.filter(
        data__year=today.year,
        data__month=today.month
    )
    
    return Response({
        'total_employees': total_employees,
        'employees_present_today': employees_present_today,
        'employees_entered': employees_entered,
        'employees_exited': employees_exited,
        'week_logs_count': week_logs.count(),
        'month_logs_count': month_logs.count(),
        'total_hours_month': 0.0,
    })


def cosine_similarity(a, b):
    """Calcula similaridade de cosseno entre dois vetores."""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a < 1e-8 or norm_b < 1e-8:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))
