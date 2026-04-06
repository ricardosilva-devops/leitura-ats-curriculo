"""
WSGI Entry Point para Gunicorn.

Este arquivo é usado pelo Gunicorn para iniciar a aplicação.
Uso: gunicorn wsgi:app
"""

from app import app

if __name__ == '__main__':
    app.run()
