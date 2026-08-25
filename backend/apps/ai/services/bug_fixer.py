import json
import logging
import time
from core.domain.models import Project, ProjectFile, Page, ProjectReview, ProjectSnapshot, ProjectFixRun
from core.services.ai_router import AIRouterService

logger = logging.getLogger(__name__)

class SnapshotService:
    @staticmethod
    def create_snapshot(project: Project, description: str = "") -> ProjectSnapshot:
        """
        Creates a full backup snapshot of project design system, files, and pages.
        """
        files_data = []
        for f in project.files.all():
            files_data.append({
                "path": f.path,
                "content": f.content
            })
        
        pages_data = []
        for p in project.pages.all():
            pages_data.append({
                "slug": p.slug,
                "title": p.title,
                "layout_ast": p.layout_ast,
                "raw_content": p.raw_content
            })

        snapshot_data = {
            "design_system": project.design_system,
            "files": files_data,
            "pages": pages_data
        }

        snapshot = ProjectSnapshot.objects.create(
            project=project,
            snapshot_data=snapshot_data,
            description=description
        )
        logger.info(f"Snapshot {snapshot.id} created for project {project.id}")
        return snapshot

    @staticmethod
    def restore_snapshot(snapshot: ProjectSnapshot):
        """
        Restores a project to the exact state saved in the snapshot.
        """
        project = snapshot.project
        data = snapshot.snapshot_data

        # Restore design system
        project.design_system = data.get("design_system", {})
        project.save(update_fields=["design_system"])

        # Restore files (Clear & Re-insert)
        project.files.all().hard_delete()
        for f_info in data.get("files", []):
            ProjectFile.objects.create(
                project=project,
                path=f_info["path"],
                content=f_info["content"]
            )

        # Restore pages (Clear & Re-insert)
        project.pages.all().hard_delete()
        for p_info in data.get("pages", []):
            Page.objects.create(
                project=project,
                slug=p_info["slug"],
                title=p_info["title"],
                layout_ast=p_info["layout_ast"],
                raw_content=p_info["raw_content"]
            )
        logger.info(f"Project {project.id} restored to snapshot {snapshot.id}")


class RollbackService:
    @staticmethod
    def rollback(snapshot: ProjectSnapshot):
        """
        Invokes SnapshotService restoration to rollback project changes.
        """
        SnapshotService.restore_snapshot(snapshot)


class FixPlanner:
    def __init__(self):
        self.ai_router = AIRouterService()

    def build_plan(self, project: Project, review: ProjectReview) -> list:
        """
        Creates a list of prioritized fix targets based on Code Review issues.
        Each contains: id, severity, reason, root_cause, affected_files, fix_strategy, confidence, estimated_risk.
        """
        issues = review.issues or []
        if not issues:
            return []

        try:
            provider_name = self.ai_router.select_best_provider_for_task("reasoning_analysis")
            provider = self.ai_router.get_provider(provider_name)

            sys_instruction = (
                "You are an expert AI Fix Planner. Analyze the review issues and project files. "
                "Output a valid JSON list of fix items. Do NOT wrap in markdown tags, explanations, or templates. "
                "Each list item MUST match the schema structure exactly:\n"
                "{\n"
                "  \"id\": \"unique-string-slug\",\n"
                "  \"severity\": \"critical|high|medium|low\",\n"
                "  \"reason\": \"...\",\n"
                "  \"root_cause\": \"...\",\n"
                "  \"affected_files\": [\"path/to/file\"],\n"
                "  \"fix_strategy\": \"...\",\n"
                "  \"confidence\": 95,\n"
                "  \"estimated_risk\": 10\n"
                "}"
            )

            files_list = [f.path for f in project.files.all()]
            user_msg = (
                f"Issues List:\n{json.dumps(issues)}\n\n"
                f"Available Files:\n{json.dumps(files_list)}\n\n"
                "Generate a prioritized plan of fixes sorted by severity. Ensure affected_files refer to actual files."
            )

            response = provider.generate_text(prompt=user_msg, system_instruction=sys_instruction)
            text = response.text.strip()

            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

            plan = json.loads(text)
        except Exception as e:
            logger.error(f"Failed to generate fix plan with AI: {e}. Falling back to rule-based planner.")
            plan = []
            for i, issue in enumerate(issues):
                severity = issue.get("severity", "medium")
                title = issue.get("title", "Unknown issue")
                desc = issue.get("description", "")
                
                affected = []
                for f in project.files.all():
                    if f.path.split("/")[-1].lower() in desc.lower() or f.path.split("/")[-1].lower() in title.lower():
                        affected.append(f.path)
                
                if not affected:
                    primary = project.files.filter(path__icontains="index").first()
                    if primary:
                        affected.append(primary.path)
                    else:
                        first_f = project.files.first()
                        if first_f:
                            affected.append(first_f.path)

                risk_val = 10 if severity == "low" else (30 if severity == "medium" else (60 if severity == "high" else 80))
                confidence_val = 90

                plan.append({
                    "id": f"fix-{i}-{severity}",
                    "severity": severity,
                    "reason": f"Resolve: {title}",
                    "root_cause": desc,
                    "affected_files": affected,
                    "fix_strategy": f"Analyze file content and refactor code to fix {title}.",
                    "confidence": confidence_val,
                    "estimated_risk": risk_val
                })

        plan = sorted(plan, key=lambda x: x.get("estimated_risk", 50), reverse=True)
        return plan


