from djtools.apps import SuapAppConfig as AppConfig


class PnpCcvConfig(AppConfig):
    default = True
    name = 'pnp_ccv'
    verbose_name = 'PNP/CCV'
    area = 'Ensino'
    description = 'Integração com a PNP'
    icon = 'file-alt'
