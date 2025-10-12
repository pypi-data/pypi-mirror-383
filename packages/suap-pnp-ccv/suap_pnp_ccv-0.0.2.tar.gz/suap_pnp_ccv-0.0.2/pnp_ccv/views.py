from .models import Ciclo, Configuracao
from django.shortcuts import get_object_or_404
from djtools.utils import rtr, httprr
from .forms import SelecionarUnidadeForm
from . import tasks
from .services import PnpService

@rtr()
def sincronizacao_inicial(request):
    service = PnpService()
    service.sincronizacao_inicial()
    return httprr('/admin/pnp_ccv/configuracao/')


@rtr()
def importar_dados(request):
    title = "Sincronização Inicial"
    form = SelecionarUnidadeForm(data=request.POST or None)
    if form.is_valid():
        return tasks.importar_dados(form.cleaned_data["unidade"])
    return locals()

@rtr()
def alunos_ciclo(request, pk):
    obj = get_object_or_404(Ciclo.objects, pk=pk)
    title = obj.nome
    alunos = obj.get_dados_alunos()
    data_inicio = Configuracao.get_data_inicio()
    data_fim = Configuracao.get_data_fim()
    return locals()

@rtr()
def inscritos_ciclo(request, pk):
    obj = get_object_or_404(Ciclo.objects, pk=pk)
    title = obj.nome
    return locals()

@rtr('alunos_ciclo.html')
def evadidos_ciclo(request, pk):
    obj = get_object_or_404(Ciclo.objects, pk=pk)
    title = obj.nome
    alunos = obj.get_dados_alunos(obj.get_evadidos())
    data_inicio = Configuracao.get_data_inicio()
    data_fim = Configuracao.get_data_fim()
    return locals()

@rtr()
def exportar_dados(request):
    title = "Exportar Dados"
    form = SelecionarUnidadeForm(data=request.POST or None)
    if form.is_valid():
        return tasks.exportar_dados(form.cleaned_data["unidade"])
    return locals()