class FixExecutor:
    def __init__(self):
        self.ai_router = AIRouterService()

    def execute_fix(self, project: Project, fix: dict) -> dict:
        """
        Executes a single fix target on the project files.
        """
        affected_paths = fix.get("affected_files", [])
        if not affected_paths:
            return {"success": False, "affected_files": [], "error": "No affected files specified."}

        target_files = []
        for path in affected_paths:
            tf = project.files.filter(path=path).first()
            if tf:
                target_files.append(tf)

        if not target_files:
            return {"success": False, "affected_files": [], "error": "Affected files do not exist."}

        provider_name = self.ai_router.select_best_provider_for_task("reasoning_analysis")
        provider = self.ai_router.get_provider(provider_name)

        try:
            sys_instruction = (
                "You are an expert AI Fix Executor. Your task is to refactor code files to resolve issues. "
                "You must return the corrected file content inside a structured JSON object. "
                "Do NOT wrap in markdown tags, explanations, or templates. "
                "Response structure:\n"
                "{\n"
                "  \"files\": [\n"
                "    {\n"
                "      \"path\": \"path/to/file\",\n"
                "      \"content\": \"... full new content ...\"\n"
                "    }\n"
                "  ],\n"
                "  \"lines_modified\": \"Modified lines 12-25 to integrate missing SEO tag.\",\n"
                "  \"explanation\": \"Added meta description and optimized img alt attributes.\"\n"
                "}"
            )

            files_payload = []
            for tf in target_files:
                files_payload.append({
                    "path": tf.path,
                    "content": tf.content
                })

            user_msg = (
                f"Issue to Fix:\n{json.dumps(fix)}\n\n"
                f"Files to Refactor:\n{json.dumps(files_payload)}\n\n"
                "Please rewrite the contents of these files to apply the fix strategy. Make sure to keep all other functionality unchanged."
            )

            response = provider.generate_text(prompt=user_msg, system_instruction=sys_instruction)
            text = response.text.strip()

            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

            result = json.loads(text)
            
            for f_edit in result.get("files", []):
                path = f_edit["path"]
                content = f_edit["content"]
                proj_file = project.files.filter(path=path).first()
                if proj_file:
                    proj_file.content = content
                    proj_file.save()
                    
                    slug = path.split("/")[-1].replace(".html", "").replace(".js", "").replace(".tsx", "")
                    page = project.pages.filter(slug=slug).first()
                    if page:
                        page.raw_content = content
                        page.save()

            return {
                "success": True,
                "affected_files": affected_paths,
                "lines_modified": result.get("lines_modified", "All lines"),
                "explanation": result.get("explanation", ""),
                "model": provider_name
            }
        except Exception as e:
            logger.error(f"Failed to execute fix: {e}")
            return {
                "success": False,
                "affected_files": affected_paths,
                "error": str(e),
                "model": provider_name
            }


