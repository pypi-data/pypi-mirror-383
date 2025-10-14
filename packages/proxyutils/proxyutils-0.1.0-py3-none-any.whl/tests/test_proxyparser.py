from proxyutils import Proxy, Extension
import unittest


class TestProxy(unittest.TestCase):
    
    def test_unauth_ip(self):
        proxy = Proxy("1.1.1.1:80")
        parts = proxy.get_proxy_parts()
        self.assertEqual(proxy.is_authenticated, False)
        self.assertEqual(proxy.proxy_root, "http://1.1.1.1:80")
        self.assertEqual(parts["ip"], "1.1.1.1")
        self.assertEqual(parts["port"], 80)
        self.assertEqual(parts.get("username"), None)
        self.assertEqual(parts.get("password"), None)


    def test_auth_ip(self):
        proxy = Proxy("1.1.1.1:80:user:password")
        parts = proxy.get_proxy_parts()
        self.assertEqual(proxy.is_authenticated, True)
        self.assertEqual(proxy.proxy_root, "http://user:password@1.1.1.1:80")
        self.assertEqual(parts["ip"], "1.1.1.1")
        self.assertEqual(parts["port"], 80)
        self.assertEqual(parts["username"], "user")
        self.assertEqual(parts["password"], "password")


    def test_auth_order(self):
        proxy_strings = [
            "1.1.1.1:80:user:password",
            "user:password:1.1.1.1:80",
        ]
        for proxy_string in proxy_strings:
            proxy = Proxy(proxy_string)
            self.assertEqual(proxy.is_authenticated, True)
            self.assertEqual(proxy.proxy_root, "http://user:password@1.1.1.1:80")


    def test_auth_delimiter(self):
        proxy_strings = [
            "1.1.1.1:80|user:password",
            "1.1.1.1:80@user:password",
            "1.1.1.1:80:user:password",
            "user:password:1.1.1.1:80",
            "user:password|1.1.1.1:80",
            "user:password@1.1.1.1:80",
        ]
        for proxy_string in proxy_strings:
            proxy = Proxy(proxy_string)
            self.assertEqual(proxy.is_authenticated, True)
            self.assertEqual(proxy.proxy_root, "http://user:password@1.1.1.1:80")

    
    def test_domain(self):
        proxy_strings = [
            "my.fast-proxy.host.cz:80",
            "my.fast-proxy.host.cz:80",
            "my.fast-proxy.host.cz:80:user:80pass",
            "my.fast-proxy.host.cz:80:user:80pass",
        ]
        for proxy_string in proxy_strings:
            proxy = Proxy(proxy_string)
            parts = proxy.get_proxy_parts()
            self.assertEqual(parts["ip"], "my.fast-proxy.host.cz")


    def test_extension_creation_and_cleanup(self):
        proxy = Proxy("user:pass@1.2.3.4:8080")
        extension = Extension(proxy)

        zip_path = extension.create_extension_zip()
        self.assertTrue(zip_path.exists())
        self.assertEqual(zip_path.suffix, ".zip")
        extension.delete()
        self.assertFalse(zip_path.exists())

        folder_path = extension.create_extension_folder()
        self.assertTrue(folder_path.exists())
        self.assertTrue(folder_path.is_dir())
        self.assertTrue((folder_path / "manifest.json").exists())
        self.assertTrue((folder_path / "background.js").exists())
        extension.delete()
        self.assertFalse(folder_path.exists())


    def test_scheme(self):
        proxy = Proxy("1.1.1.1:80:user:password")
        self.assertIn("http://", proxy.proxy_root)

        proxy = Proxy("1.1.1.1:80:user:password", scheme="https://")
        self.assertIn("https://", proxy.proxy_root)

        proxy = Proxy("1.1.1.1:80:user:password", scheme="socks5://")
        self.assertIn("socks5://", proxy.proxy_root)

        proxy = Proxy("1.1.1.1:80:user:password", scheme="socks5h://")
        self.assertIn("socks5h://", proxy.proxy_root)

        proxy = Proxy("1.1.1.1:80:user:password", scheme="socks4://")
        self.assertIn("socks4://", proxy.proxy_root)

        proxy = Proxy("1.1.1.1:80:user:password", scheme="socks4a://")
        self.assertIn("socks4a://", proxy.proxy_root)

        proxy = Proxy("socks5://1.1.1.1:80:user:password")
        self.assertIn("socks5://", proxy.proxy_root)

        proxy = Proxy("socks4://1.1.1.1:80:user:password")
        self.assertIn("socks4://", proxy.proxy_root)


if __name__ == "__main__":
    unittest.main()