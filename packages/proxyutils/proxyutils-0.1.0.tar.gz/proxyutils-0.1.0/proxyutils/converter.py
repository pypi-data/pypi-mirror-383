import re
from typing import List, Optional


class Converter:

    RE_CREDENTIAL_CHARS = r"[^@:| ]"
    RE_CREDENTIALS = f"{RE_CREDENTIAL_CHARS}+:{RE_CREDENTIAL_CHARS}+"

    RE_SUBNET = r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
    RE_IP = rf"{RE_SUBNET}\.{RE_SUBNET}\.{RE_SUBNET}\.{RE_SUBNET}"
    RE_DOMAIN = r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]"

    RE_PORT = r"\d+"
    RE_IP_PORT = rf"{RE_IP}:{RE_PORT}"
    RE_DOMAIN_PORT = rf"{RE_DOMAIN}:{RE_PORT}"
    
    RE_SCHEME = r"(?:https?://|socks4a?://|socks5h?://)"

    def __init__(
            self,
            target_string: str,
            regex_delimiter: str = "@",
            scheme: Optional[str] = None,
        ):
        if not target_string or not isinstance(target_string, str):
            raise ValueError("target_string must be a non-empty string")

        self.target_string = target_string.strip().replace("\n", "").replace("\t", "")
        self.regex_delimiter = regex_delimiter
        self.scheme = scheme


    def convert(self) -> str:
        regex_list = [self.RE_CREDENTIALS, self.RE_DOMAIN_PORT, self.RE_IP_PORT]
        return self.convert_string_to_proxy(self.target_string, regex_list)


    def convert_string_to_proxy(self, target_string: str, regex_list: List[str]) -> str:
        scheme = None

        scheme_matches = re.findall(self.RE_SCHEME, target_string)
        if scheme_matches:
            scheme = scheme_matches[0]
            target_string_without_scheme = target_string.replace(scheme, "", 1)

        else:
            target_string_without_scheme = target_string

        parts = self._get_regex_matches(target_string_without_scheme, regex_list)
        proxy = self.regex_delimiter.join(parts)
        if scheme:
            proxy = scheme + proxy
            
        proxy = self.add_scheme_to_proxy(proxy)

        return proxy


    def _get_regex_matches(self, target_string: str, regex_list: List[str]) -> List[str]:
        parts = []

        for regex in regex_list:
            matches = re.findall(regex, target_string)
            if regex == self.RE_CREDENTIALS:
                #credentials regex may also match parts suitable for domain-port. if so, clear them.
                matches = [match for match in matches if not re.findall(self.RE_DOMAIN_PORT, match)]

            matches = [match for match in matches if regex == self.RE_IP_PORT or not re.findall(self.RE_IP_PORT, match)]

            if matches:
                match = matches[0]
                parts.append(match)
                target_string = target_string.replace(match, "", 1)

        if not parts:
            raise ValueError(f"Couldn't match any regex in target string: {self.target_string!r}")

        return parts


    def add_scheme_to_proxy(self, proxy: str) -> str:
        """
        Adds the overrider scheme if provided, otherwise ensures default scheme.
        """
        scheme_matches = re.findall(self.RE_SCHEME, proxy)

        if self.scheme:
            if scheme_matches:
                proxy = proxy.replace(scheme_matches[0], "", 1)
            return self.scheme + proxy

        if scheme_matches:
            return proxy
        return "http://" + proxy


