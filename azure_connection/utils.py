from azure.core.exceptions import HttpResponseError
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient

KEY_VAULT_NAME="key-vault-gr7-part-3"
KVUri = f"https://{KEY_VAULT_NAME}.vault.azure.net"

class AzureCredential():
    def __init__(self):
        self.credential = ClientSecretCredential(
            tenant_id='c0040114-3f9c-4a21-9388-5d5d5c5fbefa',
            client_id='e7c3c26f-2e1d-407b-aace-5b03ac5be6ea',
            client_secret='EOz8Q~hlcN6tNTH_hvg4Fe.HZFDKlgzlrTqVecQG'
        )
        self.client = SecretClient(vault_url=KVUri, credential=self.credential)

    def get_secret_value(self, secret_name: str):
        try:
            return self.client.get_secret(secret_name).value
        except HttpResponseError as e:
            print(f"An error occurred while retrieving secret '{secret_name}': {e}")
            return None




