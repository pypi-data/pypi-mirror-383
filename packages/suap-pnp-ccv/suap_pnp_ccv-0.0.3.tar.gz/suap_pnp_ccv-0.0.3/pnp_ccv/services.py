
import json
import requests
from tqdm import tqdm
from datetime import datetime
from django.db.models import F
from edu.models import Aluno, MatriculaPeriodo, Turma
from .models import Configuracao, Raca, Turno, Cota, FonteFinanciamento, Curso, Ciclo, Vaga
from comum.models import Configuracao as ConfiguracaoSUAP

class PnpService:

    
    def __init__(self, *args, **kwargs):
        self.url = ConfiguracaoSUAP.get_valor_por_chave('pnp_ccv', 'url')
        self.token = ConfiguracaoSUAP.get_valor_por_chave('pnp_ccv', 'token')
    

    def sincronizacao_inicial(self):
        url = f'{self.url}/api/v2/integracao/sincronizacao_inicial'
        dados = requests.get(url).json()
        Configuracao.objects.update_or_create(
            ano=dados["configuracao"]["ano"],
            defaults=dict(
                data_inicio=datetime.strptime(dados["configuracao"]["data_inicio"], "%d/%m/%Y"),
                data_fim=datetime.strptime(dados["configuracao"]["data_fim"], "%d/%m/%Y"),
                data_envio=datetime.strptime(dados["configuracao"]["data_envio"], "%d/%m/%Y"),
                data_inicio_correcao=datetime.strptime(dados["configuracao"]["data_inicio_correcao"], "%d/%m/%Y"),
                data_fim_correcao=datetime.strptime(dados["configuracao"]["data_fim_correcao"], "%d/%m/%Y"),
            )
        )
        for item in dados["racas"]:
            Raca.objects.update_or_create(codigo=item["codigo"], defaults=dict(nome=item["nome"]))
        for item in dados["turnos"]:
            Turno.objects.update_or_create(codigo=item["codigo"], defaults=dict(nome=item["nome"]))
        for item in dados["fontes_financiamento"]:
            FonteFinanciamento.objects.update_or_create(codigo=item["codigo"], defaults=dict(nome=item["nome"]))
        for item in dados["cotas"]:
            Cota.objects.update_or_create(codigo=item["codigo"], defaults=dict(nome=item["nome"]))
    
    def unidades_usuario(self, cpf):
        url = f'{self.url}/api/v2/integracao/unidades_usuario/{cpf}'
        return requests.get(url).json()

    def importar_dados(self, codigo_unidade, task=None):
        url = f'{self.url}/api/v2/integracao/exportar_dados_unidade/{codigo_unidade}'
        dados = requests.get(url).json()
        for item in (task.iterate(dados) if task else tqdm(dados)):
            curso = Curso.objects.update_or_create(codigo=item["codigo"], defaults=dict(nome=item["nome"], codigo_catalogo=item["codigo_catalogo"], codigo_unidade=item["codigo_unidade"]))[0]
            cotas = Cota.objects.all()
            for item2 in item["ciclos"]:
                ciclo = Ciclo.objects.update_or_create(codigo=item2["codigo"], defaults=dict(curso=curso, nome=item2["nome"]))[0]
                codigos = [item3["codigo"] for item3 in item2["alunos"]]
                qs = MatriculaPeriodo.objects.filter(aluno__codigo_sistec__in=codigos, ano_letivo=F('aluno__ano_letivo'), periodo_letivo=F('aluno__periodo_letivo'))
                pks = list(qs.order_by('aluno__curso_campus').values_list('aluno__curso_campus', flat=True))
                curso_campus = max(set(pks), key=pks.count)
                pks = qs.filter(turma__curso_campus=curso_campus).order_by('turma').values_list('turma', flat=True).distinct()
                ciclo.turmas.set(pks)
                for cota in cotas:
                    Vaga.objects.update_or_create(ciclo=ciclo, cota=cota, defaults=dict())
            task.finalize("Importação realizada com sucesso.", "/admin/pnp_ccv/configuracao/")
                
    def exportar_dados(self, codigo_unidade, task=None):
        cursos = Curso.objects.filter(codigo_unidade=codigo_unidade)[0:1]
        dados = [
            {
                "codigo_curso": curso.codigo,
                "codigo_catalogo": curso.codigo_catalogo,
                "ciclos": [
                    {
                        "codigo": ciclo.codigo,
                        "data_inicio": ciclo.get_data_inicio().strftime('%d/%m/%Y'),
                        "data_termino": ciclo.get_data_termino().strftime('%d/%m/%Y'),
                        "carga_horaria": ciclo.get_carga_horaria(),
                        "fonte_financiamento": ciclo.get_fonte_financiamento(),
                        "vagas": [
                            {
                                "cota": vaga.cota.nome,
                                "regular": vaga.regular,
                                "extraordinaria": vaga.extraordinaria
                            } for vaga in ciclo.vaga_set.all()
                        ],
                        "inscritos": ciclo.get_total_inscritos(),
                        "ingressantes": ciclo.get_ingressantes().count(),
                        "evadidos": ciclo.get_evadidos().count(),
                        "matriculas":[
                            {
                                "codigo": aluno['codigo_matricula'],
                                "data": aluno['data_matricula'].strftime('%d/%m/%Y'),
                                "situacao": aluno['situacao']['pnp']['descricao'] if aluno['situacao'] else None,
                                "data_situacao": aluno['situacao']['pnp']['data'].strftime('%d/%m/%Y') if aluno['situacao'] else None,
                                "raca": aluno['raca'],
                                "renda": aluno['renda'],
                                "turno": aluno['turno']
                            } for aluno in ciclo.get_dados_alunos()
                        ]
                    } for ciclo in curso.ciclo_set.all() if ciclo.turmas.exists()
                ]
            } for curso in (task.iterate(cursos) if task else tqdm(cursos))
        ]
        with open(f"{codigo_unidade}.json", "w") as file:
            file.write(json.dumps(dados, indent=1, ensure_ascii=False))
        if task:
            task.finalize("Dados exportados com sucesso.")
