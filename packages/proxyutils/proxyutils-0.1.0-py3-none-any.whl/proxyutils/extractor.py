from .converter import Converter
from typing import Dict
import re

class Extractor:
    """Extract parts from a proxy string."""

    def __init__(self, proxy_root: str):
        self.proxy_root = proxy_root


    def get_authenticated_proxy_parts(self) -> Dict[str, str]:
        """
        Returns a dictionary with:
          - username
          - password
          - ip
          - port
        """
        plain_root = self._remove_schema_from_proxy_root()
        proxy_parts = plain_root.split("@")

        credential_part = proxy_parts[0]
        ip_part = proxy_parts[1]

        username, password = self._split_part(credential_part)
        ip, port = self._split_part(ip_part)

        return {
            "username": username,
            "password": password,
            "ip": ip,
            "port": int(port),
        }


    def get_unauthenticated_proxy_parts(self) -> dict:
        """Returns a dictionary with ip and port."""
        plain_root = self._remove_schema_from_proxy_root()
        ip, port = self._split_part(plain_root)

        return {
            "ip": ip,
            "port": int(port),
        }


    def _split_part(self, part: str) -> tuple[str, str]:
        """Splits a string 'a:b' into a tuple (a, b). Raises ValueError if invalid."""
        slices = part.split(":")
        if len(slices) != 2:
            raise ValueError(f"Invalid proxy part: {part!r}")
        return slices[0], slices[1]


    def _remove_schema_from_proxy_root(self) -> str:
        """Removes scheme like 'http://' or 'socks5://' from proxy_root."""
        schema_match = re.findall(Converter.RE_SCHEME, self.proxy_root)
        if schema_match:
            return self.proxy_root.replace(schema_match[0], "", 1)
        return self.proxy_root