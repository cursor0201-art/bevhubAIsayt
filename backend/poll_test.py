"""Poll generation status after POST /api/ai-tasks/"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import json, time, urllib.request, urllib.error

BASE = 'http://localhost:8000'

def api(method, path, body=None, token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read())
        except Exception:
            return e.code, {}
    except Exception as ex:
        return 0, {'error': str(ex)}

# Auth
s, r = api('POST', '/api/auth/token/', {'username': 'e2e_fresh', 'password': 'Audit@12345'})
token = r.get('access')
print(f'Login: HTTP {s}')

# Create task
t0 = time.time()
s, r = api('POST', '/api/ai-tasks/', {'prompt': 'Restaurant promotion landing page'}, token=token)
elapsed = time.time() - t0
print(f'POST /api/ai-tasks/ -> HTTP {s} in {elapsed:.3f}s')

if s != 201:
    print('FAIL:', r)
    sys.exit(1)

task_id = r.get('id', '')
task_status = r.get('status', '')
print(f'task_id={task_id[:8]}... status={task_status}')

if elapsed > 1.5:
    print(f'WARNING: Response was slow ({elapsed:.2f}s), should be <1s')

# Poll for 60 seconds
for i in range(12):
    time.sleep(5)
    s2, r2 = api('GET', f'/api/ai-tasks/{task_id}/', token=token)
    st = r2.get('status', '?')
    pr = r2.get('progress', 0)
    print(f'  [{(i+1)*5:2d}s] status={st} progress={pr}%')
    if st in ('success', 'failed', 'completed', 'error'):
        print(f'FINAL: {st}')
        if r2.get('project'):
            print(f'  project_id: {r2.get("project")}')
        if r2.get('logs'):
            print(f'  last log: {str(r2.get("logs",""))[-200:]}')
        break
else:
    print('TIMEOUT: task still running after 60s')
