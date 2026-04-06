"""
Dicionário de sinônimos técnicos para análise ATS.

Permite que o sistema reconheça termos equivalentes,
como "AWS" e "Amazon Web Services", "K8s" e "Kubernetes".
"""

TECH_SYNONYMS = {
    # ==========================================================================
    # SISTEMAS OPERACIONAIS
    # ==========================================================================
    "linux": [
        "gnu/linux", "centos", "ubuntu", "debian", "rhel", "red hat",
        "rocky linux", "alma linux", "fedora", "mint", "suse", 
        "oracle linux", "amazon linux"
    ],
    "windows": [
        "windows server", "win server", "microsoft windows",
        "windows 10", "windows 11", "active directory", "ad"
    ],
    
    # ==========================================================================
    # CLOUD PROVIDERS
    # ==========================================================================
    "aws": [
        "amazon web services", "amazon aws", "ec2", "s3", "rds",
        "lambda", "cloudwatch", "vpc", "iam", "elastic", "elasticache",
        "route53", "cloudfront", "eks", "ecs", "fargate", "sqs", "sns",
        "dynamodb", "aurora", "redshift", "glacier", "aws cloud"
    ],
    "azure": [
        "microsoft azure", "azure devops", "azure cloud",
        "azure ad", "azure functions", "azure kubernetes", "aks"
    ],
    "gcp": [
        "google cloud", "google cloud platform", "gke", "bigquery",
        "cloud run", "cloud functions", "gce", "gcs"
    ],
    "cloud": [
        "nuvem", "computação em nuvem", "cloud computing",
        "infraestrutura cloud", "cloud native", "multi-cloud"
    ],
    
    # ==========================================================================
    # CONTAINERS E ORQUESTRAÇÃO
    # ==========================================================================
    "docker": [
        "container", "containers", "containerização", "docker-compose",
        "docker compose", "dockerfile", "docker swarm", "containerd",
        "podman", "docker hub"
    ],
    "kubernetes": [
        "k8s", "kube", "kubectl", "helm", "orquestração de containers",
        "eks", "aks", "gke", "openshift", "rancher", "minikube",
        "kind", "k3s"
    ],
    
    # ==========================================================================
    # SERVIDORES WEB
    # ==========================================================================
    "nginx": [
        "engine-x", "proxy reverso", "reverse proxy",
        "load balancer nginx", "nginx plus"
    ],
    "apache": [
        "httpd", "apache2", "apache httpd", "apache web server",
        "apache http"
    ],
    "gunicorn": [
        "green unicorn", "wsgi server", "python wsgi"
    ],
    
    # ==========================================================================
    # MONITORAMENTO E OBSERVABILIDADE
    # ==========================================================================
    "zabbix": [
        "monitoramento zabbix", "zabbix server", "zabbix agent",
        "zabbix proxy", "zabbix monitoring"
    ],
    "prometheus": [
        "prom", "promql", "prometheus server", "prometheus monitoring"
    ],
    "grafana": [
        "dashboards grafana", "grafana dashboards",
        "visualização métricas", "grafana labs"
    ],
    "datadog": [
        "dd-agent", "apm datadog", "datadog monitoring"
    ],
    "newrelic": [
        "new relic", "nr agent", "new relic apm"
    ],
    "elk": [
        "elasticsearch", "logstash", "kibana", "elastic stack",
        "elk stack", "opensearch"
    ],
    
    # ==========================================================================
    # BANCO DE DADOS
    # ==========================================================================
    "postgresql": [
        "postgres", "psql", "pg", "banco postgresql", "postgre"
    ],
    "mysql": [
        "mariadb", "maria db", "percona", "mysql server"
    ],
    "mongodb": [
        "mongo", "nosql mongodb", "mongoose", "mongo db"
    ],
    "redis": [
        "redis cache", "redis server", "elasticache redis", "redis cluster"
    ],
    "oracle": [
        "oracle db", "oracle database", "plsql", "pl/sql"
    ],
    "sql server": [
        "mssql", "microsoft sql", "sqlserver", "tsql", "t-sql"
    ],
    
    # ==========================================================================
    # IaC E AUTOMAÇÃO
    # ==========================================================================
    "terraform": [
        "tf", "hcl", "terragrunt", "infraestrutura como código terraform",
        "terraform cloud", "terraform enterprise"
    ],
    "ansible": [
        "playbook", "playbooks ansible", "ansible tower", "awx",
        "ansible automation"
    ],
    "puppet": [
        "puppet enterprise", "puppetserver", "puppet agent"
    ],
    "chef": [
        "chef infra", "chef automate", "chef server"
    ],
    "cloudformation": [
        "cfn", "aws cloudformation", "cloud formation"
    ],
    
    # ==========================================================================
    # CI/CD
    # ==========================================================================
    "jenkins": [
        "jenkins pipeline", "jenkinsfile", "jenkins ci",
        "jenkins automation"
    ],
    "gitlab": [
        "gitlab ci", "gitlab-ci", "gitlab runner", "gitlab devops",
        "gitlab ci/cd"
    ],
    "github": [
        "github actions", "gh actions", "github ci", "github enterprise"
    ],
    "bitbucket": [
        "bitbucket pipelines", "atlassian bitbucket"
    ],
    "azure devops": [
        "azure pipelines", "tfs", "team foundation", "vsts"
    ],
    "argocd": [
        "argo cd", "argo", "gitops"
    ],
    
    # ==========================================================================
    # SCRIPTING E PROGRAMAÇÃO
    # ==========================================================================
    "bash": [
        "shell", "shell script", "shellscript", "sh", "script bash",
        "scripts shell", "automação shell", "linux shell"
    ],
    "python": [
        "py", "python3", "scripting python", "automação python",
        "scripts python", "python programming"
    ],
    "powershell": [
        "ps1", "pwsh", "powershell script", "windows powershell"
    ],
    "go": [
        "golang", "go lang", "linguagem go"
    ],
    "javascript": [
        "js", "node", "nodejs", "node.js", "ecmascript"
    ],
    "java": [
        "jvm", "spring", "spring boot", "maven", "gradle"
    ],
    
    # ==========================================================================
    # NETWORKING
    # ==========================================================================
    "tcp/ip": [
        "tcp_ip", "tcpip", "rede tcp", "protocolo tcp",
        "tcp ip", "networking"
    ],
    "dns": [
        "bind", "dns server", "servidor dns", "resolução dns",
        "named", "route53"
    ],
    "vpn": [
        "openvpn", "wireguard", "ipsec", "vpn site-to-site",
        "túnel vpn", "strongswan", "vpn ssl"
    ],
    "firewall": [
        "iptables", "nftables", "firewalld", "pfsense",
        "security groups", "nacl", "waf", "ufw"
    ],
    "load balancer": [
        "balanceamento de carga", "haproxy", "elb", "alb", "nlb",
        "load balancing", "lb"
    ],
    
    # ==========================================================================
    # VERSIONAMENTO
    # ==========================================================================
    "git": [
        "github", "gitlab", "bitbucket", "controle de versão",
        "versionamento", "git flow", "gitflow"
    ],
    "svn": [
        "subversion", "apache svn"
    ],
    
    # ==========================================================================
    # CARGOS E FUNÇÕES
    # ==========================================================================
    "devops": [
        "dev ops", "devops engineer", "engenheiro devops",
        "analista devops", "devops specialist"
    ],
    "sre": [
        "site reliability", "site reliability engineer",
        "engenheiro sre", "sre engineer"
    ],
    "sysadmin": [
        "system administrator", "administrador de sistemas",
        "admin sistemas", "administrador linux", "sys admin"
    ],
    "infraestrutura": [
        "infra", "infrastructure", "infra de ti",
        "infraestrutura de ti", "infra engineer"
    ],
    "platform engineer": [
        "platform engineering", "engenheiro de plataforma"
    ],
    
    # ==========================================================================
    # METODOLOGIAS
    # ==========================================================================
    "agile": [
        "ágil", "metodologia ágil", "agile methodology"
    ],
    "scrum": [
        "metodologia scrum", "sprint", "daily scrum"
    ],
    "kanban": [
        "quadro kanban", "kanban board"
    ],
    "devops culture": [
        "cultura devops", "devsecops", "sre culture"
    ],
    
    # ==========================================================================
    # CONCEITOS
    # ==========================================================================
    "alta disponibilidade": [
        "ha", "high availability", "redundância", "failover",
        "cluster ha", "99.9%", "99.99%"
    ],
    "escalabilidade": [
        "scaling", "auto scaling", "horizontal scaling",
        "escala horizontal", "escalável", "autoscaling"
    ],
    "troubleshooting": [
        "resolução de problemas", "diagnóstico", "rca",
        "root cause analysis", "análise de causa raiz",
        "debugging", "problem solving"
    ],
    "backup": [
        "backup e restore", "disaster recovery", "dr",
        "recuperação de desastres", "backup recovery"
    ],
    "segurança": [
        "security", "cybersecurity", "infosec",
        "segurança da informação", "security best practices"
    ],
}


def get_all_synonyms(term: str) -> list:
    """
    Retorna todos os sinônimos de um termo, incluindo ele mesmo.
    
    Args:
        term: Termo para buscar sinônimos
        
    Returns:
        Lista de sinônimos ou lista vazia se não encontrado
    """
    term_lower = term.lower()
    
    # Verificar se é uma chave principal
    if term_lower in TECH_SYNONYMS:
        return [term_lower] + TECH_SYNONYMS[term_lower]
    
    # Verificar se é um sinônimo
    for canonical, synonyms in TECH_SYNONYMS.items():
        if term_lower in [s.lower() for s in synonyms]:
            return [canonical] + synonyms
    
    return []


def find_canonical_term(term: str) -> str | None:
    """
    Encontra o termo canônico para um sinônimo.
    
    Args:
        term: Termo ou sinônimo
        
    Returns:
        Termo canônico ou None se não encontrado
    """
    term_lower = term.lower()
    
    if term_lower in TECH_SYNONYMS:
        return term_lower
    
    for canonical, synonyms in TECH_SYNONYMS.items():
        if term_lower in [s.lower() for s in synonyms]:
            return canonical
    
    return None
