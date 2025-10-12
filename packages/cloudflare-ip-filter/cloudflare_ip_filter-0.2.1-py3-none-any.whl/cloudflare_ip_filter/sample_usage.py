from flask import Flask
from cloudflare_ip_filter import CloudflareFilter

app = Flask(__name__)

cf_filter = CloudflareFilter(app)

@app.route('/')
def index():
    real_ip = cf_filter.get_real_ip()
    return f"This page is protected. Your real IP is {real_ip}"

if __name__ == '__main__':
    app.run()