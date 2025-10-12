from datetime import date, timedelta
from djtools.db import models
from ae.models import Caracterizacao
from edu.models import Aluno, Matriz, SituacaoMatricula, CursoCampus, ProcedimentoMatricula
from processo_seletivo.models import OfertaVagaCurso, Candidato
from django.db.models import F
from . import mapeamento


class Configuracao(models.ModelPlus):
    ano = models.IntegerField(verbose_name="Ano")
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_fim = models.DateField(verbose_name="Data de Fim")
    data_envio = models.DateField(verbose_name="Data de Envio", null=True, blank=True)

    data_inicio_correcao = models.DateField(verbose_name="Data de Início da Correção", null=True)
    data_fim_correcao = models.DateField(verbose_name="Data de Fim da Correção", null=True)

    class Meta:
        verbose_name = "Configuração"
        verbose_name_plural = "Configurações"

    def __str__(self):
        return f"Configuração do ano {self.ano}"

    @classmethod
    def get_data_inicio(cls):
        configuracao = Configuracao.objects.order_by('ano').last()
        if configuracao and not hasattr(cls, '_data_inicio'):
            setattr(cls, '_data_inicio', configuracao.data_inicio)
        return getattr(cls, '_data_inicio', None)

    @classmethod
    def get_data_fim(cls):
        configuracao = Configuracao.objects.order_by('ano').last()
        if configuracao and not hasattr(cls, '_data_fim'):
            setattr(cls, '_data_fim', configuracao.data_fim)
        return getattr(cls, '_data_fim', None)


class Raca(models.ModelPlus):
    nome = models.CharFieldPlus(verbose_name='Nome')
    codigo = models.IntegerField(verbose_name='Código')
    racas = models.ManyToManyFieldPlus('comum.Raca', verbose_name='Raças SUAP')

    class Meta:
        verbose_name = 'Raça'
        verbose_name_plural = 'Raças'
    
    def __str__(self):
        return self.nome


class Turno(models.ModelPlus):
    nome = models.CharFieldPlus(verbose_name='Nome')
    codigo = models.IntegerField(verbose_name='Código')
    turnos = models.ManyToManyFieldPlus('edu.Turno', verbose_name='Turnos SUAP')

    class Meta:
        verbose_name = 'Turno'
        verbose_name_plural = 'Turnos'
    
    def __str__(self):
        return self.nome


class FonteFinanciamento(models.ModelPlus):
    nome = models.CharFieldPlus(verbose_name='Nome')
    codigo = models.IntegerField(verbose_name='Código')
    convenios = models.ManyToManyFieldPlus('edu.Convenio', verbose_name='Convênios SUAP')

    class Meta:
        verbose_name = 'Fonte de Financiamento'
        verbose_name_plural = 'Fontes de Financiamento'
    

    def __str__(self):
        return self.nome


class Cota(models.ModelPlus):
    nome = models.CharFieldPlus(verbose_name='Nome')
    codigo = models.IntegerField(verbose_name='Código')
    formas_ingresso = models.ManyToManyFieldPlus('edu.FormaIngresso', verbose_name='Formas de Ingresso SUAP')

    class Meta:
        verbose_name = 'Cota'
        verbose_name_plural = 'Cotas'
    

    def __str__(self):
        return self.nome

class Curso(models.ModelPlus):
    nome = models.CharFieldPlus(verbose_name='Nome')
    codigo = models.IntegerField(verbose_name='Código')
    codigo_catalogo = models.IntegerField(verbose_name='Código do Catálogo')
    codigo_unidade = models.IntegerField(verbose_name='Código da Unidade')
    
    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
    

    def __str__(self):
        return f"{self.codigo} - {self.nome}"


