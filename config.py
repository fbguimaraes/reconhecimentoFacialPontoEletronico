"""
Módulo de configuração do Sistema de Reconhecimento Facial.
Carrega configurações de arquivo .ini ou variáveis de ambiente.
"""

import os
import configparser
from pathlib import Path

# Diretório base (funciona tanto em desenvolvimento quanto em .exe)
if getattr(os.sys, 'frozen', False):
    # Rodando como .exe
    BASE_DIR = Path(os.sys.executable).parent
else:
    # Rodando como script Python
    BASE_DIR = Path(__file__).parent

CONFIG_FILE = BASE_DIR / "config.ini"

# Configurações padrão
DEFAULT_CONFIG = {
    'API': {
        'BASE_URL': 'http://localhost:8000/api',
        'TIMEOUT': '5'
    },
    'CAMERA': {
        'CAMERA_INDEX': '0',
        'WIDTH': '640',
        'HEIGHT': '480'
    },
    'RECOGNITION': {
        'THRESHOLD': '0.40',
        'CAPTURE_FRAMES': '10'
    }
}


class Config:
    """Classe de configuração centralizada."""
    
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def load_config(self):
        """Carrega configurações do arquivo .ini ou usa padrões."""
        if CONFIG_FILE.exists():
            try:
                self.config.read(CONFIG_FILE)
                print(f"✓ Configurações carregadas de: {CONFIG_FILE}")
            except Exception as e:
                print(f"⚠ Erro ao ler config.ini: {e}")
                print("  Usando configurações padrão")
                self._load_defaults()
        else:
            print(f"⚠ Arquivo config.ini não encontrado em: {CONFIG_FILE}")
            print("  Criando arquivo de configuração padrão...")
            self._load_defaults()
            self._create_default_config()
    
    def _load_defaults(self):
        """Carrega configurações padrão."""
        for section, options in DEFAULT_CONFIG.items():
            if section not in self.config.sections():
                self.config.add_section(section)
            for key, value in options.items():
                self.config.set(section, key, value)
    
    def _create_default_config(self):
        """Cria arquivo config.ini padrão."""
        try:
            CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_FILE, 'w') as f:
                self.config.write(f)
            print(f"✓ Arquivo config.ini criado em: {CONFIG_FILE}")
        except Exception as e:
            print(f"✗ Erro ao criar config.ini: {e}")
    
    def get(self, section, option, fallback=None):
        """Obtém valor de configuração."""
        try:
            return self.config.get(section, option)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback or DEFAULT_CONFIG.get(section, {}).get(option)
    
    def getint(self, section, option, fallback=None):
        """Obtém valor inteiro de configuração."""
        try:
            return self.config.getint(section, option)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            if fallback is not None:
                return fallback
            value = DEFAULT_CONFIG.get(section, {}).get(option)
            return int(value) if value else 0
    
    def getfloat(self, section, option, fallback=None):
        """Obtém valor float de configuração."""
        try:
            return self.config.getfloat(section, option)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            if fallback is not None:
                return fallback
            value = DEFAULT_CONFIG.get(section, {}).get(option)
            return float(value) if value else 0.0
    
    # Propriedades de acesso rápido
    @property
    def api_url(self):
        """URL base da API Django."""
        return self.get('API', 'BASE_URL')
    
    @property
    def api_timeout(self):
        """Timeout das requisições API."""
        return self.getint('API', 'TIMEOUT')
    
    @property
    def camera_index(self):
        """Índice da câmera."""
        return self.getint('CAMERA', 'CAMERA_INDEX')
    
    @property
    def camera_width(self):
        """Largura da câmera."""
        return self.getint('CAMERA', 'WIDTH')
    
    @property
    def camera_height(self):
        """Altura da câmera."""
        return self.getint('CAMERA', 'HEIGHT')
    
    @property
    def recognition_threshold(self):
        """Limiar de reconhecimento."""
        return self.getfloat('RECOGNITION', 'THRESHOLD')
    
    @property
    def capture_frames(self):
        """Número de frames para captura."""
        return self.getint('RECOGNITION', 'CAPTURE_FRAMES')
    
    @property
    def models_dir(self):
        """Diretório de modelos."""
        return BASE_DIR / "models"
    
    @property
    def data_dir(self):
        """Diretório de dados."""
        return BASE_DIR / "data"
    
    @property
    def logs_dir(self):
        """Diretório de logs."""
        return BASE_DIR / "logs"


# Instância global de configuração
config = Config()


def get_resource_path(relative_path):
    """
    Obtém caminho absoluto de recursos (funciona para dev e .exe).
    Usado para acessar arquivos empacotados no executável.
    """
    if getattr(os.sys, 'frozen', False):
        # Rodando como .exe (PyInstaller)
        base_path = os.sys._MEIPASS
    else:
        # Rodando como script Python
        base_path = BASE_DIR
    
    return os.path.join(base_path, relative_path)
