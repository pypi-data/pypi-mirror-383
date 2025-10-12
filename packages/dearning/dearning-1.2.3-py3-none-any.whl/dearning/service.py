# dearning/serving.py
import http.server , http.client, socketserver ,ssl ,json ,os
import sys ,base64 ,mmap ,threading ,asyncio, subprocess
from pathlib import Path

# ============ KONFIGURASI DASAR ============
MODEL_DIR = Path(os.environ.get("DEARNING_MODEL_DIR", "dm_models"))
MODEL_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_PASSWORD = os.environ.get("DEARNING_PASSWORD", "dearning_secure")
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = int(os.environ.get("DEARNING_PORT", "8443"))

# ============ GENERATOR SERTIFIKAT ============
def _auto_generate_cert(cert_dir: Path):
    """Buat sertifikat self-signed jika belum ada"""
    cert_path = cert_dir / "server.crt"
    key_path = cert_dir / "server.key"
    if cert_path.exists() and key_path.exists():
        return cert_path, key_path

    cert_dir.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run([
            "openssl", "req", "-x509", "-nodes", "-days", "365",
            "-newkey", "rsa:2048",
            "-keyout", str(key_path),
            "-out", str(cert_path),
            "-subj", "/CN=localhost"
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"[dearning] Sertifikat dibuat di {cert_dir}")
    except Exception:
        # fallback: buat dummy file agar tetap bisa jalan (tidak aman)
        cert_path.write_text("-----BEGIN CERTIFICATE-----\nMIIDfakecert==\n-----END CERTIFICATE-----")
        key_path.write_text("-----BEGIN PRIVATE KEY-----\nfakekey==\n-----END PRIVATE KEY-----")
        print(f"[dearning] Sertifikat dummy dibuat di {cert_dir}")
    return cert_path, key_path

# ============ CACHE MODEL ============
_MAX_CACHE_BYTES = 2 * 1024 * 1024
_model_cache = {}

# ============ FUNGSI DOMM BACKGROUND ============
async def domm_background_task(interval=5.0):
    while True:
        try:
            if len(_model_cache) > 50:
                _model_cache.clear()
        except Exception:
            pass
        await asyncio.sleep(interval)

def start_domm_background_loop():
    def _run_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(domm_background_task())
        loop.run_forever()
    t = threading.Thread(target=_run_loop, daemon=True)
    t.start()

# ============ HANDLER SERVER ============
class DearningHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "DearningServer/1.0"

    def _read_json(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            if length <= 0:
                return None
            raw = self.rfile.read(length)
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return None

    def _send_json(self, code, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        data = self._read_json()
        if not data:
            return self._send_json(400, {"error": "invalid json"})
        password = data.get("password")
        if password != getattr(self.server, "cloud_password", DEFAULT_PASSWORD):
            return self._send_json(403, {"error": "invalid password"})
        if self.path == "/import_model":
            return self._handle_import_model(data)
        elif self.path == "/load_model":
            return self._handle_load_model(data)
        return self._send_json(404, {"error": "unknown endpoint"})

    def _handle_import_model(self, data):
        fname = data.get("filename")
        content_b64 = data.get("content_b64")
        if not fname or not content_b64:
            return self._send_json(400, {"error": "missing filename or content"})

        # terima .dm dan .py
        safe_name = os.path.basename(fname)
        path = MODEL_DIR / safe_name
        try:
            raw = base64.b64decode(content_b64)
        except Exception:
            return self._send_json(400, {"error": "invalid base64 content"})
        tmp = path.with_suffix(".tmp")
        with open(tmp, "wb") as fh:
            fh.write(raw)
        os.replace(tmp, path)
        if path.stat().st_size <= _MAX_CACHE_BYTES:
            _model_cache[safe_name] = raw

        return self._send_json(200, {"status": "imported", "model": safe_name, "size": path.stat().st_size})

    def _handle_load_model(self, data):
        fname = data.get("filename")
        if not fname:
            return self._send_json(400, {"error": "missing filename"})
        safe_name = os.path.basename(fname)
        path = MODEL_DIR / safe_name
        if not path.exists():
            return self._send_json(404, {"error": "not found"})
        if safe_name in _model_cache:
            content = _model_cache[safe_name]
        else:
            with open(path, "rb") as fh:
                content = fh.read()
                if len(content) <= _MAX_CACHE_BYTES:
                    _model_cache[safe_name] = content
        b64 = base64.b64encode(content).decode("ascii")
        return self._send_json(200, {"status": "ok", "filename": safe_name, "content_b64": b64})

    def log_message(self, *a):  # non-verbose
        return

# ============ RUN SERVER ============
class ThreadedHTTPSServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

def run_server(host=DEFAULT_HOST, port=DEFAULT_PORT, password=DEFAULT_PASSWORD, sslc=True):
    """Jalankan server cloud Dearning"""
    httpd = ThreadedHTTPSServer((host, port), DearningHandler)
    httpd.cloud_password = password
    if sslc:
        # Buat sertifikat otomatis
        cert_dir = MODEL_DIR / "certificates"
        cert, key = _auto_generate_cert(cert_dir)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=cert, keyfile=key)
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        print(f"[dearning] HTTPS cloud aktif di https://{host}:{port}")
    else:
        print(f"[dearning] HTTP cloud aktif di http://{host}:{port}")
    start_domm_background_loop()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down...")

# ------------ koneksi client ------------
def _make_conn(host, port, use_ssl=True, timeout=30):
    if use_ssl:
        context = ssl._create_unverified_context()
        return http.client.HTTPSConnection(host, port, context=context, timeout=timeout)
    else:
        return http.client.HTTPConnection(host, port, timeout=timeout)

def post(host, port, model_path, password=DEFAULT_PASSWORD, sslc=True, timeout=60):
    if not os.path.exists(model_path):
        raise FileNotFoundError(model_path)
    model_name = os.path.basename(model_path)
    with open(model_path, "rb") as fh:
        model_bytes = fh.read()
    b64 = base64.b64encode(model_bytes).decode("ascii")
    payload = {"password": password, "filename": model_name, "content_b64": b64}
    body = json.dumps(payload).encode("utf-8")
    conn = _make_conn(host, port, sslc, timeout)
    try:
        conn.request("POST", "/import_model", body=body, headers={
            "Content-Type": "application/json",
            "Content-Length": str(len(body))
        })
        r = conn.getresponse()
        return json.loads(r.read().decode())
    finally:
        conn.close()

def load(host, port, filename, password=DEFAULT_PASSWORD, sslc=True, timeout=60):
    payload = {"password": password, "filename": os.path.basename(filename)}
    body = json.dumps(payload).encode("utf-8")
    conn = _make_conn(host, port, sslc, timeout)
    try:
        conn.request("POST", "/load_model", body=body, headers={
            "Content-Type": "application/json",
            "Content-Length": str(len(body))
        })
        r = conn.getresponse()
        data = r.read().decode()
        j = json.loads(data)
        if "content_b64" in j:
            return base64.b64decode(j["content_b64"])
        return j
    finally:
        conn.close()

# ------------ Async wrappers ------------
async def async_post(*args, **kwargs):
    return await asyncio.to_thread(post, *args, **kwargs)
async def async_load(*args, **kwargs):
    return await asyncio.to_thread(load, *args, **kwargs)