class Ciclo(models.ModelPlus):
    curso = models.ForeignKeyPlus(Curso, verbose_name='Curso', on_delete=models.CASCADE)
    nome = models.CharFieldPlus(verbose_name='Nome')
    codigo = models.IntegerField(verbose_name='Código')
    turmas = models.ManyToManyFieldPlus('edu.Turma', verbose_name='Turmas')

    class Meta:
        verbose_name = 'Ciclo'
        verbose_name_plural = 'Ciclos'
    
    def __str__(self):
        return f"{self.codigo} - {self.nome}"

    def get_alunos(self):
        pks = self.turmas.values_list('matriculaperiodo__aluno')
        return Aluno.objects.filter(pk__in=pks)

    def get_ingressantes(self):
        qs = Aluno.objects.none()
        for turma, curso_campus, ano_letivo, periodo_letivo in self.turmas.values_list('pk', 'curso_campus', 'ano_letivo', 'periodo_letivo'):
            qs = qs | Aluno.objects.filter(matriculaperiodo__turma=turma, curso_campus=curso_campus, ano_letivo=ano_letivo, periodo_letivo=periodo_letivo)
        return qs

    def get_ofertas_vaga_curso(self):
        pks = self.get_ingressantes().order_by('candidato_vaga__oferta_vaga__oferta_vaga_curso').values_list('candidato_vaga__oferta_vaga__oferta_vaga_curso', flat=True).distinct()
        return OfertaVagaCurso.objects.filter(pk__in=pks).order_by('edital')

    def get_inscritos(self):
        pks = self.get_ofertas_vaga_curso().order_by('ofertavaga__candidatovaga__candidato').values_list('ofertavaga__candidatovaga__candidato', flat=True).distinct()
        return Candidato.objects.filter(pk__in=pks)

    def get_matrizes(self):
        pks = self.get_ingressantes().values_list('matriz', flat=True).order_by('matriz')
        return Matriz.objects.filter(pk__in=pks).order_by('pk')

    def get_fonte_financiamento(self):
        return self.turmas.filter(matriculaperiodo__aluno__convenio__isnull=False).values_list('matriculaperiodo__aluno__convenio__fontefinanciamento__nome', flat=True).order_by('matriculaperiodo__aluno__convenio__fontefinanciamento__nome').distinct().first()

    def get_codigo_fonte_financiamento(self):
        return self.turmas.filter(matriculaperiodo__aluno__convenio__isnull=False).values_list('matriculaperiodo__aluno__convenio__fontefinanciamento__codigo', flat=True).order_by('matriculaperiodo__aluno__convenio__fontefinanciamento__codigo').distinct().first()

    def get_turnos(self):
        pks = self.turmas.order_by('matriculaperiodo__aluno__turno').values_list('matriculaperiodo__aluno__turno', flat=True).distinct()
        return ', '.join(Turno.objects.filter(turnos__in=pks).values_list('nome', flat=True))

    def get_data_inicio(self):
        return self.turmas.order_by('calendario_academico__data_inicio').values_list('calendario_academico__data_inicio', flat=True).first()

    def get_data_termino(self):
        data_termino = None
        periodicidade = self.turmas.values_list('curso_campus__periodicidade', flat=True).first()
        qtd_periodos_letivos = self.get_matrizes().values_list('qtd_periodos_letivos', flat=True).first()
        if periodicidade == CursoCampus.PERIODICIDADE_ANUAL:
            data_inicio = self.get_data_inicio()
            if data_inicio:
                data_termino = data_inicio + timedelta(days=1 + (365.25 * qtd_periodos_letivos))
        elif periodicidade == CursoCampus.PERIODICIDADE_SEMESTRAL:
            data_inicio = self.get_data_inicio()
            if data_inicio:
                data_termino = self.get_data_inicio() + timedelta(days=1 + (182.625 * qtd_periodos_letivos))
        else:
            data_termino = self.turmas.order_by('calendario_academico__data_fim').values_list('calendario_academico__data_fim', flat=True).first()
        return data_termino

    def get_carga_horaria(self):
        matriz = self.get_matrizes().first()
        return matriz.get_ch_total() if matriz else None

    def get_total_inscritos(self):
        return self.get_inscritos().count()

    def get_evadidos(self):
        return self.get_ingressantes().filter(situacao=SituacaoMatricula.EVASAO, matriculaperiodo__procedimentomatricula__data__lte=Configuracao.get_data_fim(), matriculaperiodo__procedimentomatricula__tipo=ProcedimentoMatricula.EVASAO)

    def get_detalhamento_vagas(self):
        uo = None
        vagas = {}
        total = 0
        edital = None
        qs = self.get_ofertas_vaga_curso().values_list('edital', 'ofertavaga__lista__forma_ingresso__cota__nome', 'ofertavaga__qtd', 'curso_campus')
        for edital, sigla, qtd, curso_campus in qs:
            if sigla:
                total += qtd
                if sigla not in vagas:
                    vagas[sigla] = qtd
                else:
                    vagas[sigla] = +qtd
            if uo is None:
                uo = CursoCampus.objects.filter(pk=curso_campus).values_list('diretoria__setor__uo', flat=True).first()
        return dict(edital=edital, uo=uo, total=total, vagas=vagas)

    def get_dados_alunos(self, queryset=None):
        pks = (self.get_ingressantes() if queryset is None else queryset).values_list('pk', flat=True)

        procedimentos = {
            pk: dict(tipo=tipo, data=data)
            for pk, tipo, data in ProcedimentoMatricula.objects.filter(
                matricula_periodo__aluno__in=pks,
                data__lte=Configuracao.get_data_fim()
            ).values_list('matricula_periodo__aluno', 'tipo', 'data').order_by('data')
            if tipo not in (ProcedimentoMatricula.TRANCAMENTO_COMPULSORIO, ProcedimentoMatricula.TRANCAMENTO_VOLUNTARIO)
        }

        procedimentos_posteriores = {
            pk: dict(tipo=tipo, data=data)
            for pk, tipo, data in ProcedimentoMatricula.objects.filter(
                matricula_periodo__aluno__in=pks,
                data__gt=Configuracao.get_data_fim()
            ).values_list('matricula_periodo__aluno', 'tipo', 'data').order_by('data')
            if tipo not in (ProcedimentoMatricula.TRANCAMENTO_COMPULSORIO, ProcedimentoMatricula.TRANCAMENTO_VOLUNTARIO)
        }

        def calcular_faixa_renda(aluno):
            faixa_renda = 'Não Declarada'
            try:
                caracterizacao = aluno.caracterizacao
            except Caracterizacao.DoesNotExist:
                caracterizacao = None
            if caracterizacao:
                renda_per_capita = caracterizacao.renda_per_capita
                if renda_per_capita is not None:
                    if renda_per_capita <= 0.5:
                        faixa_renda = '0<RFP<=0,5'
                    elif renda_per_capita >= 0.5 and renda_per_capita <= 1.0:
                        faixa_renda = '0,5<RFP<=1,0'
                    elif renda_per_capita >= 1.0 and renda_per_capita <= 1.5:
                        faixa_renda = '1,0<RFP<=1,5'
                    elif renda_per_capita >= 1.5 and renda_per_capita <= 2.5:
                        faixa_renda = '1,5<RFP<=2,5'
                    elif renda_per_capita >= 2.5 and renda_per_capita <= 3.5:
                        faixa_renda = '2,5<RFP<=3,5'
                    elif renda_per_capita >= 3.5:
                        faixa_renda = 'RFP>3,5'
            return faixa_renda
        
        def calcular_situacao(aluno):
            data_inicio = Configuracao.get_data_inicio()
            data_fim = Configuracao.get_data_fim()
            procedimento = procedimentos.get(aluno.pk)
            procedimento_posterior = procedimentos_posteriores.get(aluno.pk)
            
            if aluno.situacao_id in (SituacaoMatricula.CONCLUIDO, SituacaoMatricula.FORMADO) and aluno.dt_conclusao_curso > Configuracao.get_data_fim():
                situacao_atual = dict(descricao=aluno.situacao.descricao, procedimento=dict(tipo="Conclusão", data=aluno.dt_conclusao_curso))
            elif procedimento_posterior:
                situacao_atual = dict(descricao=aluno.situacao.descricao, procedimento=dict(tipo=procedimento_posterior['tipo'], data=procedimento_posterior['data']))
            else:
                situacao_atual = dict(descricao=aluno.situacao.descricao, procedimento=None)
    
            if aluno.situacao_id in (SituacaoMatricula.CONCLUIDO, SituacaoMatricula.FORMADO) and aluno.dt_conclusao_curso <= Configuracao.get_data_fim():
                situacao = dict(
                    atual=situacao_atual,
                    pnp=dict(
                        codigo = mapeamento.SITUACAO_MATRICULA.get(aluno.situacao_id),
                        descricao = mapeamento.SITUACAO_MATRICULA_PNP.get(
                            mapeamento.SITUACAO_MATRICULA.get(aluno.situacao_id)
                        ),
                        data=aluno.dt_conclusao_curso
                    )
                )
            elif procedimento:
                situacao = dict(
                    atual=situacao_atual,
                    pnp=dict(
                        codigo = mapeamento.PROCEDIMENTO_MATRICULA.get(procedimento["tipo"]),
                        descricao = mapeamento.SITUACAO_MATRICULA_PNP.get(
                            mapeamento.PROCEDIMENTO_MATRICULA.get(procedimento["tipo"])
                        ),
                        data=procedimento["data"]
                    )
                )
            elif procedimento_posterior or (aluno.dt_conclusao_curso and aluno.dt_conclusao_curso > Configuracao.get_data_fim()):
                situacao = dict(
                    atual=situacao_atual,
                    pnp=dict(
                        codigo = mapeamento.SITUACAO_MATRICULA.get(SituacaoMatricula.MATRICULADO),
                        descricao = mapeamento.SITUACAO_MATRICULA_PNP.get(
                            mapeamento.SITUACAO_MATRICULA.get(SituacaoMatricula.MATRICULADO)
                        ),
                        data=aluno.data_matricula.date()
                    )
                )
            else:
                situacao = dict(
                    atual=situacao_atual,
                    pnp=dict(
                        codigo = mapeamento.SITUACAO_MATRICULA.get(aluno.situacao_id),
                        descricao = mapeamento.SITUACAO_MATRICULA_PNP.get(
                            mapeamento.SITUACAO_MATRICULA.get(aluno.situacao_id)
                        ),
                        data=aluno.data_matricula.date()
                    )
                )
            situacao["ativo"] = situacao["pnp"]["descricao"] == "EM_CURSO" or (
                data_fim >= situacao["pnp"]["data"] >= data_inicio
            )
            return situacao
        
        return [
            {
                "matricula": aluno.matricula,
                "nome": aluno.pessoa_fisica.nome,
                "cpf": aluno.pessoa_fisica.cpf,
                "codigo_matricula": aluno.codigo_sistec,
                "data_matricula": aluno.data_matricula,
                "forma_ingresso": aluno.forma_ingresso.descricao.split(' - ')[0],
                "situacao": calcular_situacao(aluno),
                "raca": aluno.pessoa_fisica.raca.raca_set.values_list('nome', flat=True).first() if aluno.pessoa_fisica.raca else None,
                "renda": calcular_faixa_renda(aluno),
                "turno": aluno.turno.turno_set.values_list('nome', flat=True).first()
            } for aluno in Aluno.objects.filter(pk__in=pks).select_related('pessoa_fisica', 'situacao')
        ]


class Vaga(models.ModelPlus):
    ciclo = models.ForeignKeyPlus(Ciclo, verbose_name='Ciclo')
    cota = models.ForeignKeyPlus(Cota, verbose_name='Cota')
    regular = models.IntegerField(verbose_name='Regular', default=0)
    extraordinaria = models.IntegerField(verbose_name='Extraordinária', default=0)

    class Meta:
        verbose_name = 'Vaga'
        verbose_name_plural = 'Vagas'
