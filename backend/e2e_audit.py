"""
BevHub AI - Full E2E Backend Audit Script
Covers all 23 verification scenarios.
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import urllib.request
import json
import sys
import time

BASE = 'http://localhost:8000'
RESULTS = []

def api(method, path, body=None, token=None, timeout=30):
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
        except:
            return e.code, {'error': str(e)}
    except Exception as ex:
        return 0, {'error': str(ex)}

def log(step, status, detail):
    icon = '✅' if status == 'PASS' else ('❌' if status == 'FAIL' else '⚠️')
    msg = f"{icon} [{step}] {status}: {detail}"
    print(msg)
    RESULTS.append({'step': step, 'status': status, 'detail': detail})

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

# ─── STEP 1: REGISTER ────────────────────────────────────────
section("STEP 1: Register New User")
s, r = api('POST', '/api/auth/register/', {
    'username': 'e2e_tester',
    'email': 'e2e_tester@bevhub.ai',
    'password': 'Audit@12345',
    'password2': 'Audit@12345'
})
if s == 201 and 'tokens' in r:
    TOKEN = r['tokens']['access']
    log('REGISTER', 'PASS', f"User created, JWT issued. Role: {r['user']['role']}")
elif s in (400,) and 'username' in str(r):
    # User already exists — try login
    log('REGISTER', 'WARN', f"User may already exist (HTTP {s}): {r}")
    TOKEN = None
else:
    log('REGISTER', 'FAIL', f"HTTP {s}: {r}")
    TOKEN = None

# ─── STEP 2: LOGIN ───────────────────────────────────────────
section("STEP 2: Login")
s, r = api('POST', '/api/auth/token/', {
    'username': 'e2e_tester',
    'password': 'Audit@12345'
})
if s == 200 and 'access' in r:
    TOKEN = r['access']
    log('LOGIN', 'PASS', f"JWT access token issued. Token[:40]: {TOKEN[:40]}...")
else:
    log('LOGIN', 'FAIL', f"HTTP {s}: {r}")
    sys.exit(1)

# ─── STEP 3: GET USER PROFILE ───────────────────────────────
section("STEP 3: User Profile")
s, r = api('GET', '/api/auth/me/', token=TOKEN)
if s == 200:
    log('PROFILE', 'PASS', f"User: {r.get('username')}, Email: {r.get('email')}, Tenant: {r.get('tenant_id')}")
else:
    log('PROFILE', 'FAIL', f"HTTP {s}: {r}")

# ─── STEP 4: CHECK WORKSPACES ────────────────────────────────
section("STEP 4: Workspaces")
s, r = api('GET', '/api/workspaces/', token=TOKEN)
WORKSPACE_ID = None
if s == 200:
    if len(r) == 0:
        # Create workspace
        s2, r2 = api('POST', '/api/workspaces/', {'name': 'E2E Test Workspace'}, token=TOKEN)
        if s2 == 201:
            WORKSPACE_ID = r2['id']
            log('WORKSPACE', 'PASS', f"Created workspace: {r2['name']} (id: {WORKSPACE_ID[:8]}...)")
        else:
            log('WORKSPACE', 'FAIL', f"Create failed HTTP {s2}: {r2}")
    else:
        WORKSPACE_ID = r[0]['id']
        log('WORKSPACE', 'PASS', f"Found {len(r)} workspace(s). Using: {r[0]['name']} (id: {WORKSPACE_ID[:8]}...)")
else:
    log('WORKSPACE', 'FAIL', f"HTTP {s}: {r}")

# ─── STEP 5: CHECK BILLING DASHBOARD ────────────────────────
section("STEP 5: Billing Dashboard & Credits")
s, r = api('GET', '/api/billing/dashboard/', token=TOKEN)
if s == 200:
    bal = r.get('balance', 'N/A')
    sub = r.get('subscription', {})
    plans = r.get('plans', [])
    log('BILLING_DASHBOARD', 'PASS', f"Balance: {bal} credits. Subscription: {sub.get('plan_name','N/A')} ({sub.get('status','N/A')}). Plans available: {len(plans)}")
    BALANCE_BEFORE = float(bal) if bal != 'N/A' else 0
else:
    log('BILLING_DASHBOARD', 'FAIL', f"HTTP {s}: {r}")
    BALANCE_BEFORE = 0

# ─── STEP 6: TEMPLATES ───────────────────────────────────────
section("STEP 6: Templates List")
s, r = api('GET', '/api/templates/', token=TOKEN)
if s == 200 and isinstance(r, list):
    log('TEMPLATES', 'PASS', f"Got {len(r)} templates. Categories: {set(t['category'] for t in r)}")
    TEMPLATE_PROMPT = r[0]['prompt'] if r else "Build a modern SaaS platform"
else:
    log('TEMPLATES', 'FAIL', f"HTTP {s}: {r}")
    TEMPLATE_PROMPT = "Build a modern SaaS landing page for TaskFlow"

# ─── STEP 7: INTEGRATIONS ────────────────────────────────────
section("STEP 7: Integrations List")
s, r = api('GET', '/api/integrations/', token=TOKEN)
if s == 200 and isinstance(r, list):
    connected = [i for i in r if i.get('is_connected')]
    log('INTEGRATIONS_LIST', 'PASS', f"Got {len(r)} integrations. Connected: {len(connected)}")
else:
    log('INTEGRATIONS_LIST', 'FAIL', f"HTTP {s}: {r}")

# ─── STEP 8: CONNECT INTEGRATION ─────────────────────────────
section("STEP 8: Connect GitHub Integration")
s, r = api('POST', '/api/integrations/github/connect/', {'config': {'api_key': 'ghp_test_e2e_key_12345'}}, token=TOKEN)
if s == 200 and r.get('is_connected'):
    log('INTEGRATIONS_CONNECT', 'PASS', f"GitHub connected: {r.get('message')}")
else:
    log('INTEGRATIONS_CONNECT', 'FAIL', f"HTTP {s}: {r}")

# ─── STEP 9: HISTORY (before generation) ────────────────────
section("STEP 9: History (pre-generation)")
s, r = api('GET', '/api/analytics/history/', token=TOKEN)
if s == 200:
    log('HISTORY_PRE', 'PASS', f"Got {len(r)} history events")
else:
    log('HISTORY_PRE', 'FAIL', f"HTTP {s}: {r}")

# ─── STEP 10: CREATE AI TASK (non-blocking) ──────────────────
section("STEP 10: Create AI Generation Task")
TASK_ID = None
PROJECT_ID = None
s, r = api('POST', '/api/ai-tasks/', {
    'prompt': 'Build a minimal dark-mode landing page for a SaaS analytics tool called MetricFlow. Include hero, features, and pricing sections.',
    'workspace_id': WORKSPACE_ID
}, token=TOKEN)
if s == 201 and 'id' in r:
    TASK_ID = r['id']
    log('AI_TASK_CREATE', 'PASS', f"Task queued. ID: {TASK_ID[:8]}... Status: {r.get('status')}")
else:
    log('AI_TASK_CREATE', 'FAIL', f"HTTP {s}: {r}")

# ─── STEP 11: POLL TASK PROGRESS ────────────────────────────
section("STEP 11: Poll AI Task Progress")
if TASK_ID:
    max_wait = 180  # 3 minutes
    elapsed = 0
    poll_interval = 8
    final_status = None
    last_stage = None
    while elapsed < max_wait:
        time.sleep(poll_interval)
        elapsed += poll_interval
        s, r = api('GET', f'/api/ai-tasks/{TASK_ID}/progress/', token=TOKEN)
        if s == 200:
            pct = r.get('progress_percent', 0)
            stage = r.get('current_stage', '?')
            status = r.get('status', '?')
            last_log = r.get('last_log', '')[:80]
            if stage != last_stage:
                print(f"  [{elapsed:3d}s] {pct}% | Stage: {stage} | {last_log}")
                last_stage = stage
            if status in ('completed', 'failed'):
                final_status = status
                cost = r.get('total_cost', 0)
                log('AI_TASK_POLL', 'PASS' if status=='completed' else 'FAIL', 
                    f"Finished in {elapsed}s. Status: {status}. Total cost: ${cost:.4f}. Stage: {stage}")
                break
        else:
            log('AI_TASK_POLL', 'FAIL', f"Progress poll failed HTTP {s}: {r}")
            break
    
    if not final_status:
        log('AI_TASK_POLL', 'FAIL', f"Timeout after {max_wait}s — task still running")
    
    # Get project from task
    s, r = api('GET', f'/api/ai-tasks/{TASK_ID}/', token=TOKEN)
    if s == 200 and r.get('project'):
        PROJECT_ID = r['project']
        log('AI_TASK_GET_PROJECT', 'PASS', f"Project ID from task: {str(PROJECT_ID)[:8]}...")
    else:
        log('AI_TASK_GET_PROJECT', 'FAIL', f"No project in task. HTTP {s}: {r}")

# ─── STEP 12: GET PROJECT DETAILS ────────────────────────────
section("STEP 12: Project Details & Files")
if PROJECT_ID:
    s, r = api('GET', f'/api/projects/{PROJECT_ID}/', token=TOKEN)
    if s == 200:
        files = r.get('files', [])
        pages = r.get('pages', [])
        deploys = r.get('deployments', [])
        log('PROJECT_DETAIL', 'PASS', 
            f"Project: '{r['project_name']}'. Files: {len(files)}, Pages: {len(pages)}, Deployments: {len(deploys)}")
        print(f"  Files: {[f['path'] for f in files[:10]]}")
        print(f"  Pages: {[p['slug'] for p in pages]}")
    else:
        log('PROJECT_DETAIL', 'FAIL', f"HTTP {s}: {r}")
else:
    log('PROJECT_DETAIL', 'FAIL', "No PROJECT_ID available from task")

# ─── STEP 13: DEPLOYED PAGE ACCESSIBLE ──────────────────────
section("STEP 13: Public URL Access (no auth)")
if PROJECT_ID:
    s, r = api('GET', f'/api/projects/{PROJECT_ID}/', token=TOKEN)
    if s == 200:
        deploys = r.get('deployments', [])
        if deploys:
            deploy_url = deploys[-1].get('deploy_url', '')
            if deploy_url:
                # Try accessing the deployed page
                try:
                    req = urllib.request.Request(deploy_url)
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        content = resp.read()[:200].decode('utf-8', errors='replace')
                        log('PUBLIC_URL', 'PASS', f"Public URL accessible! URL: {deploy_url}. Preview: {content[:100]}")
                except Exception as ex:
                    log('PUBLIC_URL', 'FAIL', f"URL: {deploy_url}. Error: {ex}")
            else:
                log('PUBLIC_URL', 'FAIL', "Deploy URL is empty")
        else:
            log('PUBLIC_URL', 'FAIL', "No deployments on project")

# ─── STEP 14: AI EDIT ────────────────────────────────────────
section("STEP 14: AI Edit (Brain Assistant)")
if PROJECT_ID:
    s, r = api('POST', f'/api/projects/{PROJECT_ID}/ai-edit/', {
        'prompt': 'Change the hero section background to a deep violet gradient #4c1d95 to #7c3aed',
        'filepath': 'src/pages/index.html'
    }, token=TOKEN)
    if s == 200:
        log('AI_EDIT', 'PASS', f"AI edit applied. Project name: {r.get('project_name')}. Files: {len(r.get('files',[]))}")
    else:
        log('AI_EDIT', 'FAIL', f"HTTP {s}: {r}")

# ─── STEP 15: DEPLOY PROJECT ─────────────────────────────────
section("STEP 15: Deploy Project")
if PROJECT_ID:
    s, r = api('POST', f'/api/projects/{PROJECT_ID}/deploy/', {}, token=TOKEN, timeout=60)
    if s == 200:
        deploys = r.get('deployments', [])
        deploy_url = deploys[-1].get('deploy_url','') if deploys else ''
        log('DEPLOY', 'PASS', f"Deployed! URL: {deploy_url}")
    else:
        log('DEPLOY', 'FAIL', f"HTTP {s}: {r}")

# ─── STEP 16: DEPLOYMENTS MODULE ─────────────────────────────
section("STEP 16: Deployments Module")
s, r = api('GET', '/api/deployments/', token=TOKEN)
if s == 200:
    log('DEPLOYMENTS_MODULE', 'PASS', f"Got {len(r)} deployments. Statuses: {set(d['status'] for d in r)}")
    if r:
        latest = r[0]
        print(f"  Latest: {latest.get('status')} | URL: {latest.get('deploy_url', 'N/A')}")
        # Check logs
        if latest.get('logs'):
            print(f"  Logs preview: {str(latest.get('logs',''))[:120]}")
else:
    log('DEPLOYMENTS_MODULE', 'FAIL', f"HTTP {s}: {r}")

# ─── STEP 17: HISTORY (after generation + deploy) ───────────
section("STEP 17: History (post-generation)")
s, r = api('GET', '/api/analytics/history/', token=TOKEN)
if s == 200:
    event_types = [e['event'] for e in r[:20]]
    log('HISTORY_POST', 'PASS', f"Got {len(r)} events. Recent: {event_types[:8]}")
else:
    log('HISTORY_POST', 'FAIL', f"HTTP {s}: {r}")

# ─── STEP 18: CREDIT DEDUCTION ───────────────────────────────
section("STEP 18: Credit Deduction Check")
s, r = api('GET', '/api/billing/dashboard/', token=TOKEN)
if s == 200:
    bal_after = float(r.get('balance', 0))
    deducted = BALANCE_BEFORE - bal_after
    if deducted > 0:
        log('CREDIT_DEDUCTION', 'PASS', f"Credits deducted! Before: {BALANCE_BEFORE:.2f} → After: {bal_after:.2f} (Used: {deducted:.4f})")
    else:
        log('CREDIT_DEDUCTION', 'WARN', f"No deduction detected. Before: {BALANCE_BEFORE:.2f}, After: {bal_after:.2f}. Check if orchestrator ran via Celery.")
else:
    log('CREDIT_DEDUCTION', 'FAIL', f"HTTP {s}: {r}")

# ─── STEP 19: PROMO CODE ─────────────────────────────────────
section("STEP 19: Promo Code")
s, r = api('POST', '/api/billing/promo/', {'code': 'BEVHUB2026'}, token=TOKEN)
if s == 200:
    log('PROMO_CODE', 'PASS', f"Promo applied: {r.get('message')}. New balance: {r.get('balance')}")
elif s == 400:
    log('PROMO_CODE', 'WARN', f"Promo not found (expected if no seed): {r}")
else:
    log('PROMO_CODE', 'FAIL', f"HTTP {s}: {r}")

# ─── STEP 20: PLAN SUBSCRIPTION ──────────────────────────────
section("STEP 20: Plan Subscription")
s, r = api('POST', '/api/billing/subscribe/', {'plan_slug': 'growth', 'billing_cycle': 'monthly'}, token=TOKEN)
if s == 200:
    log('BILLING_SUBSCRIBE', 'PASS', f"Subscribed: {r.get('plan_name')} - {r.get('status')}")
elif s == 404:
    log('BILLING_SUBSCRIBE', 'WARN', f"Plan 'growth' not found in DB. Run seed. HTTP {s}: {r}")
else:
    log('BILLING_SUBSCRIBE', 'FAIL', f"HTTP {s}: {r}")

# ─── STEP 21: SETTINGS - UPDATE PROFILE ──────────────────────
section("STEP 21: Settings - Update Profile")
s, r = api('PATCH', '/api/auth/me/', {'username': 'e2e_updated'}, token=TOKEN)
if s == 200:
    log('SETTINGS_PROFILE', 'PASS', f"Profile updated: {r.get('username')}")
else:
    log('SETTINGS_PROFILE', 'FAIL', f"HTTP {s}: {r}")

# ─── STEP 22: SETTINGS - CHANGE PASSWORD ─────────────────────
section("STEP 22: Settings - Change Password")
s, r = api('POST', '/api/auth/change-password/', {'old_password': 'Audit@12345', 'new_password': 'NewAudit@999'}, token=TOKEN)
if s == 200:
    log('SETTINGS_PASSWORD', 'PASS', f"Password changed: {r.get('message')}")
else:
    log('SETTINGS_PASSWORD', 'FAIL', f"HTTP {s}: {r}")

# ─── STEP 23: ERROR - EMPTY PROMPT ───────────────────────────
section("STEP 23: Error Scenario - Empty Prompt")
s, r = api('POST', '/api/ai-tasks/', {'prompt': '', 'workspace_id': WORKSPACE_ID}, token=TOKEN)
if s == 400:
    log('ERROR_EMPTY_PROMPT', 'PASS', f"Validation works: {r}")
else:
    log('ERROR_EMPTY_PROMPT', 'FAIL', f"Expected 400, got HTTP {s}: {r}")

# ─── STEP 24: ERROR - DISCONNECT INTEGRATION ─────────────────
section("STEP 24: Disconnect Integration")
s, r = api('POST', '/api/integrations/github/disconnect/', {}, token=TOKEN)
if s == 200:
    log('INTEGRATIONS_DISCONNECT', 'PASS', f"GitHub disconnected: {r.get('message')}")
else:
    log('INTEGRATIONS_DISCONNECT', 'FAIL', f"HTTP {s}: {r}")

# ─── STEP 25: DELETE ACCOUNT (re-login first) ────────────────
section("STEP 25: Delete Account Verification (dry-run)")
# Re-login with new password
s, r = api('POST', '/api/auth/token/', {'username': 'e2e_updated', 'password': 'NewAudit@999'})
if s == 200:
    NEW_TOKEN = r['access']
    log('RELOGIN_AFTER_PW_CHANGE', 'PASS', f"Re-login with new password succeeded")
    # Test delete with wrong password (should fail)
    s, r = api('POST', '/api/auth/delete-account/', {'password': 'wrong_password'}, token=NEW_TOKEN)
    if s == 400:
        log('DELETE_ACCOUNT_GUARD', 'PASS', f"Delete blocked with wrong password: {r.get('error')}")
    else:
        log('DELETE_ACCOUNT_GUARD', 'FAIL', f"Expected 400, got HTTP {s}: {r}")
    # Now actually delete the e2e test account
    s, r = api('POST', '/api/auth/delete-account/', {'password': 'NewAudit@999'}, token=NEW_TOKEN)
    if s == 200:
        log('DELETE_ACCOUNT', 'PASS', f"Account soft-deleted: {r.get('message')}")
    else:
        log('DELETE_ACCOUNT', 'FAIL', f"HTTP {s}: {r}")
else:
    log('RELOGIN_AFTER_PW_CHANGE', 'FAIL', f"Re-login failed HTTP {s}: {r}")

# ─── FINAL REPORT ────────────────────────────────────────────
print("\n" + "="*60)
print("  FINAL E2E AUDIT REPORT")
print("="*60)
passed = [r for r in RESULTS if r['status'] == 'PASS']
failed = [r for r in RESULTS if r['status'] == 'FAIL']
warned = [r for r in RESULTS if r['status'] == 'WARN']
print(f"\n✅ PASSED: {len(passed)}")
print(f"❌ FAILED: {len(failed)}")
print(f"⚠️  WARNED: {len(warned)}")

if failed:
    print("\n--- FAILURES ---")
    for r in failed:
        print(f"  ❌ {r['step']}: {r['detail'][:150]}")

if warned:
    print("\n--- WARNINGS ---")
    for r in warned:
        print(f"  ⚠️  {r['step']}: {r['detail'][:150]}")

print(f"\nTotal steps audited: {len(RESULTS)}")
