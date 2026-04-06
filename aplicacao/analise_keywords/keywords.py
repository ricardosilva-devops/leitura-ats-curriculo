"""
Keywords críticas e padrões de seções para análise ATS.

Define palavras-chave técnicas importantes e padrões
para identificar seções em currículos.
"""

# =============================================================================
# KEYWORDS CRÍTICAS (Alta importância na análise)
# =============================================================================

CRITICAL_KEYWORDS = {
    # Tecnologias Core
    "linux", "aws", "docker", "kubernetes", "terraform", "ansible",
    "python", "bash", "shell", "nginx", "postgresql", "mysql",
    "zabbix", "prometheus", "grafana", "jenkins", "gitlab",
    "azure", "gcp", "google cloud", "ec2", "s3", "vpc",
    
    # Ferramentas importantes
    "git", "ci/cd", "pipeline", "devops", "sre", "monitoring",
    "elasticsearch", "redis", "mongodb", "kafka",
    
    # Conceitos críticos
    "troubleshooting", "automação", "automation", "scripting",
    "backup", "disaster recovery", "high availability",
    
    # Certificações
    "certificação", "certificado", "aws certified", "cka", "ckad",
    "lpic", "rhcsa", "rhce",
    
    # Níveis (importante para match)
    "sênior", "senior", "pleno", "júnior", "junior",
    
    # Idiomas (crítico para algumas vagas)
    "inglês", "ingles", "english", "fluente", "avançado",
    
    # Modalidade
    "remoto", "presencial", "híbrido", "home office", "remote",
}


# =============================================================================
# KEYWORDS DE SEÇÕES (Para identificar estrutura do currículo)
# =============================================================================

SECTION_KEYWORDS = {
    "dados_pessoais": [
        "dados pessoais", "informações pessoais", "contato",
        "personal info", "contact", "sobre mim", "about me"
    ],
    "objetivo": [
        "objetivo", "objetivo profissional", "objective",
        "career objective", "meta profissional"
    ],
    "resumo": [
        "resumo", "resumo profissional", "perfil", "profile",
        "summary", "professional summary", "sobre",
        "apresentação", "introduction"
    ],
    "experiencia": [
        "experiência", "experiência profissional", "experience",
        "work experience", "histórico profissional", "carreira",
        "employment history", "work history"
    ],
    "formacao": [
        "formação", "formação acadêmica", "educação", "education",
        "academic background", "escolaridade", "graduação",
        "pós-graduação", "mestrado", "doutorado"
    ],
    "habilidades": [
        "habilidades", "habilidades técnicas", "competências",
        "skills", "technical skills", "conhecimentos",
        "hard skills", "soft skills", "tecnologias"
    ],
    "idiomas": [
        "idiomas", "línguas", "languages", "proficiência linguística"
    ],
    "certificacoes": [
        "certificações", "certificados", "cursos", "certifications",
        "training", "treinamentos", "qualificações"
    ],
    "projetos": [
        "projetos", "portfólio", "portfolio", "projects",
        "trabalhos", "cases", "realizações"
    ],
}


# =============================================================================
# PATTERNS PARA EXTRAÇÃO DE DADOS
# =============================================================================

DATA_PATTERNS = {
    "email": r'[\w\.-]+@[\w\.-]+\.\w+',
    "telefone_br": r'(?:\+55\s?)?\(?[1-9]{2}\)?\s?(?:9\s?)?[0-9]{4}[-\s]?[0-9]{4}',
    "linkedin": r'linkedin\.com/in/[\w-]+',
    "github": r'github\.com/[\w-]+',
    "data_periodo": r'(?:jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)[a-z]*[.\s/]*\d{2,4}',
}


# =============================================================================
# KEYWORDS POR ÁREA (Para identificar perfil)
# =============================================================================

AREA_KEYWORDS = {
    "infraestrutura": [
        "linux", "servidor", "server", "infraestrutura", "infra",
        "datacenter", "virtualização", "vmware", "hypervisor",
        "storage", "rede", "network", "firewall", "vpn",
        "backup", "disaster recovery", "alta disponibilidade"
    ],
    "cloud": [
        "aws", "azure", "gcp", "cloud", "ec2", "s3", "lambda",
        "serverless", "iaas", "paas", "saas", "multi-cloud",
        "cloud native", "migration"
    ],
    "devops": [
        "devops", "ci/cd", "pipeline", "jenkins", "gitlab ci",
        "github actions", "docker", "kubernetes", "k8s",
        "terraform", "ansible", "automation", "gitops"
    ],
    "sre": [
        "sre", "site reliability", "observability", "monitoring",
        "alerting", "incident", "on-call", "slo", "sli",
        "postmortem", "chaos engineering"
    ],
    "desenvolvimento": [
        "python", "java", "javascript", "golang", "node",
        "api", "rest", "microservices", "backend", "frontend",
        "full stack", "software engineer"
    ],
    "banco_dados": [
        "postgresql", "mysql", "mongodb", "redis", "oracle",
        "sql server", "dba", "database", "sql", "nosql",
        "replicação", "backup", "tuning"
    ],
    "seguranca": [
        "security", "segurança", "pentest", "vulnerability",
        "firewall", "waf", "siem", "compliance", "gdpr",
        "lgpd", "iso 27001", "cybersecurity"
    ],
}


def get_area_for_keywords(keywords: list) -> dict:
    """
    Identifica as áreas de atuação baseado nas keywords encontradas.
    
    Args:
        keywords: Lista de keywords do currículo
        
    Returns:
        Dict com áreas e seus scores
    """
    keywords_lower = [k.lower() for k in keywords]
    area_scores = {}
    
    for area, area_keywords in AREA_KEYWORDS.items():
        matches = sum(1 for kw in area_keywords if kw in keywords_lower)
        if matches > 0:
            area_scores[area] = {
                "count": matches,
                "percentage": round((matches / len(area_keywords)) * 100, 1),
                "matched": [kw for kw in area_keywords if kw in keywords_lower]
            }
    
    return area_scores
