import json
from django.db.models import F
from edu.models import Aluno, MatriculaPeriodo, Turma

with open("/Users/breno/Documents/Workspace/pnp/api/AP.json", "r") as file:
    dados = json.loads(file.read())

print(dados)
for item in dados["programas"]:
    print(item["codigo"], item["nome"])
for item in dados["cotas"]:
    print(item["codigo"], item["nome"])
for item in dados["cursos"]:
    print(item["codigo"], item["nome"], item["codigo_catalogo"])
    for item2 in item["ciclos"]:
        print(item2["codigo"], item2["nome"])
        qs = MatriculaPeriodo.objects.filter(aluno__codigo_sistec__in=item2["alunos"], ano_letivo=F('aluno__ano_letivo'), periodo_letivo=F('aluno__periodo_letivo'))
        pks = qs.filter(turma__isnull=False).order_by('turma').values_list('turma', flat=True).distinct()
        