from __future__ import annotations
from typing import Union, Optional

from .converter import Converter
from .extractor import Extractor

import re

class Proxy:
     
    def __init__(
            self,
            proxy_input: Union[str, dict, Proxy],
            scheme: Optional[str] = None,
        ):
        self.proxy_string = self.sanitize_proxy_input(proxy_input)

        if scheme and not scheme.endswith("://"):
            scheme = scheme + "://"

        self.converter = Converter(self.proxy_string, scheme=scheme)
    
        self.proxy_root = self.converter.convert()
        self.proxies = {
            "http": self.proxy_root,
            "https": self.proxy_root,
        }
        self.scheme = self.get_scheme(self.proxy_root)


    @classmethod
    def sanitize_proxy_input(cls, input: Optional[Union[str, dict, Proxy]] = None) -> str:
        """
        Normalize proxy input to a standard string format.

        Supported input formats:
        - Proxy instance
        - String URL, e.g., "http://user:pass@1.2.3.4:8080"
        - Dictionary with keys "http" or "http://", e.g., {"http": "..."} or httpx style
        """
        if isinstance(input, Proxy):
            return input.proxy_string

        if isinstance(input, str):
            return input.strip()

        if isinstance(input, dict):
            for key in ("http", "http://"):
                if key in input:
                    return input[key].strip()

        raise ValueError(
            "Unsupported proxy format. Supported formats: str, Proxy object, dict with 'http' or 'http://' key."
        )

    def get_proxy_parts(self) -> dict:
        extractor = Extractor(self.proxy_root)
        if self.is_authenticated:
            return extractor.get_authenticated_proxy_parts()

        else:
            return extractor.get_unauthenticated_proxy_parts()
            
    def get_scheme(self, input: str) -> str:
        """Return the full scheme including '://', e.g., 'http://'."""
        matches = re.findall(Converter.RE_SCHEME, input)
        if not matches:
            raise ValueError(f"No scheme found in proxy: {input!r}")
        return matches[0]

    @property
    def scheme_type(self) -> str:
        """Return scheme type without '://', e.g., 'http', 'socks5'."""
        return self.scheme.replace("://", "")

    @property
    def is_authenticated(self) -> bool:
        """Return True if the proxy includes username:password."""
        return "@" in self.proxy_root


