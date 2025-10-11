"""Core implementation for URLMapper package.

- URLMapper: simple HTTP proxy using Flask + requests
- DNSMapper: simple DNS responder using dnslib (for local/testing only)
"""
from flask import Flask, request, Response
import requests
from urllib.parse import urlparse
import threading
import logging

# DNSMapper uses dnslib when available
try:
    from dnslib.server import DNSServer, BaseResolver
    from dnslib import RR, QTYPE, A
    _HAS_DNSLIB = True
except Exception:
    _HAS_DNSLIB = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("urlmapper")

class URLMapper:
    """Simple HTTP proxy mapper.

    Usage:
        mapper = URLMapper()
        mapper.translate_url("http://192.168.15.9:5000", "http://web.servermon:5000")
        mapper.run(host="0.0.0.0", port=5000)
    """
    def __init__(self):
        self.app = Flask(__name__)
        self.mappings = {}  # alias_base -> target_base
        self._registered = False

    def translate_url(self, source_url: str, alias_url: str):
        s = urlparse(source_url)
        a = urlparse(alias_url)
        src_base = f"{s.scheme}://{s.hostname}:{s.port or (443 if s.scheme=='https' else 80)}"
        alias_base = f"{a.scheme}://{a.hostname}:{a.port or (443 if a.scheme=='https' else 80)}"
        self.mappings[alias_base] = src_base
        logger.info(f"Mapped {alias_base} -> {src_base}")
        if not self._registered:
            self._register_routes()
            self._registered = True

    def _filter_request_headers(self, headers):
        excluded = {'host', 'content-length', 'accept-encoding', 'connection'}
        return {k: v for k, v in headers.items() if k.lower() not in excluded}

    def _filter_response_headers(self, headers):
        excluded = {'content-encoding', 'content-length', 'transfer-encoding', 'connection'}
        return [(k, v) for k, v in headers.items() if k.lower() not in excluded]

    def _build_target(self, target_base, path):
        if path:
            return f"{target_base.rstrip('/')}/{path.lstrip('/')}"
        return target_base

    def _register_routes(self):
        @self.app.route('/', defaults={'path': ''}, methods=['GET','POST','PUT','DELETE','PATCH','OPTIONS','HEAD'])
        @self.app.route('/<path:path>', methods=['GET','POST','PUT','DELETE','PATCH','OPTIONS','HEAD'])
        def proxy(path):
            host_header = request.host
            scheme = 'https' if request.is_secure else 'http'
            alias_base = f"{scheme}://{host_header}"
            target_base = self.mappings.get(alias_base)
            if not target_base:
                # try without explicit port (fallback)
                p = urlparse(alias_base)
                alias_noport = f"{p.scheme}://{p.hostname}:80"
                target_base = self.mappings.get(alias_noport)
            if not target_base:
                return Response(f"[URLMapper] No mapping for {alias_base}", status=404)

            query = request.query_string.decode()
            target_url = self._build_target(target_base, path)
            if query:
                target_url = f"{target_url}?{query}"

            method = request.method
            headers = self._filter_request_headers(dict(request.headers))
            parsed_target = urlparse(target_base)
            headers['Host'] = parsed_target.hostname

            data = request.get_data() or None
            try:
                resp = requests.request(method,
                                        target_url,
                                        headers=headers,
                                        data=data,
                                        cookies=request.cookies,
                                        allow_redirects=False,
                                        stream=True,
                                        timeout=(5, 30))
            except requests.RequestException as e:
                return Response(f"[URLMapper] Error contacting upstream: {e}", status=502)

            response_headers = self._filter_response_headers(resp.headers)

            def generate():
                try:
                    for chunk in resp.iter_content(chunk_size=4096):
                        if chunk:
                            yield chunk
                finally:
                    resp.close()

            return Response(generate(), status=resp.status_code, headers=response_headers)

    def run(self, host="0.0.0.0", port=80, threaded=True):
        if not self.mappings:
            logger.warning("No mappings configured.")
            return
        logger.info("Mappings:")
        for a, t in self.mappings.items():
            logger.info(f"  {a} -> {t}")
        self.app.run(host=host, port=port, threaded=threaded)

    def start_background(self, host="0.0.0.0", port=80):
        thr = threading.Thread(target=self.run, args=(host, port), daemon=True)
        thr.start()
        logger.info(f"Proxy background thread started on {host}:{port}")

if _HAS_DNSLIB:
    class _DictResolver(BaseResolver):
        def __init__(self, records):
            self.records = records

        def resolve(self, request, handler):
            reply = request.reply()
            qname = str(request.q.qname).rstrip('.')
            qtype = QTYPE[request.q.qtype]
            if qtype == 'A' and qname in self.records:
                ip = self.records[qname]
                reply.add_answer(RR(qname, QTYPE.A, rdata=A(ip), ttl=60))
            return reply

    class DNSMapper:
        """Simple DNS responder for local testing. Requires dnslib."""
        def __init__(self):
            self.records = {}
            self.server = None

        def add_record(self, name, ip):
            self.records[name] = ip

        def start(self, listen_host='0.0.0.0', port=53):
            resolver = _DictResolver(self.records)
            self.server = DNSServer(resolver, address=listen_host, port=port)
            self.server.start_thread()
            logger.info(f"DNSMapper started on {listen_host}:{port} with {len(self.records)} records")

        def start_background(self, listen_host='0.0.0.0', port=53):
            # convenience wrapper
            thr = threading.Thread(target=self.start, args=(listen_host, port), daemon=True)
            thr.start()
            logger.info(f"DNSMapper background thread requested on {listen_host}:{port}")

        def stop(self):
            if self.server:
                try:
                    self.server.stop()
                except Exception:
                    pass
else:
    class DNSMapper:
        def __init__(self):
            raise RuntimeError("dnslib is required for DNSMapper. Install dnslib to enable this feature.")
