from django.db import models
from django.contrib.auth.models import User
from medico.models import DatasAbertas

class Consulta(models.Model):
    # Define as opções de status possíveis para uma consulta.
    status_choices = (
        ('A', 'Agendada'),  # A consulta está agendada.
        ('F', 'Finalizada'),  # A consulta foi finalizada.
        ('C', 'Cancelada'),  # A consulta foi cancelada.
        ('I', 'Iniciada')  # A consulta foi iniciada.
    )
    
    # Campo de relação com o modelo User. Um paciente é um usuário no sistema.
    paciente = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    # Campo de relação com o modelo DatasAbertas. Referencia uma data de consulta aberta.
    data_aberta = models.ForeignKey(DatasAbertas, on_delete=models.DO_NOTHING)
    # Campo de status da consulta. Utiliza as opções definidas em status_choices.
    status = models.CharField(max_length=1, choices=status_choices, default='A')
    # Campo opcional para armazenar um link relacionado à consulta (por exemplo, link para consulta online).
    link = models.URLField(null=True, blank=True)
    
    # Define a representação em string do modelo Consulta.
    def __str__(self):
        # Retorna o nome de usuário do paciente.
        return self.paciente.username
    
class Documento(models.Model):
    consulta = models.ForeignKey(Consulta, on_delete=models.DO_NOTHING)
    titulo = models.CharField(max_length=30)
    documento = models.FileField(upload_to='documentos')

    def __str__(self):
        return self.titulo