
from django.contrib import admin
from django.utils.safestring import mark_safe
from djtools.contrib.admin import ModelAdminPlus
from .models import Configuracao, Raca, FonteFinanciamento, Turno, Cota, Curso, Ciclo, Vaga


class ConfiguracaoAdmin(ModelAdminPlus):
    list_display_icons = True
    list_display = 'ano', 'data_inicio', 'data_fim', 'data_envio', 'data_inicio_correcao', 'data_fim_correcao'

admin.site.register(Configuracao, ConfiguracaoAdmin)


class RacaAdmin(ModelAdminPlus):
    list_display_icons = True
    list_display = 'codigo', 'nome', 'racas_suap'
    list_filter = 'racas',
    readonly_fields = 'codigo', 'nome'

    def racas_suap(self, obj):
        return ', '.join(obj.racas.values_list('descricao', flat=True))

    racas_suap.short_description = 'Raças SUAP'

admin.site.register(Raca, RacaAdmin)


class TurnoAdmin(ModelAdminPlus):
    list_display_icons = True
    list_display = 'codigo', 'nome', 'turnos_suap'
    list_filter = 'turnos',
    readonly_fields = 'codigo', 'nome'

    def turnos_suap(self, obj):
        return ', '.join(obj.turnos.values_list('descricao', flat=True))

    turnos_suap.short_description = 'Turno SUAP'

admin.site.register(Turno, TurnoAdmin)


class CotaAdmin(ModelAdminPlus):
    list_display_icons = True
    list_display = 'codigo', 'nome', 'formas_de_ingresso_suap'
    list_filter = 'formas_ingresso',
    readonly_fields = 'codigo', 'nome'

    def formas_de_ingresso_suap(self, obj):
        return ', '.join(obj.formas_ingresso.values_list('descricao', flat=True))

    formas_de_ingresso_suap.short_description = 'Formas de Ingresso SUAP'

admin.site.register(Cota, CotaAdmin)


class FonteFinanciamentoAdmin(ModelAdminPlus):
    list_display_icons = True
    list_display = 'codigo', 'nome', 'convenios_suap'
    list_filter = 'convenios',
    readonly_fields = 'codigo', 'nome'

    def convenios_suap(self, obj):
        return ', '.join(obj.convenios.values_list('descricao', flat=True))

    convenios_suap.short_description = 'Convênios SUAP'


admin.site.register(FonteFinanciamento, FonteFinanciamentoAdmin)


class CursoAdmin(ModelAdminPlus):
    list_display_icons = True
    search_fields = 'codigo', 'nome'
    list_display = 'get_codigo_nome', 'codigo_catalogo', 'codigo_unidade', 'get_ciclos'
    list_filter = 'ciclo__turmas__curso_campus__diretoria', 'ciclo__turmas__curso_campus',
    readonly_fields = 'codigo', 'nome', 'codigo_unidade'

    def get_codigo_nome(self, obj):
        return str(obj)

    get_codigo_nome.short_description = 'Código/Nome'

    def get_ciclos(self, obj):
        ul = ['<ul>']
        for nome in obj.ciclo_set.values_list('nome', flat=True):
            ul.append(f'<li>{nome}</li>')
        ul.append('</ul>')
        return mark_safe(''.join(ul))

    get_ciclos.short_description = 'Ciclos'


admin.site.register(Curso, CursoAdmin)



class VagaInline(admin.TabularInline):
    model = Vaga
    extra = 0


class CicloAdmin(ModelAdminPlus):
    list_display_icons = True
    search_fields = 'codigo', 'nome'
    list_display = 'get_codigo_nome', 'get_data_inicio', 'get_data_termino', 'get_carga_horaria', 'get_turnos', 'get_total_inscritos', 'get_total_ingressantes', 'get_total_evadidos', 'get_turmas', 'get_fonte_financiamento', 'get_quantidade_vagas'
    list_filter = 'turmas__curso_campus', 'turmas'
    inlines = VagaInline,
    list_per_page = 25
    readonly_fields = 'codigo', 'nome'

    def get_codigo_nome(self, obj):
        return str(obj)

    get_codigo_nome.short_description = 'Código/Nome'

    def get_turmas(self, obj):
        links = []
        for pk, codigo in obj.turmas.values_list('pk', 'codigo'):
            links.append(f'<a target="_blank" href="/edu/turma/{pk}/">{codigo}</a>')
        return mark_safe(' '.join(links))

    get_turmas.short_description = 'Turmas de Ingresso'

    def get_fonte_financiamento(self, obj):
        return obj.get_fonte_financiamento()

    get_fonte_financiamento.short_description = 'Fonte Financ.'

    def get_turnos(self, obj):
        return obj.get_turnos()

    get_turnos.short_description = 'Turnos'

    def get_data_inicio(self, obj):
        return obj.get_data_inicio()

    get_data_inicio.short_description = 'Início'

    def get_data_termino(self, obj):
        return obj.get_data_termino()

    get_data_termino.short_description = 'Término'

    def get_carga_horaria(self, obj):
        matriz = obj.get_matrizes().first()
        if matriz:
            return mark_safe(f'<a target="_blank" href="/edu/matriz/{matriz.id}/">{matriz.get_ch_total()}</a>')
        return None

    get_carga_horaria.short_description = 'CH'

    def get_total_inscritos(self, obj):
        return mark_safe(
            f'<a class="popup" href="/pnp_ccv/inscritos_ciclo/{obj.pk}/">{obj.get_total_inscritos()}</a>'
        )

    get_total_inscritos.short_description = 'Insc.'

    def get_total_ingressantes(self, obj):
        return mark_safe(
            f'<a class="popup" href="/pnp_ccv/alunos_ciclo/{obj.pk}/">{obj.get_ingressantes().count()}</a>'
        )

    get_total_ingressantes.short_description = 'Ingres.'
    
    def get_total_evadidos(self, obj):
        return mark_safe(
            f'<a class="popup" href="/pnp_ccv/evadidos_ciclo/{obj.pk}/">{obj.get_evadidos().count()}</a>'
        )

    get_total_evadidos.short_description = 'Evad.'
    
    def get_quantidade_vagas(self, obj):
        dados = obj.get_detalhamento_vagas()
        total = f'<a target="_blank" href="/processo_seletivo/edital/{dados['edital']}/?tab=vagas&uo_selecionada={dados['uo']}">{dados['total']}<a>'
        detalhamento = ', '.join([f'{sigla}: {qtd}' for sigla, qtd in dados['vagas'].items()])
        return mark_safe(f'{total}<br/>{detalhamento}')

    get_quantidade_vagas.short_description = 'Vagas Regulares'


admin.site.register(Ciclo, CicloAdmin)