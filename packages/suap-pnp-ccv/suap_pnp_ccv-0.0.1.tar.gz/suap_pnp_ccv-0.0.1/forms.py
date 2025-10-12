from djtools import forms


class SelecionarUnidadeForm(forms.FormPlus):
    unidade = forms.ChoiceField(label="Unidade", choices=[["19", "Campus Apodi"]])
