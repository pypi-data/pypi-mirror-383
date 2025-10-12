import requests
import ipaddress
import logging
import sys
from threading import Timer
from flask import request, abort, current_app

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("cloudflare_access.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

class CloudflareFilter:
    CLOUDFLARE_IP_LIST_URL = "https://api.cloudflare.com/client/v4/ips"
    
    def __init__(self, app=None, update_interval=86400):
        self.cloudflare_networks = []
        self.update_interval = update_interval
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask uygulaması ile entegrasyonu sağlar."""
        app.before_request(self.check_ip)
        
        if not self.fetch_cloudflare_ips():
            logging.critical("Failed to load initial Cloudflare IP list. Application cannot start securely.")
            sys.exit(1)
        self._schedule_next_update()
        logging.info(f"Cloudflare IP list will be updated every {self.update_interval} seconds.")

    def fetch_cloudflare_ips(self):
        """Cloudflare IP aralıklarını indirir ve belleğe yükler."""
        logging.info("Attempting to fetch Cloudflare IP ranges...")
        try:
            response = requests.get(self.CLOUDFLARE_IP_LIST_URL, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("success"):
                ipv4_cidrs = data["result"].get("ipv4_cidrs", [])
                ipv6_cidrs = data["result"].get("ipv6_cidrs", [])
                all_cidrs = ipv4_cidrs + ipv6_cidrs
                new_networks = [ipaddress.ip_network(cidr) for cidr in all_cidrs]
                self.cloudflare_networks = new_networks
                
                logging.info(
                    f"Cloudflare IP ranges loaded successfully. "
                    f"({len(ipv4_cidrs)} IPv4, {len(ipv6_cidrs)} IPv6 networks)"
                )
                return True
            else:
                logging.error("Failed to retrieve Cloudflare IP list (API returned unsuccessful response).")
                return False

        except requests.exceptions.RequestException as e:
            logging.exception(f"Network error while fetching Cloudflare IPs: {e}")
            return False
        except Exception as e:
            logging.exception(f"An unexpected error occurred while fetching Cloudflare IPs: {e}")
            return False

    def _schedule_next_update(self):
        """Bir sonraki IP listesi güncellemesini zamanlar."""
        timer = Timer(self.update_interval, self._update_task)
        timer.daemon = True
        timer.start()

    def _update_task(self):
        """Periyodik güncelleme görevini çalıştırır."""
        self.fetch_cloudflare_ips()
        self._schedule_next_update()

    def is_cloudflare_ip(self, remote_addr):
        """Verilen IP'nin bir Cloudflare IP'si olup olmadığını kontrol eder."""
        if not self.cloudflare_networks:
            logging.warning("Cloudflare IP list is empty. Denying request for safety.")
            return False
        try:
            ip = ipaddress.ip_address(remote_addr)
            return any(ip in net for net in self.cloudflare_networks)
        except ValueError:
            logging.warning(f"Invalid IP address received: {remote_addr}")
            return False

    def get_real_ip(self):
        """Gerçek ziyaretçi IP'sini CF-Connecting-IP veya X-Forwarded-For başlığından alır."""
        if "CF-Connecting-IP" in request.headers:
            return request.headers["CF-Connecting-IP"]
        if "X-Forwarded-For" in request.headers:
            return request.headers.get("X-Forwarded-For").split(',')[0].strip()
        return request.remote_addr

    def check_ip(self, log=True):
        """Gelen isteği kontrol eder ve Cloudflare dışından geliyorsa engeller."""
        request_ip = request.remote_addr
        
        if self.is_cloudflare_ip(request_ip):
            if log:
                real_ip = self.get_real_ip()
                logging.info(f"✅ Allowed access from Cloudflare proxy {request_ip}. Real IP: {real_ip}")
        else:
            if log:
                logging.warning(f"❌ Blocked direct access from non-Cloudflare IP: {request_ip}")
            abort(403)