class ReviewComparator:
    @staticmethod
    def compare(before: ProjectReview, after: ProjectReview) -> dict:
        """
        Compares before and after reviews to detect score improvements.
        """
        diff = after.overall_score - before.overall_score
        improved = diff > 0
        return {
            "improved": improved,
            "difference": diff,
            "details": f"Score changed from {before.overall_score} to {after.overall_score} ({'+' if diff >= 0 else ''}{diff})"
        }


class BugFixService:
    def __init__(self):
        self.planner = FixPlanner()
        self.executor = FixExecutor()
        self.comparator = ReviewComparator()

    def run_bug_fix_pipeline(self, project: Project) -> dict:
        """
        Orchestrates the complete AI Bug Fixer pipeline:
        Review -> Snapshot -> Plan -> Fix -> Re-Review -> Compare -> Commit/Rollback.
        """
        start_time = time.time()

        from apps.ai.services.review_engine import ReviewService
        review_service = ReviewService()
        
        before_review = project.reviews.order_by("-created_at").first()
        if not before_review:
            before_review = review_service.perform_code_review(project)

        before_score = before_review.overall_score

        # 1. Create Snapshot
        snapshot = SnapshotService.create_snapshot(project, description="Pre-fix snapshot protection")

        # 2. Build prioritized fix plan
        plan = self.planner.build_plan(project, before_review)

        fixed_count = 0
        logs = []

        # 3. Execute fixes
        for fix in plan:
            fix_start = time.time()
            res = self.executor.execute_fix(project, fix)
            fix_end = time.time()
            
            logs.append({
                "issue_id": fix["id"],
                "severity": fix["severity"],
                "reason": fix["reason"],
                "root_cause": fix["root_cause"],
                "affected_files": fix["affected_files"],
                "fix_strategy": fix["fix_strategy"],
                "success": res.get("success", False),
                "lines_modified": res.get("lines_modified", ""),
                "explanation": res.get("explanation", ""),
                "model": res.get("model", "Fallback"),
                "duration_ms": int((fix_end - fix_start) * 1000)
            })
            if res.get("success"):
                fixed_count += 1

        # 4. Perform after-fix review
        after_review = review_service.perform_code_review(project)
        after_score = after_review.overall_score

        # 5. Review comparison & rollback evaluation
        comp = self.comparator.compare(before_review, after_review)

        rollback_applied = False
        if not comp["improved"]:
            RollbackService.rollback(snapshot)
            rollback_applied = True
            final_score = before_score
        else:
            final_score = after_score

        # 6. Save FixRun record
        fix_run = ProjectFixRun.objects.create(
            project=project,
            before_score=before_score,
            after_score=final_score,
            fixed_count=fixed_count,
            remaining_count=len(plan) - fixed_count if not rollback_applied else len(plan),
            rollback_applied=rollback_applied,
            snapshot=snapshot,
            logs=logs
        )

        try:
            from core.domain.models import UserJourneyEvent
            owner = project.owner or project.tenant.users.first()
            UserJourneyEvent.objects.create(
                user=owner,
                step='bug_fix_pipeline_completed',
                status='success',
                duration_ms=int((time.time() - start_time) * 1000),
                logs=f"Before: {before_score}, After: {final_score}, Fixed: {fixed_count}, Rollback: {rollback_applied}",
                workspace_id=str(project.workspace.id) if project.workspace else ""
            )
        except Exception as e:
            logger.warning(f"Telemetry log failed for bug fixer: {e}")

        return {
            "before_score": before_score,
            "after_score": final_score,
            "fixed": fixed_count if not rollback_applied else 0,
            "remaining": len(plan) - fixed_count if not rollback_applied else len(plan),
            "rollback_available": rollback_applied,
            "snapshot_id": str(snapshot.id),
            "fix_run_id": str(fix_run.id)
        }
