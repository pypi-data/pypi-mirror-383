import random
import threading

import requests

from xproject.xlogger import get_logger


class Clash:
    def __init__(
            self,
            api_url: str = "http://127.0.0.1:9097",
            proxy_group: str = "GLOBAL",
            proxy_port: int = 7897,
            api_secret: str = "set-your-secret",
            switch_interval: int = 60,
    ):
        self.api_url = api_url.rstrip("/")
        self.proxy_group = proxy_group
        self.proxy_port = proxy_port
        self.api_secret = api_secret
        self.switch_interval = switch_interval

        self._running_event = threading.Event()
        self._thread: threading.Thread | None = None
        self.logger = get_logger()

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.api_secret}"} if self.api_secret else {}

    def _get(self, path: str) -> requests.Response:
        url = f"{self.api_url}/{path.lstrip('/')}"
        return requests.get(url, headers=self._headers(), timeout=5)

    def _put(self, path: str, data: dict) -> requests.Response:
        url = f"{self.api_url}/{path.lstrip('/')}"
        return requests.put(url, json=data, headers=self._headers(), timeout=5)

    def get_node_names(self) -> list[str]:
        response = self._get("/proxies")
        response.raise_for_status()
        jsn = response.json()
        return jsn.get("proxies", {}).get(self.proxy_group, {}).get("all", [])

    def switch_to_node(self, node_name: str) -> str | None:
        response = self._put(f"/proxies/{self.proxy_group}", {"name": node_name})
        if response.status_code == 204:
            return node_name
        return None

    def switch_to_random_node(self) -> str | None:
        node_names = self.get_node_names()
        if node_names:
            node_name = random.choice(node_names)
            node_name = self.switch_to_node(node_name)
            return node_name
        return None

    def get_current_node_name(self) -> str:
        response = self._get(f"/proxies/{self.proxy_group}")
        response.raise_for_status()
        return response.json().get("now", "")

    def get_current_ip(self) -> str:
        proxies = {
            "http": f"http://127.0.0.1:{self.proxy_port}",
            "https": f"http://127.0.0.1:{self.proxy_port}",
        }
        response = requests.get("https://ipinfo.io/ip", proxies=proxies, timeout=8)
        return response.text.strip()

    def _run_service(self) -> None:
        while self._running_event.is_set():
            try:
                self.switch_to_random_node()

                node_name = self.get_current_node_name()
                if node_name:
                    self.logger.debug(f"node_name: {node_name}")

                ip = self.get_current_ip()
                if ip:
                    self.logger.debug(f"ip: {ip}")

            except Exception as e:
                self.logger.error(f"Exception: {e}")

            if not self._running_event.wait(timeout=self.switch_interval):
                break

    def start_service(self) -> None:
        if not self._running_event.is_set():
            self._running_event.set()
            self._thread = threading.Thread(target=self._run_service, daemon=True)
            self._thread.start()
            self.logger.info("started service")

    def stop_service(self) -> None:
        if self._running_event.is_set():
            self._running_event.clear()
            self.logger.debug("send stop service signal...")

            if self._thread and self._thread.is_alive():
                self._thread.join()
                self.logger.info("stoped service")

    def listen(self) -> None:
        try:
            while self._running_event.is_set():
                threading.Event().wait(1)
        except KeyboardInterrupt:
            self.logger.warning("KeyboardInterrupt received, stopping service...")
            self.stop_service()


if __name__ == "__main__":
    clash = Clash(switch_interval=10)
    clash.start_service()
    clash.listen()
    # clash.stop_service()
