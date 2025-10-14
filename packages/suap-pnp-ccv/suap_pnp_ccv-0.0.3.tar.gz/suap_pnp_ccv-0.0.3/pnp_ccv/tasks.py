from .services import PnpService
from djtools.assincrono import task


@task('ImportarDados de Unidade PNP')
def importar_dados(uo, task=None):
    service = PnpService()
    service.importar_dados(uo, task)


@task('Exportar Dados de Unidade PNP')
def exportar_dados(uo, task=None):
    service = PnpService()
    service.exportar_dados(uo, task)
