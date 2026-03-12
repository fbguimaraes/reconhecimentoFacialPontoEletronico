"""
Models para o sistema de reconhecimento facial e controle de ponto.
"""
from django.db import models
from django.core.validators import MinLengthValidator
from django.utils import timezone
import pickle
import base64


class Employee(models.Model):
    """Modelo de funcionário no sistema."""
    
    emp_id = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="ID do Funcionário",
        validators=[MinLengthValidator(1)],
        help_text="Identificador único do funcionário"
    )
    name = models.CharField(
        max_length=200, 
        verbose_name="Nome Completo"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Data de Cadastro"
    )
    is_active = models.BooleanField(
        default=True, 
        verbose_name="Ativo",
        help_text="Funcionário ativo no sistema"
    )
    department = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name="Departamento"
    )
    position = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name="Cargo"
    )
    
    class Meta:
        verbose_name = "Funcionário"
        verbose_name_plural = "Funcionários"
        ordering = ['name']
        indexes = [
            models.Index(fields=['emp_id']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.emp_id})"
    
    def get_today_status(self):
        """Retorna o status do funcionário no dia atual."""
        today = timezone.now().date()
        log = TimeLog.objects.filter(
            employee=self, 
            date=today
        ).first()
        
        if not log:
            return "absent"
        if log.exit_time:
            return "exited"
        return "entered"
    
    def get_total_hours_month(self, year=None, month=None):
        """Calcula total de horas trabalhadas no mês."""
        if year is None:
            year = timezone.now().year
        if month is None:
            month = timezone.now().month
        
        logs = TimeLog.objects.filter(
            employee=self,
            date__year=year,
            date__month=month,
            exit_time__isnull=False
        )
        
        total_seconds = 0
        for log in logs:
            if log.entry_time and log.exit_time:
                entry_datetime = timezone.datetime.combine(log.date, log.entry_time)
                exit_datetime = timezone.datetime.combine(log.date, log.exit_time)
                delta = exit_datetime - entry_datetime
                total_seconds += delta.total_seconds()
        
        return total_seconds / 3600  # Retorna em horas


class FaceEmbedding(models.Model):
    """Armazena os embeddings faciais dos funcionários."""
    
    employee = models.OneToOneField(
        Employee, 
        on_delete=models.CASCADE, 
        related_name='embedding',
        verbose_name="Funcionário"
    )
    embedding_data = models.BinaryField(
        verbose_name="Dados do Embedding",
        help_text="Embedding facial serializado (numpy array)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )
    
    class Meta:
        verbose_name = "Embedding Facial"
        verbose_name_plural = "Embeddings Faciais"
    
    def __str__(self):
        return f"Embedding - {self.employee.name}"
    
    def set_embedding(self, numpy_array):
        """Serializa e armazena o embedding numpy."""
        self.embedding_data = pickle.dumps(numpy_array)
    
    def get_embedding(self):
        """Deserializa e retorna o embedding numpy."""
        return pickle.loads(self.embedding_data)


class TimeLog(models.Model):
    """Registro de entrada e saída de funcionários."""
    
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        related_name='time_logs',
        verbose_name="Funcionário"
    )
    date = models.DateField(
        verbose_name="Data"
    )
    entry_time = models.TimeField(
        verbose_name="Horário de Entrada"
    )
    exit_time = models.TimeField(
        blank=True, 
        null=True,
        verbose_name="Horário de Saída"
    )
    entry_confidence = models.FloatField(
        default=0.0,
        verbose_name="Confiança da Entrada",
        help_text="Score de similaridade do reconhecimento facial na entrada"
    )
    exit_confidence = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Confiança da Saída",
        help_text="Score de similaridade do reconhecimento facial na saída"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )
    
    class Meta:
        verbose_name = "Registro de Ponto"
        verbose_name_plural = "Registros de Ponto"
        ordering = ['-date', '-entry_time']
        unique_together = ['employee', 'date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['employee', 'date']),
        ]
    
    def __str__(self):
        return f"{self.employee.name} - {self.date} ({self.entry_time})"
    
    def get_worked_hours(self):
        """Retorna as horas trabalhadas neste registro."""
        if not self.exit_time:
            return None
        
        entry_datetime = timezone.datetime.combine(self.date, self.entry_time)
        exit_datetime = timezone.datetime.combine(self.date, self.exit_time)
        delta = exit_datetime - entry_datetime
        return delta.total_seconds() / 3600  # Retorna em horas
    
    def get_status(self):
        """Retorna o status do registro."""
        if self.exit_time:
            return "Completo"
        return "Pendente (sem saída)"
