"""
Configuração do Django Admin para o sistema de reconhecimento facial.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Employee, FaceEmbedding, TimeLog


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Admin para funcionários."""
    
    list_display = ['emp_id', 'name', 'department', 'is_active', 'created_at', 'status_tag']
    list_filter = ['is_active', 'department', 'created_at']
    search_fields = ['emp_id', 'name', 'department']
    ordering = ['name']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('emp_id', 'name', 'is_active')
        }),
        ('Informações Profissionais', {
            'fields': ('department',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']
    
    def status_tag(self, obj):
        """Mostra status do funcionário hoje."""
        status = obj.get_today_status()
        colors = {
            'absent': 'gray',
            'entrada': 'orange',
            'saida': 'green'
        }
        labels = {
            'absent': 'Ausente',
            'entrada': 'Presente',
            'saida': 'Saiu'
        }
        color = colors.get(status, 'gray')
        label = labels.get(status, status)
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, label
        )
    status_tag.short_description = 'Status Hoje'


@admin.register(FaceEmbedding)
class FaceEmbeddingAdmin(admin.ModelAdmin):
    """Admin para embeddings faciais."""
    
    list_display = ['employee', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['employee__name', 'employee__emp_id']
    readonly_fields = ['created_at', 'updated_at', 'embedding_info']
    
    fieldsets = (
        ('Funcionário', {
            'fields': ('employee',)
        }),
        ('Embedding', {
            'fields': ('embedding_info',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def embedding_info(self, obj):
        """Mostra informações do embedding."""
        if obj.embedding_data:
            import pickle
            embedding = pickle.loads(obj.embedding_data)
            return format_html(
                '<strong>Shape:</strong> {}<br><strong>Type:</strong> {}<br><strong>Size:</strong> {} bytes',
                embedding.shape, embedding.dtype, len(obj.embedding_data)
            )
        return '-'
    embedding_info.short_description = 'Informações do Embedding'


@admin.register(TimeLog)
class TimeLogAdmin(admin.ModelAdmin):
    """Admin para registros de ponto."""
    
    list_display = [
        'employee', 'tipo', 'data', 'horario', 'confidence', 'status_tag'
    ]
    list_filter = ['tipo', 'data', 'employee']
    search_fields = ['employee__name', 'employee__emp_id']
    date_hierarchy = 'data'
    ordering = ['-horario']
    
    fieldsets = (
        ('Funcionário', {
            'fields': ('employee',)
        }),
        ('Registro de Ponto', {
            'fields': ('tipo', 'horario', 'data', 'confidence')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['horario', 'created_at']
    
    def status_tag(self, obj):
        """Mostra status do registro."""
        if obj.tipo == 'saida':
            return format_html(
                '<span style="background-color: green; color: white; padding: 3px 10px; border-radius: 3px;">Saída</span>'
            )
        return format_html(
            '<span style="background-color: orange; color: white; padding: 3px 10px; border-radius: 3px;">Entrada</span>'
        )
    status_tag.short_description = 'Status'
