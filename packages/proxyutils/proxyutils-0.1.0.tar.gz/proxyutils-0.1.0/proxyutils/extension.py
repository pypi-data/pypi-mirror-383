from pathlib import Path
from typing import Union, Optional
import tempfile
import zipfile
import secrets
import shutil

from .extension_consts import MANIFEST, JS
from .proxy import Proxy


class Extension:
    """
    Creates a Chrome extension extension for browser with an authenticated proxy.
    The extension is stored in the temp folder.
    """

    EXTENSION_FOLDER_NAME = "proxy-extensions"

    def __init__(self, proxy: Union[str, dict, Proxy]):
        """
        Initialize the extension with a proxy.
        Raises ValueError if proxy is not authenticated.
        """
        self.proxy = Proxy(proxy)
        self.proxy_parts = self.proxy.get_proxy_parts()

        if not self.proxy.is_authenticated:
            raise ValueError("Proxy must be authenticated for chrome extension. Use --proxy-server argument for authenticated proxy.")

        # Use system temporary directory
        self.extension_folder_path = Path(tempfile.gettempdir()) / self.EXTENSION_FOLDER_NAME
        self.extension_folder_path.mkdir(parents=True, exist_ok=True)
        self.extension_path: Optional[Path] = None


    def create_extension_zip(self) -> Path:
        """
        Creates a Chrome extension zip file for Selenium in temp folder.
        Returns the full path to the zip.
        """
        extension_path = self._create_extension_zip_path()

        js = JS % (
            self.proxy.scheme_type,
            self.proxy_parts["ip"],
            self.proxy_parts["port"],
            self.proxy_parts["username"],
            self.proxy_parts["password"],
        )
        with zipfile.ZipFile(extension_path, "w") as extension_file:
            extension_file.writestr("manifest.json", MANIFEST)
            extension_file.writestr("background.js", js)

        self.extension_path = extension_path
        return extension_path

    def create_extension_folder(self) -> Path:
        """
        Creates a Chrome extension folder for Selenium in temp folder.
        Returns the full path to the folder.
        """
        extension_path = self._create_extension_folder_path()
        extension_path.mkdir(parents=True, exist_ok=True)

        js = JS % (
            self.proxy.scheme_type,
            self.proxy_parts["ip"],
            self.proxy_parts["port"],
            self.proxy_parts["username"],
            self.proxy_parts["password"],
        )
        (extension_path / "manifest.json").write_text(MANIFEST, encoding="utf-8")
        (extension_path / "background.js").write_text(js, encoding="utf-8")

        self.extension_path = extension_path
        return extension_path

    def delete(self) -> None:
        """
        Deletes a Chrome extension file or folder.
        Works on Windows, Linux, and macOS.
        """
        try:
            if not self.extension_path.exists():
                return

            if self.extension_path.is_file():
                self.extension_path.unlink()
            elif self.extension_path.is_dir():
                shutil.rmtree(self.extension_path)
        except:
            pass


    def _create_extension_zip_path(self) -> Path:
        """Generates a random zip file path for the extension in temp folder."""
        file_name = "".join(secrets.token_hex(8)) + ".zip"
        return self.extension_folder_path / file_name

    def _create_extension_folder_path(self) -> Path:
        """Generates a random folder path for the extension in temp folder."""
        folder_name = "".join(secrets.token_hex(8))
        return self.extension_folder_path / folder_name
