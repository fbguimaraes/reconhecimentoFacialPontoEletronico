"""
Serializers para a API REST do sistema de reconhecimento facial.
"""
from rest_framework import serializers
from .models import Employee, FaceEmbedding, TimeLog
import pickle
import numpy as np


class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer para modelo Employee."""
    
    today_status = serializers.SerializerMethodField()
    total_hours_month = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = [
            'id', 'emp_id', 'name', 'department', 'position',
            'is_active', 'created_at', 'today_status', 'total_hours_month'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_today_status(self, obj):
        return obj.get_today_status()
    
    def get_total_hours_month(self, obj):
        return round(obj.get_total_hours_month(), 2)


class FaceEmbeddingSerializer(serializers.ModelSerializer):
    """Serializer para embeddings faciais."""
    
    employee_id = serializers.IntegerField(write_only=True, required=False)
    emp_id = serializers.CharField(write_only=True, required=False)
    embedding = serializers.ListField(
        child=serializers.FloatField(),
        write_only=True,
        required=False,
        help_text="Array numpy do embedding (lista de floats)"
    )
    
    class Meta:
        model = FaceEmbedding
        fields = ['id', 'employee', 'employee_id', 'emp_id', 'embedding', 'created_at', 'updated_at']
        read_only_fields = ['id', 'employee', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Obter employee por ID ou emp_id
        employee_id = validated_data.pop('employee_id', None)
        emp_id = validated_data.pop('emp_id', None)
        embedding_list = validated_data.pop('embedding')
        
        if employee_id:
            employee = Employee.objects.get(id=employee_id)
        elif emp_id:
            employee = Employee.objects.get(emp_id=emp_id)
        else:
            raise serializers.ValidationError("employee_id ou emp_id é obrigatório")
        
        # Converter lista para numpy array
        embedding_array = np.array(embedding_list, dtype=np.float32)
        
        # Criar ou atualizar embedding
        face_embedding, created = FaceEmbedding.objects.update_or_create(
            employee=employee,
            defaults={'embedding_data': pickle.dumps(embedding_array)}
        )
        
        return face_embedding


class TimeLogSerializer(serializers.ModelSerializer):
    """Serializer para registros de ponto."""
    
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    employee_emp_id = serializers.CharField(source='employee.emp_id', read_only=True)
    worked_hours = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = TimeLog
        fields = [
            'id', 'employee', 'employee_name', 'employee_emp_id',
            'date', 'entry_time', 'exit_time', 
            'entry_confidence', 'exit_confidence',
            'worked_hours', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_worked_hours(self, obj):
        hours = obj.get_worked_hours()
        return round(hours, 2) if hours else None
    
    def get_status(self, obj):
        return obj.get_status()


class RecognitionRequestSerializer(serializers.Serializer):
    """Serializer para requisição de reconhecimento facial."""
    
    embedding = serializers.ListField(
        child=serializers.FloatField(),
        help_text="Embedding facial do rosto a ser reconhecido"
    )
    threshold = serializers.FloatField(
        default=0.40,
        help_text="Limiar de similaridade (0-1)"
    )


class RecognitionResponseSerializer(serializers.Serializer):
    """Serializer para resposta de reconhecimento facial."""
    
    recognized = serializers.BooleanField()
    employee = EmployeeSerializer(required=False, allow_null=True)
    similarity = serializers.FloatField(required=False, allow_null=True)
    message = serializers.CharField(required=False)


class RegisterLogSerializer(serializers.Serializer):
    """Serializer para registrar entrada/saída."""
    
    emp_id = serializers.CharField(help_text="ID do funcionário")
    mode = serializers.ChoiceField(
        choices=['entrada', 'saida'],
        help_text="Tipo de registro"
    )
    confidence = serializers.FloatField(
        help_text="Score de similaridade do reconhecimento"
    )


class EmployeeRegistrationSerializer(serializers.Serializer):
    """Serializer para cadastro completo de funcionário com embedding."""
    
    emp_id = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=200)
    department = serializers.CharField(max_length=100, required=False, allow_blank=True)
    position = serializers.CharField(max_length=100, required=False, allow_blank=True)
    embeddings = serializers.ListField(
        child=serializers.ListField(child=serializers.FloatField()),
        help_text="Lista de embeddings capturados (múltiplos frames)"
    )
    
    def create(self, validated_data):
        embeddings_list = validated_data.pop('embeddings')
        
        # Calcular embedding médio
        avg_embedding = np.mean(embeddings_list, axis=0).astype(np.float32)
        
        # Criar funcionário
        employee = Employee.objects.create(**validated_data)
        
        # Criar embedding
        FaceEmbedding.objects.create(
            employee=employee,
            embedding_data=pickle.dumps(avg_embedding)
        )
        
        return employee
