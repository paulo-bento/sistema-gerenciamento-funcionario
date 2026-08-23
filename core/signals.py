from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Funcionario

@receiver(post_save, sender=User)
def criar_funcionario_para_usuario(sender, instance, created, **kwargs):
    """
    Quando um novo User for criado, cria automaticamente um Funcionario associado.
    """
    if created:
        Funcionario.objects.create(
            user=instance,
            departamento=None,  # será definido depois
            cargo=Funcionario.Cargo.JUNIOR,
            salario=0.00,
            horas_semana=40
        )
