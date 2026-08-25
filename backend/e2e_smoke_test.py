"""
E2E Smoke Test: Full generation pipeline
POST /api/ai-tasks/ → poll → verify SUCCESS + ProjectFile
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import json, time, urllib.request, urllib.error, traceback

BASE = 'http://localhost:8000'

def api(method, path, body=None, token=None, timeout=15):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read())
        except Exception:
            return e.code, {'raw': e.read().decode()[:500]}
    except Exception as ex:
        return 0, {'error': str(ex)}

# ── 1. Auth ──────────────────────────────────────────────────────────────────
print("=== STEP 1: AUTH ===")
s, r = api('POST', '/api/auth/register/', {
    'username': 'smoke_test_user',
    'email': 'smoke@bevhub.ai',
    'password': 'SmokeTest@123',
    'password2': 'SmokeTest@123'
})
if s == 201:
    TOKEN = r.get('tokens', {}).get('access') or r.get('access')
    print(f"Registered: HTTP {s}")
else:
    s, r = api('POST', '/api/auth/token/', {'username': 'smoke_test_user', 'password': 'SmokeTest@123'})
    TOKEN = r.get('access')
    print(f"Login: HTTP {s}")

if not TOKEN:
    print("FAIL: No auth token. Aborting.")
    sys.exit(1)
print(f"Token: {TOKEN[:20]}...")

# ── 2. POST /api/ai-tasks/ ───────────────────────────────────────────────────
print("\n=== STEP 2: CREATE AI TASK ===")
t0 = time.time()
s, r = api('POST', '/api/ai-tasks/', {
    'prompt': 'Build a premium e-commerce storefront with product grid, shopping cart, and checkout flow.'
}, token=TOKEN, timeout=5)
elapsed = time.time() - t0

if s == 201:
    task_id = r.get('id')
    print(f"PASS: HTTP 201 in {elapsed:.2f}s")
    print(f"  task_id = {task_id}")
    print(f"  status  = {r.get('status')}")
    print(f"  project = {r.get('project')}")
    if elapsed > 2.0:
        print(f"  WARNING: Response took {elapsed:.2f}s (should be <1s)")
else:
    print(f"FAIL: HTTP {s} in {elapsed:.2f}s")
    if 'raw' in r:
        # Extract key error from HTML
        import re, html
        raw = r['raw']
        match = re.search(r'<title>(.*?)</title>', raw)
        if match:
            print(f"  Error: {html.unescape(match.group(1))}")
        match2 = re.search(r'OperationalError.*?\n(.*?\n){0,3}', raw)
        if match2:
            print(f"  {match2.group(0)[:500]}")
    else:
        print(f"  Response: {json.dumps(r, indent=2)[:500]}")
    sys.exit(1)

# ── 3. Poll task status ──────────────────────────────────────────────────────
print("\n=== STEP 3: POLL TASK STATUS (max 60s) ===")
final_status = None
for i in range(20):
    time.sleep(3)
    s, r = api('GET', f'/api/ai-tasks/{task_id}/', token=TOKEN)
    st = r.get('status', '?')
    pr = r.get('progress', 0)
    print(f"  [{(i+1)*3:2d}s] status={st} progress={pr}%")
    if st in ('success', 'failed', 'completed', 'error'):
        final_status = st
        break

print(f"\n=== STEP 4: VERIFY RESULT ===")
if final_status == 'success':
    proj_id = r.get('project')
    print(f"PASS: Task completed with status=success")
    print(f"  project_id = {proj_id}")
    
    # Check project files
    if proj_id:
        s2, r2 = api('GET', f'/api/projects/{proj_id}/', token=TOKEN)
        if s2 == 200:
            pages = r2.get('pages', [])
            files = r2.get('files', [])
            print(f"  Pages: {len(pages)}")
            print(f"  Files: {len(files)}")
            if pages or files:
                print("PASS: Project has generated content")
            else:
                print("WARN: Project exists but no pages/files found")
        else:
            print(f"WARN: Could not fetch project: HTTP {s2}")
else:
    if final_status is None:
        print(f"FAIL: Task still not finished after 60s (last status: {r.get('status')})")
    else:
        print(f"FAIL: Task ended with status={final_status}")
        print(f"  error: {r.get('error_message', r.get('logs', ''))[:500]}")

print("\n=== SMOKE TEST COMPLETE ===")
