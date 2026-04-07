"""
Keywords críticas e padrões de seções para análise ATS.

Define palavras-chave técnicas importantes e padrões
para identificar seções em currículos.

Baseado em estudo de keywords para perfil de Infraestrutura/DevOps.
"""

# =============================================================================
# KEYWORDS POR NÍVEL DE IMPORTÂNCIA
# =============================================================================

# ALTA PRIORIDADE (Critical) - Keywords principais que definem o perfil
KEYWORDS_CRITICAL = {
    # Sistemas Operacionais
    "linux", "centos", "ubuntu", "rocky linux", "debian", "rhel", "mint",
    
    # Cloud AWS
    "aws", "ec2", "s3", "glacier", "vpc", "cloudformation", "lambda", "rds",
    
    # Containers e Web Stack
    "docker", "nginx", "gunicorn", "supervisor", "apache",
    
    # Banco de Dados
    "postgresql", "mysql", "mongodb", "redis", "mariadb",
    
    # Monitoramento
    "zabbix", "prometheus", "grafana", "datadog", "nagios",
    
    # Scripting e Automação
    "shell script", "bash", "automação", "python", "powershell",
    
    # Versionamento
    "git", "bitbucket", "gitlab", "github",
    
    # Redes
    "tcp/ip", "dns", "vpn", "openvpn", "firewall", "load balancer",
    
    # Conceitos Core
    "troubleshooting", "migração", "observabilidade", "rca",
    "sustentação", "infraestrutura", "redução de incidentes",
    
    # IaC (se aplicável)
    "terraform", "ansible", "kubernetes", "k8s", "helm", "argocd",
    
    # DevOps
    "ci/cd", "jenkins", "pipeline", "devops", "sre",
}

# MÉDIA PRIORIDADE (High) - Keywords secundárias importantes
KEYWORDS_HIGH = {
    # Ferramentas e conceitos secundários
    "logs", "tuning", "backup", "recovery", "restore",
    "documentação", "padronização", "disponibilidade",
    "estabilidade", "crontab", "sla", "checklists",
    
    # Ferramentas específicas
    "rclone", "cups", "samba", "lpd", "smtp",
    
    # Redes secundárias
    "dhcp", "vlan", "traceroute", "gateway", "roteamento",
    "latência", "conectividade", "monitoramento de link",
    
    # Monitoramento secundário
    "alertas", "dashboards", "monitoramento", "triggers", "templates",
    
    # Cloud secundário
    "cloudwatch", "iam", "route53", "eks", "ecs",
    
    # Containers secundário
    "docker-compose", "dockerfile", "containerd",
    
    # Telecom
    "telecom", "operação 24/7", "incidentes", "atendimento n2",
}

# BAIXA PRIORIDADE (Medium) - Keywords de contexto operacional
KEYWORDS_MEDIUM = {
    # Contexto operacional
    "chamados", "incidentes", "tickets", "suporte",
    "n1", "n2", "n3", "escalonamento", "triagem",
    
    # Ferramentas de suporte
    "glpi", "acesso remoto", "anydesk", "teamviewer", "putty", "dwservice",
    
    # Contexto de trabalho
    "operação 24/7", "plantão", "on-call", "escala 24/7",
    "tratativa de incidentes", "análise de causa", "diagnóstico de rede",
    "pós-implantação", "implantação",
    
    # Sistemas secundários
    "windows", "windows server", "active directory",
}

# Combinar todas para compatibilidade com código existente
CRITICAL_KEYWORDS = KEYWORDS_CRITICAL | KEYWORDS_HIGH


# =============================================================================
# KEYWORDS DE SEÇÕES (Para identificar estrutura do currículo)
# =============================================================================

SECTION_KEYWORDS = {
    "dados_pessoais": [
        "dados pessoais", "informações pessoais", "informacoes pessoais",
        "personal info", "contact info", "contato:"
    ],
    "objetivo": [
        "objetivo profissional", "objetivo:", "career objective",
        "meta profissional"
    ],
    "resumo": [
        "resumo profissional", "perfil profissional", "resumo:",
        "summary", "professional summary", "apresentação profissional",
        "sobre mim", "perfil:"
    ],
    "experiencia": [
        "experiência profissional", "experiencia profissional",
        "experiências", "work experience", "histórico profissional",
        "employment history", "work history", "experiência:"
    ],
    "formacao": [
        "formação acadêmica", "formacao academica", "educação",
        "education", "academic background", "escolaridade",
        "graduação", "pós-graduação", "formação:"
    ],
    "habilidades": [
        "habilidades técnicas", "habilidades tecnicas", "habilidades:",
        "habilidades e idiomas", "habilidades/idiomas",
        "competências técnicas", "competencias tecnicas",
        "technical skills", "hard skills", "conhecimentos técnicos",
        "conhecimentos tecnicos", "tecnologias:", "skills:",
        "stack técnica", "stack tecnica", "ferramentas e tecnologias"
    ],
    "idiomas": [
        "idiomas:", "línguas:", "languages:", "proficiência linguística"
    ],
    "certificacoes": [
        "certificações:", "certificados:", "certifications:",
        "cursos e certificações", "qualificações:"
    ],
    "projetos": [
        "projetos:", "portfólio:", "portfolio:", "projects:",
        "principais projetos", "realizações:"
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
        "backup", "disaster recovery", "alta disponibilidade",
        "sustentação", "troubleshooting"
    ],
    "cloud": [
        "aws", "azure", "gcp", "cloud", "ec2", "s3", "lambda",
        "serverless", "iaas", "paas", "saas", "multi-cloud",
        "cloud native", "migration", "glacier", "vpc"
    ],
    "devops": [
        "devops", "ci/cd", "pipeline", "jenkins", "gitlab ci",
        "github actions", "docker", "kubernetes", "k8s",
        "terraform", "ansible", "automation", "gitops"
    ],
    "monitoramento": [
        "zabbix", "prometheus", "grafana", "datadog", "new relic",
        "nagios", "elk", "elasticsearch", "observabilidade",
        "alertas", "dashboards", "monitoramento", "logs"
    ],
    "banco_dados": [
        "postgresql", "mysql", "mariadb", "mongodb", "redis",
        "oracle", "sql server", "dba", "database", "sql", "nosql",
        "replicação", "backup", "tuning"
    ],
    "redes": [
        "tcp/ip", "dns", "dhcp", "vpn", "firewall", "vlan",
        "roteamento", "gateway", "latência", "conectividade",
        "openvpn", "iptables"
    ],
    "scripting": [
        "bash", "shell script", "python", "powershell",
        "automação", "scripts", "crontab"
    ],
}


def get_keyword_importance(keyword: str) -> str:
    """
    Retorna o nível de importância de uma keyword.
    
    Returns:
        "critical", "high", ou "medium"
    """
    kw_lower = keyword.lower()
    
    if kw_lower in KEYWORDS_CRITICAL:
        return "critical"
    elif kw_lower in KEYWORDS_HIGH:
        return "high"
    elif kw_lower in KEYWORDS_MEDIUM:
        return "medium"
    else:
        return "medium"  # Default


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
