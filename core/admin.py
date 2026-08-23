from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Departamento, Funcionario, RegistroPonto

# Inline
class RegistroPontoInline(admin.TabularInline):
    model = RegistroPonto
    extra = 1
    fields = ['data', 'horas_trabalhadas', 'observacao']
    readonly_fields = ['data']
    can_delete = True

# Departamento
@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome', 'created_at']
    search_fields = ['nome']
    ordering = ['nome']

# Funcionario
@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_nome', 'get_email', 'departamento', 'cargo', 'salario', 'is_deleted']
    list_filter = ['departamento', 'cargo', 'is_deleted', 'data_contratacao']
    search_fields = ['user__first_name', 'user__last_name', 'user__username', 'user__email']
    readonly_fields = ['data_contratacao', 'created_at', 'updated_at']
    inlines = [RegistroPontoInline]
    actions = ['restaurar_funcionarios']

    fieldsets = (
        ('Dados Pessoais', {
            'fields': ('user', 'departamento', 'cargo', 'salario', 'horas_semana')
        }),
        ('Auditoria', {
            'fields': ('data_contratacao', 'created_at', 'updated_at', 'is_deleted'),
            'classes': ('collapse',)
        }),
    )

    def get_nome(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_nome.short_description = 'Nome'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

    def restaurar_funcionarios(self, request, queryset):
        count = queryset.update(is_deleted=False)
        self.message_user(request, f'{count} funcionário(s) restaurado(s).')
    restaurar_funcionarios.short_description = 'Restaurar funcionários selecionados'

# RegistroPonto
@admin.register(RegistroPonto)
class RegistroPontoAdmin(admin.ModelAdmin):
    list_display = ['id', 'funcionario', 'data', 'horas_trabalhadas']
    list_filter = ['funcionario__departamento', 'data']
    search_fields = ['funcionario__user__first_name', 'funcionario__user__last_name']
    ordering = ['-data']
    readonly_fields = ['data', 'created_at', 'updated_at']

    fieldsets = (
        (None, {
            'fields': ('funcionario', 'data', 'horas_trabalhadas', 'observacao')
        }),
        ('Auditoria', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
