"""
Stopwords em Português para análise ATS.

Lista de palavras a serem ignoradas na tokenização,
incluindo termos genéricos de vagas e currículos.
"""

STOPWORDS_PT = {
    # Artigos
    "o", "a", "os", "as", "um", "uma", "uns", "umas",
    
    # Preposições
    "de", "da", "do", "das", "dos", "em", "na", "no", "nas", "nos",
    "por", "para", "com", "sem", "sob", "sobre", "entre", "até",
    "e", "ou", "que", "se", "ao", "aos", "à", "às",
    
    # Conjunções
    "mas", "porém", "contudo", "todavia", "entretanto",
    "porque", "pois", "como", "quando", "onde", "qual", "quais",
    
    # Verbos auxiliares / comuns
    "é", "são", "ser", "estar", "ter", "haver", "foi", "era", "será",
    "sendo", "sido", "tenho", "tinha", "tive", "fazendo", "faz", "fazer",
    
    # Pronomes
    "eu", "tu", "ele", "ela", "nós", "vós", "eles", "elas",
    "você", "vocês", "seu", "sua", "seus", "suas", "nosso", "nossa",
    "este", "esta", "esse", "essa", "aquele", "aquela", "isto", "isso",
    "meu", "minha", "meus", "minhas",
    
    # Advérbios comuns
    "não", "sim", "muito", "pouco", "mais", "menos", "bem", "mal",
    "já", "ainda", "sempre", "nunca", "também", "só", "apenas",
    "aqui", "ali", "lá", "cá", "onde", "aonde",
    
    # Numerais básicos
    "um", "dois", "três", "quatro", "cinco", "seis", "sete",
    "oito", "nove", "dez",
    
    # Termos genéricos de currículos
    "currículo", "curriculum", "vitae", "cv",
    "experiência", "experiencias", "experiência profissional",
    "anos", "ano", "meses", "mês", "dias", "dia",
    "conhecimento", "conhecimentos", "habilidade", "habilidades",
    "trabalho", "trabalhar", "empresa", "empresas", "time", "equipe",
    "área", "setor", "departamento", "cargo", "cargos", "função",
    "responsabilidades", "responsabilidade", "atividades", "atividade",
    "perfil", "candidato", "candidata", "profissional", "profissionais",
    
    # Termos genéricos de vagas
    "vaga", "vagas", "oportunidade", "oportunidades",
    "requisitos", "requisito", "necessário", "necessária",
    "obrigatório", "obrigatória", "desejável", "diferencial", "diferenciais",
    "benefícios", "benefício", "salário", "remuneração",
    "contrato", "regime",
    
    # Outros comuns
    "the", "and", "or", "of", "to", "in", "for", "with", "is", "are", "be",
    "bom", "boa", "bons", "boas", "melhor", "pior", "ótimo", "excelente",
    "novo", "nova", "novos", "novas", "grande", "grandes", "pequeno", "pequena",
    "todo", "toda", "todos", "todas", "cada", "algum", "alguma", "alguns", "algumas",
    "nenhum", "nenhuma", "outro", "outra", "outros", "outras",
    "primeiro", "primeira", "último", "última", "segundo", "segunda",
    "hora", "horas", "semana", "semanas", "período", "atual", "atualmente",
}

# Verbos de ação comuns em currículos (NÃO remover - são importantes)
ACTION_VERBS = {
    "desenvolvi", "desenvolver", "implementei", "implementar",
    "gerenciei", "gerenciar", "liderando", "liderei", "liderar",
    "criei", "criar", "otimizei", "otimizar",
    "automatizei", "automatizar", "migrei", "migrar",
    "administrei", "administrar", "configurei", "configurar",
    "monitorei", "monitorar", "analisei", "analisar",
    "coordenei", "coordenar", "supervisionei", "supervisionar",
    "planejei", "planejar", "executei", "executar",
    "reduzi", "reduzir", "aumentei", "aumentar",
    "melhorei", "melhorar", "construí", "construir",
}
