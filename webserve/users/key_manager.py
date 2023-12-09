
from azure.identity import EnvironmentCredential
from azure.keyvault.secrets import SecretClient
from cryptography.fernet import Fernet

from .models import User, UserKeys
from django.conf import settings

import logging
logger = logging.getLogger('default')


class _EncryptionKeyManager:

    def __init__(self) -> None:
        self._keys = {}  # user_id => keyname
        self._credentials = EnvironmentCredential()  # assume someone loaded dotenvs. happens in settings.
        self._client = SecretClient(settings.AZURE_KEYVAULT_URL, self._credentials)

    def get_key(self, user : User) -> str:
        if user.pk in self._keys:
            return self._keys[user.pk]
        
        # Try to get key name
        try:
            user_key = UserKeys.objects.get(active=1, user=user)
        except UserKeys.DoesNotExist:
            # no key set up yet - create one.
            return self._create_key(user)
        else:
            return self._read_from_kv(user_key.name)
        
    def _create_key(self, user : User) -> str:
        # create a key, save it, then create a username.
        logger.info("Creating key for %s", user.pk)
        key_name = f"fa-{user.pk}"
        key = EncryptionWrapper.get_key()
        self._write_to_kv(key_name, key)
        UserKeys.objects.create(
            user=user,
            name=key_name
        )
        return key

    def _write_to_kv(self, key_name, key_value):
        self._client.set_secret(key_name, key_value)

    def _read_from_kv(self, key_name):
        return self._client.get_secret(key_name).value


class EncryptionWrapper:

    def __init__(self) -> None:
        pass

    def encrypt(self, user : User, message : str) -> bytes:
        key = encryption_manager.get_key(user)
        cipher_suite = Fernet(key)
        return cipher_suite.encrypt(message.encode())
    
    def decrypt(self, user : User, message : bytes) -> str:
        key = encryption_manager.get_key(user)
        cipher_suite = Fernet(key)
        return cipher_suite.decrypt(message).decode()
    
    @classmethod
    def get_key(cls) -> bytes:
        return Fernet.generate_key().decode()


# we want a singleton
encryption_manager = _EncryptionKeyManager()
