from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),

    # Funcionários
    path('funcionarios/', views.FuncionarioListView.as_view(), name='funcionario_list'),
    path('funcionarios/novo/', views.FuncionarioCreateView.as_view(), name='funcionario_create'),
    path('funcionarios/<int:pk>/', views.FuncionarioDetailView.as_view(), name='funcionario_detail'),
    path('funcionarios/<int:pk>/editar/', views.FuncionarioUpdateView.as_view(), name='funcionario_update'),
    path('funcionarios/<int:pk>/deletar/', views.FuncionarioDeleteView.as_view(), name='funcionario_delete'),

    # Departamentos
    path('departamentos/', views.DepartamentoListView.as_view(), name='departamento_list'),
    path('departamentos/novo/', views.DepartamentoCreateView.as_view(), name='departamento_create'),
    path('departamentos/<int:pk>/editar/', views.DepartamentoUpdateView.as_view(), name='departamento_update'),
    path('departamentos/<int:pk>/deletar/', views.DepartamentoDeleteView.as_view(), name='departamento_delete'),

    # Meus Registros (funcionário)
    path('meus-pontos/', views.MeusRegistrosView.as_view(), name='meus_registros'),

    # Registro de Ponto (bater ponto e listagem)
    path('bater-ponto/', views.BaterPontoView.as_view(), name='bater_ponto'),
    path('registros/', views.RegistroPontoListView.as_view(), name='registro_ponto_list'),
    path('registros/novo/', views.RegistroPontoCreateView.as_view(), name='registro_ponto_create'),
    path('registros/<int:pk>/editar/', views.RegistroPontoUpdateView.as_view(), name='registro_ponto_update'),
    path('registros/<int:pk>/deletar/', views.RegistroPontoDeleteView.as_view(), name='registro_ponto_delete'),
]
