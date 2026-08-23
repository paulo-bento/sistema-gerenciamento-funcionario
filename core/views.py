from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.db.models import Count, Sum, Avg
from django.db import models
from django.core.exceptions import ValidationError
from .models import Funcionario, Departamento, RegistroPonto
from .forms import FuncionarioForm, DepartamentoForm
from .services.registro_ponto_service import RegistroPontoService
from django.http import Http404

# Dashboard (gerente)
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        is_gerente = user.groups.filter(name='Gerente').exists()

        if is_gerente:
            context['total_funcionarios'] = Funcionario.objects.count()
            context['total_departamentos'] = Departamento.objects.count()
            context['media_salarial'] = Funcionario.objects.aggregate(Avg('salario'))['salario__avg'] or 0
            context['ultimos_registros'] = RegistroPonto.objects.select_related(
                'funcionario__user'
            ).order_by('-data')[:5]
        else:
            funcionario = get_object_or_404(Funcionario, user=user)
            context['total_funcionarios'] = None
            context['total_departamentos'] = None
            context['media_salarial'] = None
            context['ultimos_registros'] = funcionario.registros.all().order_by('-data')[:5]
            context['funcionario'] = funcionario

        context['is_gerente'] = is_gerente
        return context

# Funcionario CRUD
class FuncionarioListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Funcionario
    template_name = 'core/funcionario_list.html'
    context_object_name = 'funcionarios'
    paginate_by = 10
    permission_required = 'core.view_funcionario'

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset().select_related('user', 'departamento')

        if not user.groups.filter(name='Gerente').exists():
            queryset = queryset.filter(user=user)

        nome = self.request.GET.get('nome')
        if nome:
            queryset = queryset.filter(
                models.Q(user__first_name__icontains=nome) |
                models.Q(user__last_name__icontains=nome)
            )
        dept = self.request.GET.get('departamento')
        if dept:
            queryset = queryset.filter(departamento_id=dept)
        cargo = self.request.GET.get('cargo')
        if cargo:
            queryset = queryset.filter(cargo=cargo)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departamentos'] = Departamento.objects.all()
        context['cargos'] = Funcionario.Cargo.choices
        return context

class FuncionarioDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Funcionario
    template_name = 'core/funcionario_detail.html'
    context_object_name = 'funcionario'
    permission_required = 'core.view_funcionario'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['registros'] = self.object.registros.all()[:10]
        return context

class FuncionarioCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = Funcionario
    form_class = FuncionarioForm
    template_name = 'core/funcionario_form.html'
    permission_required = 'core.add_funcionario'
    success_message = 'Funcionário criado com sucesso!'
    success_url = reverse_lazy('core:funcionario_list')

class FuncionarioUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Funcionario
    form_class = FuncionarioForm
    template_name = 'core/funcionario_form.html'
    permission_required = 'core.change_funcionario'
    success_message = 'Funcionário atualizado com sucesso!'
    success_url = reverse_lazy('core:funcionario_list')

class FuncionarioDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Funcionario
    template_name = 'core/funcionario_confirm_delete.html'
    permission_required = 'core.delete_funcionario'
    success_url = reverse_lazy('core:funcionario_list')
    success_message = 'Funcionário removido com sucesso! (soft delete)'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

# Departamento CRUD
class DepartamentoListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Departamento
    template_name = 'core/departamento_list.html'
    context_object_name = 'departamentos'
    permission_required = 'core.view_departamento'
    paginate_by = 10

class DepartamentoCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = Departamento
    form_class = DepartamentoForm
    template_name = 'core/departamento_form.html'
    permission_required = 'core.add_departamento'
    success_message = 'Departamento criado com sucesso!'
    success_url = reverse_lazy('core:departamento_list')

class DepartamentoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Departamento
    form_class = DepartamentoForm
    template_name = 'core/departamento_form.html'
    permission_required = 'core.change_departamento'
    success_message = 'Departamento atualizado com sucesso!'
    success_url = reverse_lazy('core:departamento_list')

class DepartamentoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Departamento
    template_name = 'core/departamento_confirm_delete.html'
    permission_required = 'core.delete_departamento'
    success_url = reverse_lazy('core:departamento_list')
    success_message = 'Departamento removido com sucesso!'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

# Meus Registros (funcionário)
class MeusRegistrosView(LoginRequiredMixin, ListView):
    model = RegistroPonto
    template_name = 'core/meus_registros.html'
    context_object_name = 'registros'
    paginate_by = 15

    def get_queryset(self):
        funcionario = get_object_or_404(Funcionario, user=self.request.user)
        return funcionario.registros.all().order_by('-data')

# Registro de Ponto
class BaterPontoView(LoginRequiredMixin, TemplateView):
    template_name = 'core/bater_ponto.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        funcionario = get_object_or_404(Funcionario, user=self.request.user)
        hoje = timezone.localdate()
        registro = RegistroPonto.objects.filter(
            funcionario=funcionario,
            data=hoje
        ).first()
        context['funcionario'] = funcionario
        context['registro'] = registro
        context['hoje'] = hoje
        context['ultimos_registros'] = RegistroPontoService.get_registros_por_funcionario(
            funcionario
        )[:10]
        return context

    def post(self, request, *args, **kwargs):
        funcionario = get_object_or_404(Funcionario, user=self.request.user)
        try:
            # Obtém horário local ajustado
            agora = timezone.localtime(timezone.now())
            result = RegistroPontoService.bater_ponto(funcionario, agora)
            messages.success(request, result['mensagem'])
        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Erro ao registrar ponto: {str(e)}')
        return redirect('core:bater_ponto')

class RegistroPontoListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = RegistroPonto
    template_name = 'core/registro_ponto_list.html'
    context_object_name = 'registros'
    paginate_by = 15
    permission_required = 'core.view_registroponto'

    def get_queryset(self):
        user = self.request.user
        is_gerente = user.groups.filter(name='Gerente').exists()

        if is_gerente:
            queryset = RegistroPontoService.get_registros_todos()
        else:
            funcionario = get_object_or_404(Funcionario, user=user)
            queryset = RegistroPontoService.get_registros_por_funcionario(funcionario)

        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        funcionario_id = self.request.GET.get('funcionario')
        if data_inicio:
            queryset = queryset.filter(data__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(data__lte=data_fim)
        if funcionario_id and is_gerente:
            queryset = queryset.filter(funcionario_id=funcionario_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        is_gerente = user.groups.filter(name='Gerente').exists()
        context['is_gerente'] = is_gerente
        if is_gerente:
            context['funcionarios'] = Funcionario.objects.all()
        return context

class RegistroPontoCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = RegistroPonto
    fields = ['funcionario', 'data', 'entrada', 'saida', 'observacao']
    template_name = 'core/registro_ponto_form.html'
    permission_required = 'core.add_registroponto'
    success_message = 'Registro criado com sucesso!'
    success_url = reverse_lazy('core:registro_ponto_list')

class RegistroPontoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = RegistroPonto
    fields = ['funcionario', 'data', 'entrada', 'saida', 'observacao']
    template_name = 'core/registro_ponto_form.html'
    permission_required = 'core.change_registroponto'
    success_message = 'Registro atualizado com sucesso!'
    success_url = reverse_lazy('core:registro_ponto_list')

class RegistroPontoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = RegistroPonto
    template_name = 'core/registro_ponto_confirm_delete.html'
    permission_required = 'core.delete_registroponto'
    success_url = reverse_lazy('core:registro_ponto_list')
    success_message = 'Registro removido com sucesso!'

    def delete(self, request, *args, **kwargs):
        messages.success(request, self.success_message)
        return super().delete(request, *args, **kwargs)

# Error Handlers
def handler403(request, exception):
    return render(request, '403.html', status=403)

def handler404(request, exception):
    return render(request, '404.html', status=404)

