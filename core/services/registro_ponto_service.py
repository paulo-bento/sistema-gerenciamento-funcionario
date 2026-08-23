from django.utils import timezone
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from ..models import RegistroPonto, Funcionario

class RegistroPontoService:
    """
    Service Layer para lógica de registro de ponto.
    """

    @staticmethod
    def bater_ponto(funcionario: Funcionario, agora=None):
        """
        Registra entrada ou saída para um funcionário.
        Retorna um dicionário com o status e o registro.
        """
        if agora is None:
            agora = timezone.localtime(timezone.now())
        hoje = agora.date()

        # Busca registro de hoje
        registro = RegistroPonto.objects.filter(
            funcionario=funcionario,
            data=hoje
        ).first()

        if not registro:
            # Primeiro registro do dia → entrada
            registro = RegistroPonto.objects.create(
                funcionario=funcionario,
                data=hoje,
                entrada=agora,
                saida=None
            )
            return {
                'status': 'entrada',
                'registro': registro,
                'mensagem': f'✅ Entrada registrada às {agora.strftime("%H:%M")}'
            }

        if registro.saida is None:
            # Já tem entrada, mas não saída → registrar saída
            if agora < registro.entrada:
                raise ValidationError('❌ A saída não pode ser registrada antes da entrada. Verifique o horário.')

            # Opcional: validar tempo mínimo de trabalho (1 hora)
            # if (agora - registro.entrada).total_seconds() < 3600:
            #     raise ValidationError('⏳ A saída só pode ser registrada após pelo menos 1 hora de trabalho.')

            registro.saida = agora
            registro.save()
            horas = registro.horas_trabalhadas
            return {
                'status': 'saida',
                'registro': registro,
                'mensagem': f'✅ Saída registrada às {agora.strftime("%H:%M")}. Total: {horas}h'
            }

        # Já tem entrada e saída → dia completo
        return {
            'status': 'completo',
            'registro': registro,
            'mensagem': 'ℹ️ Ponto já registrado hoje. Entrada: {} | Saída: {}'.format(
                registro.entrada.strftime("%H:%M"),
                registro.saida.strftime("%H:%M")
            )
        }

    @staticmethod
    def criar_registro_manual(funcionario, data, entrada, saida=None, observacao=''):
        """Cria registro manualmente (para gerentes)."""
        if RegistroPonto.objects.filter(funcionario=funcionario, data=data).exists():
            raise ValidationError('⚠️ Já existe um registro para esta data.')

        return RegistroPonto.objects.create(
            funcionario=funcionario,
            data=data,
            entrada=entrada,
            saida=saida,
            observacao=observacao
        )

    @staticmethod
    def atualizar_registro(registro, entrada=None, saida=None, observacao=None):
        """Atualiza um registro existente."""
        if entrada:
            registro.entrada = entrada
        if saida:
            registro.saida = saida
        if observacao is not None:
            registro.observacao = observacao
        registro.save()
        return registro

    @staticmethod
    def deletar_registro(registro):
        """Remove um registro."""
        registro.delete()

    @staticmethod
    def get_registros_por_funcionario(funcionario, data_inicio=None, data_fim=None):
        """Retorna registros de um funcionário com filtros opcionais."""
        queryset = RegistroPonto.objects.filter(funcionario=funcionario)
        if data_inicio:
            queryset = queryset.filter(data__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(data__lte=data_fim)
        return queryset.order_by('-data', '-entrada')

    @staticmethod
    def get_registros_todos(data_inicio=None, data_fim=None):
        """Retorna todos os registros (para gerentes)."""
        queryset = RegistroPonto.objects.select_related('funcionario__user')
        if data_inicio:
            queryset = queryset.filter(data__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(data__lte=data_fim)
        return queryset.order_by('-data', '-entrada')
