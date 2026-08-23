from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q

# BaseModel (Auditoria)
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# Soft Delete Manager
class SoftDeleteQuerySet(models.QuerySet):
    def ativos(self):
        return self.filter(is_deleted=False)

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).ativos()

    def all_objects(self):
        return super().get_queryset()

# Departamento
class Departamento(BaseModel):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome

    class Meta:
        ordering = ['nome']

# Funcionario
class Funcionario(BaseModel):
    class Cargo(models.TextChoices):
        ESTAGIARIO = 'est', 'Estagiário'
        JUNIOR = 'jun', 'Júnior'
        PLENO = 'pln', 'Pleno'
        SENIOR = 'sen', 'Sênior'
        GERENTE = 'ger', 'Gerente'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='funcionario')
    departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True, blank=True, related_name='funcionarios')
    cargo = models.CharField(max_length=3, choices=Cargo.choices, default=Cargo.JUNIOR)
    salario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    horas_semana = models.PositiveIntegerField(default=40)
    data_contratacao = models.DateField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    # Managers
    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.username})"

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()

    class Meta:
        ordering = ['user__first_name', 'user__last_name']
        permissions = [
            ("can_manage_funcionarios", "Pode gerenciar funcionários"),
            ("can_view_all_registros", "Pode ver todos os registros de ponto"),
        ]

# RegistroPonto
class RegistroPonto(BaseModel):
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name='registros')
    data = models.DateField()  # agora obrigatório (não mais auto_now_add)
    entrada = models.DateTimeField()  # novo campo
    saida = models.DateTimeField(null=True, blank=True)  # novo campo
    observacao = models.TextField(blank=True)

    class Meta:
        unique_together = ['funcionario', 'data']
        ordering = ['-data', '-entrada']

    @property
    def horas_trabalhadas(self):
        if self.entrada and self.saida:
            delta = self.saida - self.entrada
            return round(delta.total_seconds() / 3600, 2)
        return 0
