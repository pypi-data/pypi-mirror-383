# proxyutils
Easy to use proxy parser library for Python's niche proxy format.
## Install
    pip install proxyutils
## Basic usage
```python
from proxyutils import Proxy

# get requests-supported proxy dict
proxy = Proxy("1.2.3.4:8080:user:pass")
proxy.proxies #{'http': 'http://user:pass@1.2.3.4:8080', 'https': 'http://user:pass@1.2.3.4:8080'}
proxy.get_proxy_parts() #{'user': 'user', 'pass': 'pass', 'ip': '1.2.3.4', 'port': 8080}
```


## Works with all formats you need
```python
odd_formatted_proxies = [
    #ip:port
    "1.1.1.1:8080",
    
    #ip:port[delimiters@:|]user:pass
    "1.1.1.1:8080:user:pass",
    "1.1.1.1:8080@user:pass",
    "1.1.1.1:8080|user:pass",
    
    #user:pass[delimiters@:|]ip:port
    "user:pass:1.1.1.1:8080",
    
    #with different schemes
    "http://user:pass:1.1.1.1:8080",
    "https://user:pass:1.1.1.1:8080",
    "socks4://user:pass:1.1.1.1:8080",
    "socks4a://user:pass:1.1.1.1:8080",
    "socks5://user:pass:1.1.1.1:8080",
    "socks5h://user:pass:1.1.1.1:8080",

    #host instead of ip
    "user:pass:sub.my-host.com:65535",
    "anotherhost.cz:65535:user:pass",

    #requests and httpx like proxy dictionaries
    {"http": "http://1.1.1.1:80", "https": "http://1.1.1.1:80"},
    {"http://": "http://1.1.1.1:80", "https://": "http://1.1.1.1:80"},
    #unformatted
    {"http": "1.1.1.1:80", "https": "1.1.1.1:80"},

    #proxy objects itself.
    Proxy("1.1.1.1:80"),
    Proxy("1.1.1.1:80:user:pass"),
]
proxies = [Proxy(p).proxies for p in odd_formatted_proxies]
```
## Chrome proxy extension support
```python
from proxyutils import Proxy, Extension
from selenium.webdriver.chrome.options import Options

proxy = Proxy("1.1.1.1:80:user:pass")
extension = Extension(proxy)
extension = Extension("1.1.1.1:80:user:pass")
extension = Extension({"http": "http://1.1.1.1:80:user:pass", "https": "http://1.1.1.1:80:user:pass"})


#zip
ext_zip_path = extension.create_extension_zip()
chrome_options = Options()
chrome_options.add_extension(ext_zip_path)

#folder
ext_folder_path = extension.create_extension_folder()
chrome_options = Options()
chrome_options.add_argument(f"--load-extension={ext_folder_path}") #deprecated in chrome 137+

...

extension.delete()
```
Enjoying this project? Show some love with a ⭐!