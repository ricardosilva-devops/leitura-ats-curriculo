"""
Keywords críticas e padrões de seções para análise ATS.

Define palavras-chave técnicas importantes e padrões
para identificar seções em currículos.
"""

# =============================================================================
# KEYWORDS CRÍTICAS (Alta importância na análise)
# =============================================================================

CRITICAL_KEYWORDS = {
    # Sistemas Operacionais
    "linux", "ubuntu", "centos", "debian", "rhel", "red hat",
    "windows server", "unix", "freebsd",
    
    # Cloud
    "aws", "azure", "gcp", "google cloud", "ec2", "s3", "vpc",
    "lambda", "cloudformation", "ecs", "eks", "rds", "dynamodb",
    "cloudwatch", "iam", "route53", "cloudfront",
    
    # Containers e Orquestração
    "docker", "kubernetes", "k8s", "openshift", "rancher",
    "helm", "containerd", "podman", "docker compose",
    
    # IaC e Automação
    "terraform", "ansible", "puppet", "chef", "saltstack",
    "cloudformation", "pulumi", "vagrant",
    
    # CI/CD
    "jenkins", "gitlab", "github actions", "bitbucket pipelines",
    "circleci", "travis", "argocd", "spinnaker",
    
    # Monitoramento e Observabilidade
    "zabbix", "prometheus", "grafana", "datadog", "new relic",
    "nagios", "elk", "elasticsearch", "logstash", "kibana",
    "splunk", "dynatrace", "jaeger", "opentelemetry",
    
    # Redes e Segurança
    "tcp/ip", "dns", "vpn", "firewall", "nginx", "apache",
    "haproxy", "load balancer", "ssl", "tls", "iptables",
    "waf", "cloudflare",
    
    # Banco de Dados
    "postgresql", "mysql", "mariadb", "mongodb", "redis",
    "oracle", "sql server", "cassandra", "dynamodb",
    
    # Linguagens e Scripting
    "python", "bash", "shell", "powershell", "go", "golang",
    "ruby", "perl", "groovy",
    
    # Versionamento e Colaboração
    "git", "github", "gitlab", "bitbucket", "svn",
    
    # Metodologias e Práticas
    "devops", "sre", "gitops", "infrastructure as code",
    "ci/cd", "pipeline", "agile", "scrum", "kanban",
    
    # Virtualização
    "vmware", "vsphere", "hyper-v", "kvm", "proxmox", "xen",
    
    # Storage e Backup
    "storage", "san", "nas", "nfs", "ceph", "minio",
    "backup", "veeam", "bacula", "rsync",
    
    # Mensageria
    "kafka", "rabbitmq", "sqs", "sns", "activemq",
    
    # Ferramentas de Desenvolvimento
    "api", "rest", "graphql", "microservices", "serverless",
    
    # Certificações (abreviações técnicas)
    "aws certified", "cka", "ckad", "lpic", "rhcsa", "rhce",
    "azure certified", "gcp certified",
}


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
        "habilidades técnicas", "habilidades:", "competências técnicas",
        "technical skills", "hard skills", "conhecimentos técnicos",
        "tecnologias:", "skills:"
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
