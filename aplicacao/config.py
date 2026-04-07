"""
Configuração centralizada da aplicação.

Separa configurações por ambiente (desenvolvimento vs produção)
e centraliza constantes de segurança.
"""

import os


class Config:
    """Configuração base."""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'pdf'}
    ALLOWED_MIME_TYPES = {'application/pdf'}
    PDF_MAGIC_BYTES = b'%PDF'
    
    # Logging
    LOG_DETAILED = os.environ.get('LOG_DETAILED', 'false').lower() == 'true'
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Segurança
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    """Configuração para desenvolvimento local."""
    DEBUG = True
    LOG_DETAILED = True  # Em dev, log completo é útil


class ProductionConfig(Config):
    """Configuração para produção."""
    DEBUG = False
    LOG_DETAILED = False  # Em prod, não logar dados sensíveis
    
    def __init__(self):
        # Em produção, SECRET_KEY deve ser definida via ambiente
        if self.SECRET_KEY == 'dev-secret-key-change-in-production':
            import warnings
            warnings.warn(
                "SECRET_KEY não foi definida! Use variável de ambiente SECRET_KEY em produção.",
                RuntimeWarning
            )


class TestingConfig(Config):
    """Configuração para testes."""
    TESTING = True
    DEBUG = True
    LOG_DETAILED = False


def get_config():
    """Retorna configuração baseada no ambiente."""
    env = os.environ.get('FLASK_ENV', os.environ.get('APP_ENV', 'development'))
    
    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    return configs.get(env, DevelopmentConfig)()
