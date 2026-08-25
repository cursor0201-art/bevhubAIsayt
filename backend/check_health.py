import urllib.request
import urllib.error
import json

try:
    r = urllib.request.urlopen('http://localhost:8000/health/', timeout=3)
    print(f'/health/ -> HTTP {r.status}: {r.read()[:200]}')
except urllib.error.HTTPError as e:
    print(f'/health/ -> HTTP {e.code}')
except Exception as e:
    print(f'/health/ NOT FOUND: {e}')

try:
    r2 = urllib.request.urlopen('http://localhost:8000/api/auth/token/', timeout=3)
except urllib.error.HTTPError as e:
    print(f'/api/auth/token/ -> HTTP {e.code} (expected 405 or 400)')
except Exception as e:
    print(f'/api/ NOT reachable: {e}')
