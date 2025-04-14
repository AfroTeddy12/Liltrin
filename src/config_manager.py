import os
import json
from cryptography.fernet import Fernet
import base64
from pathlib import Path

class ConfigManager:
    def __init__(self):
        self.config_dir = Path(os.path.expanduser("~")) / ".trin_assistant"
        self.config_dir.mkdir(exist_ok=True)
        self.key_file = self.config_dir / "key.key"
        self.config_file = self.config_dir / "config.enc"
        self._key = None
        
    def _generate_key(self):
        """Generate a new encryption key"""
        return Fernet.generate_key()
        
    def _get_key(self):
        """Get the encryption key, generating if necessary"""
        if not self._key:
            if self.key_file.exists():
                with open(self.key_file, "rb") as f:
                    self._key = f.read()
            else:
                self._key = self._generate_key()
                with open(self.key_file, "wb") as f:
                    f.write(self._key)
        return self._key
        
    def _get_cipher(self):
        """Get the Fernet cipher instance"""
        return Fernet(self._get_key())
        
    def save_config(self, config_data):
        """Encrypt and save configuration data"""
        cipher = self._get_cipher()
        encrypted_data = cipher.encrypt(json.dumps(config_data).encode())
        with open(self.config_file, "wb") as f:
            f.write(encrypted_data)
            
    def load_config(self):
        """Load and decrypt configuration data"""
        if not self.config_file.exists():
            return {}
            
        cipher = self._get_cipher()
        with open(self.config_file, "rb") as f:
            encrypted_data = f.read()
        decrypted_data = cipher.decrypt(encrypted_data)
        return json.loads(decrypted_data)
        
    def update_config(self, key, value):
        """Update a specific configuration value"""
        config = self.load_config()
        config[key] = value
        self.save_config(config)
        
    def get_config(self, key, default=None):
        """Get a specific configuration value"""
        config = self.load_config()
        return config.get(key, default)
        
    def clear_config(self):
        """Clear all configuration data"""
        if self.config_file.exists():
            self.config_file.unlink()
        if self.key_file.exists():
            self.key_file.unlink() 