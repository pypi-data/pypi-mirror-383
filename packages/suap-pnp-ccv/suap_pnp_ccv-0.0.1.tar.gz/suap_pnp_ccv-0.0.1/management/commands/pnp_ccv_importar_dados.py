from djtools.management.commands import BaseCommandPlus
from pnp_ccv.services import PnpService


class Command(BaseCommandPlus):
    def check(self, *args, **kwargs):
        pass

    def check_migrations(self, *args, **kwargs):
        pass
    
    def handle(self, *args, **options):
        service = PnpService()
        service.importar_dados(19)
