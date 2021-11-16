"""
Module to interact with Hashicorp Vault.
"""
import hvac


class Vault:
    def __init__(
        self,
        vault_url: str,
        vault_token: str,
        ensure_unseal: bool = True,
        unseal_keys: list = [],
    ) -> None:
        self.client = hvac.Client(url=vault_url, token=vault_token)

        if self.client.sys.is_sealed():
            if ensure_unseal:
                if not unseal_keys:
                    raise AttributeError(
                        "You passed `unsure_unseal` as True, but did not pass `unseal_keys`."
                    )
                else:
                    # Unseal with keys
                    self.client.sys.submit_unseal_keys(unseal_keys)

            else:
                raise AttributeError(
                    "Vault is sealed, and you passed `ensure_unseal` as False."
                )

        if not self.client.is_authenticated():
            raise AttributeError(
                "Vault authentication failed. Please check credentials"
            )

    def get_secret(self, mount_point: str, path: str, key: str) -> str:
        """
        Returns the secret (defined by a key) located at a given path
        """

        read_response = self.client.secrets.kv.read_secret_version(
            path=path, mount_point=mount_point
        )

        return read_response["data"]["data"][key]
