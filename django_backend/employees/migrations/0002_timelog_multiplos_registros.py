# Generated manually for model restructuring in production migration module 1

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='timelog',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='employee',
            name='position',
        ),
        migrations.DeleteModel(
            name='TimeLog',
        ),
        migrations.CreateModel(
            name='TimeLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('entrada', 'Entrada'), ('saida', 'Saída')], max_length=10, verbose_name='Tipo')),
                ('horario', models.DateTimeField(auto_now_add=True, verbose_name='Horário')),
                ('data', models.DateField(blank=True, null=True, verbose_name='Data')),
                ('confidence', models.FloatField(default=0.0, help_text='Score de similaridade do reconhecimento facial', verbose_name='Confiança')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='time_logs', to='employees.employee', verbose_name='Funcionário')),
            ],
            options={
                'verbose_name': 'Registro de Ponto',
                'verbose_name_plural': 'Registros de Ponto',
                'ordering': ['-horario'],
            },
        ),
        migrations.AddIndex(
            model_name='timelog',
            index=models.Index(fields=['data'], name='employees_t_data_07c5b7_idx'),
        ),
        migrations.AddIndex(
            model_name='timelog',
            index=models.Index(fields=['employee', 'data'], name='employees_t_employe_f72953_idx'),
        ),
    ]
