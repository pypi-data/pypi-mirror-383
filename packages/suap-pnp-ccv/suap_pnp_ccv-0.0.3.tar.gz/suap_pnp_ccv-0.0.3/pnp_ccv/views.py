from .models import Ciclo, Configuracao
from django.shortcuts import get_object_or_404
from djtools.utils import rtr, httprr, permission_required
from .forms import SincronizacaoInicialForm, SelecionarUnidadeForm
from . import tasks
from .services import PnpService

@rtr()
@permission_required('pnp_ccv.view_configuracao')
def sincronizacao_inicial(request):
    title = "Sincronização Inicial"
    form = SincronizacaoInicialForm(data=request.POST or None)
    if form.is_valid():
        service = PnpService()
        service.sincronizacao_inicial()
        return httprr('/admin/pnp_ccv/configuracao/', 'Sincronização inicial realizada com sucesso. Realise o mapeamento dos turnos, cotas, raças e fontes de financiamento.')
    return locals()

@rtr()
@permission_required('pnp_ccv.view_curso')
def importar_dados(request):
    title = "Importar Dados"
    form = SelecionarUnidadeForm(data=request.POST or None)
    service = PnpService()
    cpf = request.user.get_profile().cpf.replace('.', '').replace('-', '')
    form.fields["unidade"].choices = [
        [unidade["codigo"], unidade["nome"],] for unidade in service.unidades_usuario(cpf)
    ]
    if form.is_valid():
        return tasks.importar_dados(form.cleaned_data["unidade"])
    return locals()

@rtr()
@permission_required('pnp_ccv.view_curso')
def alunos_ciclo(request, pk):
    obj = get_object_or_404(Ciclo.objects, pk=pk)
    title = obj.nome
    alunos = obj.get_dados_alunos()
    data_inicio = Configuracao.get_data_inicio()
    data_fim = Configuracao.get_data_fim()
    return locals()

@rtr()
@permission_required('pnp_ccv.view_curso')
def inscritos_ciclo(request, pk):
    obj = get_object_or_404(Ciclo.objects, pk=pk)
    title = obj.nome
    return locals()

@rtr('alunos_ciclo.html')
@permission_required('pnp_ccv.view_curso')
def evadidos_ciclo(request, pk):
    obj = get_object_or_404(Ciclo.objects, pk=pk)
    title = obj.nome
    alunos = obj.get_dados_alunos(obj.get_evadidos())
    data_inicio = Configuracao.get_data_inicio()
    data_fim = Configuracao.get_data_fim()
    return locals()

@rtr()
@permission_required('pnp_ccv.view_curso')
def exportar_dados(request):
    title = "Exportar Dados"
    form = SelecionarUnidadeForm(data=request.POST or None)
    if form.is_valid():
        return tasks.exportar_dados(form.cleaned_data["unidade"])
    return locals()