from .services import PnpService
from djtools.assincrono import task


@task('Sincronização Inicial')
def importar_dados(uo, task=None):
    service = PnpService()
    service.importar_dados(uo, task)


@task('Exportar Dados PNP')
def exportar_dados(uo, task=None):
    service = PnpService()
    service.exportar_dados(uo, task)