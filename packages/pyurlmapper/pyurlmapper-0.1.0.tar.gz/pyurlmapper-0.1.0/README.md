# pyurlmapper

URLMapper — lightweight library to map and proxy URLs and optionally provide a small DNS mapper for local testing.

**Features**
- `URLMapper`: simple HTTP proxy to map alias URL -> target URL (handles headers, query strings, binary bodies, streaming).
- `DNSMapper`: minimal DNS responder using `dnslib` for mapping hostnames to IPs (useful for local networks/tests).
- Ready-to-publish packaging (pyproject, setup.py, LICENSE, README).

## Install (development)

```bash
pip install -e .
# or for runtime:
pip install flask requests dnslib
```

## Quick example

```python
from urlmapper import URLMapper, DNSMapper

# DNS (optional): resolve web.servermon -> 192.168.15.9 (for clients you control)
dns = DNSMapper()
dns.add_record("web.servermon", "192.168.15.9")
dns.start_background(listen_host="0.0.0.0", port=5353)  # uses 5353 for tests (non-root)

# Proxy: forward requests from alias to real service
mapper = URLMapper()
mapper.translate_url("http://192.168.15.9:5000", "http://web.servermon:5000")
mapper.run(host="0.0.0.0", port=5000)
```

See `tests/example_usage.py` for a runnable example.

## License
MIT
