from django import forms
from django.contrib.auth.models import User
from .models import Funcionario, Departamento

class FuncionarioForm(forms.ModelForm):
    # Campos do User que serão exibidos no mesmo formulário
    first_name = forms.CharField(max_length=30, label='Nome')
    last_name = forms.CharField(max_length=30, label='Sobrenome', required=False)
    username = forms.CharField(max_length=150, label='Usuário')
    email = forms.EmailField(label='E-mail')
    password = forms.CharField(widget=forms.PasswordInput, label='Senha', required=False)

    class Meta:
        model = Funcionario
        fields = ['departamento', 'cargo', 'salario', 'horas_semana']

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance and instance.user_id:
            initial = kwargs.get('initial', {})
            initial['first_name'] = instance.user.first_name
            initial['last_name'] = instance.user.last_name
            initial['username'] = instance.user.username
            initial['email'] = instance.user.email
            kwargs['initial'] = initial
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Busca ou cria o usuário
        if instance.user_id:
            user = instance.user
        else:
            user = User()

        # Atualiza os dados do usuário
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']

        # Se senha for fornecida, define (mesmo em edição)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)

        if commit:
            user.save()
            instance.user = user

            # Verifica se já existe um funcionário para este usuário
            funcionario_existente = Funcionario.objects.filter(user=user).first()
            if funcionario_existente:
                # Atualiza o existente
                funcionario_existente.departamento = instance.departamento
                funcionario_existente.cargo = instance.cargo
                funcionario_existente.salario = instance.salario
                funcionario_existente.horas_semana = instance.horas_semana
                funcionario_existente.save()
                instance = funcionario_existente
            else:
                instance.save()

        return instance

class DepartamentoForm(forms.ModelForm):
    class Meta:
        model = Departamento
        fields = ['nome', 'descricao']

def clean_username(self):
    username = self.cleaned_data.get('username')
    if not username:
        raise forms.ValidationError('O nome de usuário é obrigatório.')

    instance = self.instance
    if instance and instance.user_id:
        # Editando: verifica se outro usuário já tem este username
        if User.objects.exclude(id=instance.user_id).filter(username=username).exists():
            raise forms.ValidationError('Este nome de usuário já está em uso. Escolha outro.')
    else:
        # Criando: verifica se já existe
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nome de usuário já está em uso. Escolha outro.')
    return username

def clean_email(self):
    email = self.cleaned_data.get('email')
    if not email:
        raise forms.ValidationError('O e-mail é obrigatório.')

    instance = self.instance
    if instance and instance.user_id:
        if User.objects.exclude(id=instance.user_id).filter(email=email).exists():
            raise forms.ValidationError('Este e-mail já está cadastrado. Use outro.')
    else:
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este e-mail já está cadastrado. Use outro.')
    return email
