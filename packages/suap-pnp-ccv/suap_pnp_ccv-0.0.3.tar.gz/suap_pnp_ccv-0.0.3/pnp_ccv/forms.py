from djtools import forms


class ConfiguracaoForm(forms.FormPlus):
    url = forms.CharField(label='URL PNP', help_text='URL da API da PNP.', required=False)
    token = forms.CharField(label='Token PNP', help_text='Token de autenticação na PNP.', required=False)
    

class SincronizacaoInicialForm(forms.FormPlus):
    confirmar = forms.BooleanField(label="Confirmar sincronização", help_text="Após a sincronização inicial será necessário mapear os cadastros de turnos, cotas, raças e fontes de financiamento com os respectivos cadastrados no SUAP.")


class SelecionarUnidadeForm(forms.FormPlus):
    unidade = forms.ChoiceField(label="Unidade", choices=[["19", "Campus Apodi"]])
