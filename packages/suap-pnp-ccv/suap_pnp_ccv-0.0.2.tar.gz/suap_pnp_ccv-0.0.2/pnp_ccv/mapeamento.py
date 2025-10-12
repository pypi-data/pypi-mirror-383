

SITUACAO_MATRICULA = {
    1: 3, #  Matriculado / EM_CURSO
    2: 3, #  Trancado / EM_CURSO
    3: 7, #  Jubilado / DESLIGADA
    4: 2, #  Transferido Interno / TRANSF_INT
    5: None, #  Concludente
    6: 11, #  Concluído / CONCLUIDA
    7: 7, #  Falecido / DESLIGADA
    8: 7, #  Afastado / DESLIGADA
    9: 4, #  Evasão / ABANDONO
    10: 12, #  Cancelado / CANCELADA
    11: 2, #  Transferido Externo / TRANSF_INT
    12: None, #  Estagiario (Concludente)
    13: None, #  Aguardando Colação de Grau
    14: None, #  Certificado ENEM
    15: None, #  Aguardando Seminário
    16: None, #  Aguardando ENADE
    17: None, #  Intercâmbio
    18: None, #  Egresso
    19: 11, #  Formado / CONCLUIDA
    20: 12, #  Cancelamento Compulsório / CANCELADA
    21: 3, #  Matrícula Vínculo Institucional / EM_CURSO
    25: 11, #  Integralizado Fase Escolar / CONCLUIDA
    97: 12, #  Cancelamento por Desligamento / CANCELADA
    98: 12, #  Cancelamento por Duplicidade / CANCELADA
    99: 3, #  Trancado Voluntariamente / EM_CURSO
    100: 10, #  Não concluído / REPROVADA
    101: None, #  Transferido SUAP
    102: 12, #  Não Concluído / REPROVADA
}

SITUACAO_MATRICULA_PNP = {
    1: 'INTEGRALIZADA',
    2: 'TRANSF_INT',
    3: 'EM_CURSO',
    4: 'ABANDONO',
    5: 'NAO_DECLARADA',
    6: 'TRANSF_EXT',
    7: 'DESLIGADA',
    8: 'SUBSTITUIDO',
    9: 'EXCLUIDO',
    10: 'REPROVADA',
    11: 'CONCLUIDA',
    12: 'CANCELADA'
}

PROCEDIMENTO_MATRICULA = {
    'Intercâmbio': 12, # CANCELADA
    'Trancamento Compulsório': 3, # EM_CURSO
    'Trancamento Voluntário': 3, # EM_CURSO
    'Cancelamento Compulsório': 12, # CANCELADA
    'Cancelamento Voluntário': 12, # CANCELADA
    'Cancelamento por Duplicidade': 12, # CANCELADA
    'Cancelamento por Desligamento': 12, # CANCELADA
    'Evasão': 4, # ABANDONO
    'Jubilamento': 7, # DESLIGADA
    'Reintegração': 3, # EM_CURSO
    'Transferência Intercampus': 2, # TRANSF_INT
    'Transferência de Curso': 2, # TRANSF_INT
    'Transferência Externa': 6, # TRANSF_EXT
    'Matrícula Vínculo': 3, # EM_CURSO
    'Integralização Fase Escolar': 11, # CONCLUIDA
}