# =============================================================================
# Gunicorn Configuration
# =============================================================================
# Uso: gunicorn -c gunicorn/gunicorn.conf.py wsgi:app

import multiprocessing

# Bind
bind = "127.0.0.1:8000"

# Workers
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5

# Processo
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = None
group = None

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)sμs'

# Server
graceful_timeout = 30
preload_app = True
max_requests = 1000
max_requests_jitter = 50

# SSL (desabilitado - usar Nginx para SSL)
# keyfile = None
# certfile = None
