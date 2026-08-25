from django.core.management.base import BaseCommand
import time
import json
import concurrent.futures
from statistics import mean, quantiles
from django.contrib.auth import get_user_model
from django.db import connection
from core.domain.models import Tenant, Workspace, Project
from ai.services.context_engine import ContextEngine

User = get_user_model()

class Command(BaseCommand):
    help = "Runs Operation Iron Wall scale benchmarks, stress tests, and chaos verification."

    def handle(self, *args, **options):
        self.stdout.write("=== STARTING OPERATION IRON WALL BENCHMARKING ===")
        
        # 1. Base Setup
        tenant = Tenant.objects.create(company_name="Benchmarking Corp", plan_level="growth")
        user = User.objects.create_user(
            username='benchuser_' + str(int(time.time())), 
            password='password123', 
            email='bench@bench.com', 
            tenant=tenant
        )
        workspace = Workspace.objects.create(tenant=tenant, name="Bench Workspace")
        project = Project.objects.create(
            tenant=tenant,
            workspace=workspace,
            owner=user,
            project_name="Benchmark Project",
            subdomain="bench-sub-" + str(int(time.time()))
        )

        # 2. Context Engine Latency Profiling
        self.stdout.write("Profiling ContextEngine...")
        latencies = []
        for _ in range(100):
            t0 = time.perf_counter()
            ContextEngine.get_generation_context(project, user)
            latencies.append((time.perf_counter() - t0) * 1000) # in ms
        
        avg_latency = mean(latencies)
        p95_latency = quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies)
        p99_latency = quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies)
        
        self.stdout.write(f"ContextEngine Latency - Avg: {avg_latency:.2f}ms, P95: {p95_latency:.2f}ms, P99: {p99_latency:.2f}ms")

        # 3. Scale Stress Simulations
        user_scales = [50, 100, 250, 500, 1000]
        stress_results = {}

        def simulate_request():
            t0 = time.perf_counter()
            try:
                # Simulated DB queries read operations
                p = Project.objects.get(id=project.id)
                ContextEngine.get_generation_context(p, user)
                return (time.perf_counter() - t0) * 1000, True
            except Exception:
                return (time.perf_counter() - t0) * 1000, False

        for scale in user_scales:
            self.stdout.write(f"Simulating stress level: {scale} concurrent requests...")
            with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
                t_start = time.perf_counter()
                futures = [executor.submit(simulate_request) for _ in range(scale)]
                results = [f.result() for f in futures]
                duration = (time.perf_counter() - t_start) * 1000
            
            times = [r[0] for r in results]
            successes = [r[1] for r in results]
            
            success_rate = (sum(successes) / scale) * 100
            avg_t = mean(times)
            p95_t = quantiles(times, n=20)[18] if len(times) >= 20 else max(times)
            p99_t = quantiles(times, n=100)[98] if len(times) >= 100 else max(times)
            
            stress_results[str(scale)] = {
                "success_rate": success_rate,
                "avg_latency_ms": round(avg_t, 2),
                "p95_latency_ms": round(p95_t, 2),
                "p99_latency_ms": round(p99_t, 2),
                "throughput_req_sec": round((scale / (duration / 1000)), 2)
            }
            self.stdout.write(f"Scale {scale} results - Success: {success_rate}%, Avg: {avg_t:.2f}ms, Throughput: {stress_results[str(scale)]['throughput_req_sec']} req/sec")

        # 4. Chaos Outage / Recovery verification
        self.stdout.write("Verifying Chaos Resilience recovery...")
        chaos_passed = False
        try:
            # Simulate connection closure / drop database connection
            connection.close()
            # Verify automatic reconnect on first query
            Project.objects.first()
            chaos_passed = True
            self.stdout.write("Chaos Recovery check: Successful reconnect after connection loss!")
        except Exception as e:
            self.stdout.write(f"Chaos Recovery check: Failed! Error: {e}")

        # 5. Save report metrics to disk
        report_data = {
            "context_engine": {
                "avg_latency_ms": round(avg_latency, 2),
                "p95_latency_ms": round(p95_latency, 2),
                "p99_latency_ms": round(p99_latency, 2)
            },
            "stress_test": stress_results,
            "chaos_resilience": {
                "db_reconnect_recovery": "SUCCESS" if chaos_passed else "FAILURE"
            }
        }
        
        # Save to main app data directory brain folder for E2E validation tracking
        import os
        from django.conf import settings
        report_path = r"C:\Users\user\.gemini\antigravity\brain\533d3f40-44c9-46eb-903a-1c202d6923b7\iron_wall_metrics.json"
        
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        self.stdout.write(f"Metrics saved to {report_path}")
