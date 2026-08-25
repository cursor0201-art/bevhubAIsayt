import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import urllib.request, json

BASE = 'http://localhost:8000'

def api(method, path, body=None, token=None):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    headers = {'Content-Type': 'application/json'}
    if token: headers['Authorization'] = 'Bearer ' + token
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try: return e.code, json.loads(e.read())
        except: return e.code, {'error': str(e)}
    except Exception as ex:
        return 0, {'error': str(ex)}

print("=== REGISTERING FRESH USER ===")
s, r = api('POST', '/api/auth/register/', {
    'username': 'e2e_fresh',
    'email': 'e2e_fresh@bevhub.ai',
    'password': 'Audit@12345',
    'password2': 'Audit@12345'
})
print(f'Register: HTTP {s}')
if s != 201:
    # try login
    s, r = api('POST', '/api/auth/token/', {'username': 'e2e_fresh', 'password': 'Audit@12345'})
    print(f'Login fallback: HTTP {s}')
TOKEN = r.get('tokens', {}).get('access') or r.get('access')
print(f'Token: {str(TOKEN)[:30]}...' if TOKEN else 'NO TOKEN')

print("\n=== TEST 1: EMPTY PROMPT VALIDATION ===")
s, r = api('POST', '/api/ai-tasks/', {'prompt': '   ', 'workspace_id': None}, token=TOKEN)
print(f'HTTP {s}: {r}')
if s == 400:
    print("PASS: Validation returns 400")
elif s == 404:
    print("FAIL: Still 404 - URL not fixed yet")
else:
    print(f"UNEXPECTED: {s}")

print("\n=== TEST 2: VALID AI TASK CREATE ===")
s, r = api('POST', '/api/ai-tasks/', {'prompt': 'Build a minimal landing page for a SaaS tool'}, token=TOKEN)
print(f'HTTP {s}: status={r.get("status")}, id={str(r.get("id",""))[:8]}')
if s == 201:
    print("PASS: Task created and queued")
else:
    print(f"FAIL: {r}")

print("\n=== TEST 3: PROMO CODE BEVHUB2026 ===")
s, r = api('POST', '/api/billing/promo/', {'code': 'BEVHUB2026'}, token=TOKEN)
print(f'HTTP {s}: {r}')
if s == 200:
    print("PASS: Promo code accepted")
else:
    print(f"FAIL/WARN: {r}")

print("\n=== TEST 4: BILLING DASHBOARD ===")
s, r = api('GET', '/api/billing/dashboard/', token=TOKEN)
if s == 200:
    print(f"PASS: Balance={r.get('balance')}, Plan={r.get('subscription',{}).get('plan_name')}, Transactions={len(r.get('transactions',[]))}")
else:
    print(f"FAIL: HTTP {s}: {r}")

print("\nALL SPOT CHECKS COMPLETE")
