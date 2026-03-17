"""
Models para o sistema de reconhecimento facial e controle de ponto.
"""
from django.db import models
from django.core.validators import MinLengthValidator
from django.utils import timezone
import pickle


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
        today = timezone.localdate()
        ultimo = TimeLog.objects.filter(
            employee=self,
            data=today
        ).order_by('-horario').first()
        
        if not ultimo:
            return "absent"
        return ultimo.tipo


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
    """Registro de ponto por evento discreto (entrada ou saída)."""

    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
    ]
    
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        related_name='time_logs',
        verbose_name="Funcionário"
    )
    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES,
        verbose_name="Tipo"
    )
    horario = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Horário"
    )
    data = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data"
    )
    confidence = models.FloatField(
        default=0.0,
        verbose_name="Confiança",
        help_text="Score de similaridade do reconhecimento facial"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    
    class Meta:
        verbose_name = "Registro de Ponto"
        verbose_name_plural = "Registros de Ponto"
        ordering = ['-horario']
        indexes = [
            models.Index(fields=['data']),
            models.Index(fields=['employee', 'data']),
        ]

    def save(self, *args, **kwargs):
        if not self.data:
            self.data = timezone.localdate()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.employee.name} - {self.tipo} - {self.horario.strftime('%d/%m/%Y %H:%M')}"
