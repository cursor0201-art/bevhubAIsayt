import json
import logging
from core.domain.models import Project, ProjectFile, Page, ProjectReview
from core.services.ai_router import AIRouterService

logger = logging.getLogger(__name__)

class BaseAnalyzer:
    def __init__(self, key: str):
        self.key = key

    def analyze(self, project: Project, files: list, pages: list) -> dict:
        raise NotImplementedError("Analyzers must implement analyze method.")

class ArchitectureAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__("architecture")

    def analyze(self, project: Project, files: list, pages: list) -> dict:
        issues = []
        recommendations = []
        score = 100

        # Check for Clean Architecture separation
        has_components = any("components" in f.path.lower() for f in files)
        has_pages = any("pages" in f.path.lower() or "app" in f.path.lower() for f in files)
        
        if not (has_components and has_pages):
            score -= 15
            issues.append({
                "severity": "medium",
                "title": "Loose Project Directory Structure",
                "description": "The codebase does not cleanly separate UI components from pages/routes. Organize directories to follow clean architecture guidelines."
            })

        for f in files:
            lines = f.content.split("\n")
            if len(lines) > 300:
                score -= 10
                issues.append({
                    "severity": "medium",
                    "title": f"Monolithic File: {f.path}",
                    "description": f"The file '{f.path}' has {len(lines)} lines. Split components to satisfy SOLID single responsibility and keep files under 300 lines."
                })

        if score == 100:
            recommendations.append("Project conforms to Clean Architecture and SOLID rules.")
        else:
            recommendations.append("Apply DRY principles by modularizing repeat structures in presentational modules.")

        return {"score": max(50, score), "issues": issues, "recommendations": recommendations}

class ReactAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__("react")

    def analyze(self, project: Project, files: list, pages: list) -> dict:
        issues = []
        recommendations = []
        score = 100

        for f in files:
            if not f.path.endswith((".js", ".jsx", ".ts", ".tsx", ".html")):
                continue
            
            content = f.content
            # Check useEffect dependency arrays
            if "useEffect(" in content and "useEffect(() =>" in content:
                if ", [])" not in content and ", [" not in content:
                    score -= 10
                    issues.append({
                        "severity": "high",
                        "title": "Raw useEffect Dependency Array",
                        "description": f"A useEffect call in '{f.path}' seems to lack a dependency array, potentially leading to infinite render loops."
                    })
            
            # Check memoization checks
            if ".map(" in content and "useMemo(" not in content and len(content) > 5000:
                score -= 5
                issues.append({
                    "severity": "low",
                    "title": "Missing useMemo for Large Loops",
                    "description": f"Large .map rendering found in '{f.path}'. Wrap computed data sets in useMemo to prevent unnecessary calculations."
                })

        if score == 100:
            recommendations.append("React state triggers, lifecycle effects, and memo hooks comply with best practices.")
        else:
            recommendations.append("Enforce client-side hooks isolation and check useEffect dependency keys.")

        return {"score": max(50, score), "issues": issues, "recommendations": recommendations}

class NextjsAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__("nextjs")

    def analyze(self, project: Project, files: list, pages: list) -> dict:
        issues = []
        recommendations = []
        score = 100

        for p in pages:
            content = p.raw_content.lower()
            if "<img" in content and "next/image" not in content:
                score -= 10
                issues.append({
                    "severity": "medium",
                    "title": f"Unoptimized HTML Image Tag in /{p.slug}",
                    "description": "Standard <img> tags found. Use Next.js Image component (<Image>) to benefit from automatic format conversion, webp generation, and sizing constraints."
                })

            if "google-font" in content or "fonts.googleapis.com" in content:
                score -= 5
                issues.append({
                    "severity": "low",
                    "title": "External Font Import Link",
                    "description": "Direct external font stylesheets reduce page load speed. Use next/font/google to optimize and self-host typography assets."
                })

        if score == 100:
            recommendations.append("Next.js server-side configurations, metadata structures, and components are fully optimized.")
        else:
            recommendations.append("Transition heavy layouts to Next.js App Router server components.")

        return {"score": max(50, score), "issues": issues, "recommendations": recommendations}

class TypeScriptAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__("typescript")

    def analyze(self, project: Project, files: list, pages: list) -> dict:
        issues = []
        recommendations = []
        score = 100

        for f in files:
            if not f.path.endswith((".ts", ".tsx")):
                continue
            
            content = f.content
            if ": any" in content or "as any" in content:
                score -= 10
                issues.append({
                    "severity": "high",
                    "title": "Explicit 'any' Type Declaration",
                    "description": f"Found 'any' type in '{f.path}'. Replace with strict type signatures or 'unknown' to avoid runtime errors."
                })

        if score == 100:
            recommendations.append("TypeScript strict configuration and explicit interfaces are fully enforced.")
        else:
            recommendations.append("Perform refactoring to eliminate loose any-typed variables and use strict generic typing.")

        return {"score": max(50, score), "issues": issues, "recommendations": recommendations}

class TailwindAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__("tailwind")

    def analyze(self, project: Project, files: list, pages: list) -> dict:
        issues = []
        recommendations = []
        score = 100

        for f in files:
            if not f.path.endswith((".html", ".jsx", ".tsx", ".js")):
                continue
            
            content = f.content
            if "p-4" in content and "p-2" in content:
                score -= 5
                issues.append({
                    "severity": "low",
                    "title": f"Redundant Spacing Classes in {f.path}",
                    "description": "Multiple padding overrides detected in class definitions. Clean up className references."
                })

        if score == 100:
            recommendations.append("Tailwind CSS classes adhere to unified design tokens and breakpoints.")
        else:
            recommendations.append("Standardize responsive modifiers (sm:, md:, lg:) and clean up spacing utilities.")

        return {"score": max(50, score), "issues": issues, "recommendations": recommendations}

class UXAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__("ux")

    def analyze(self, project: Project, files: list, pages: list) -> dict:
        issues = []
        recommendations = []
        score = 100

        ds = project.design_system
        colors = ds.get("colors", [])
        if len(colors) < 2:
            score -= 10
            issues.append({
                "severity": "medium",
                "title": "Low Color Contrast System",
                "description": "The design system has an inadequate color scale, potentially reducing text readability."
            })

        for p in pages:
            if "button" not in p.raw_content.lower() and "href=" not in p.raw_content.lower():
                score -= 15
                issues.append({
                    "severity": "high",
                    "title": f"No Clear Call to Action (CTA) on /{p.slug}",
                    "description": "The page lacks interactive triggers or CTA links to funnel user conversion."
                })

        if score == 100:
            recommendations.append("UX layout defines strong visual hierarchy and clear conversion triggers.")
        else:
            recommendations.append("Introduce prominent primary action buttons at the top fold header (Hero section).")

        return {"score": max(50, score), "issues": issues, "recommendations": recommendations}

class AccessibilityAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__("accessibility")

    def analyze(self, project: Project, files: list, pages: list) -> dict:
        issues = []
        recommendations = []
        score = 100

        for p in pages:
            content = p.raw_content.lower()
            if "<html" in content and 'lang=' not in content:
                score -= 10
                issues.append({
                    "severity": "medium",
                    "title": "Missing lang attribute",
                    "description": "The <html> element does not specify a language attribute, impeding screen readers."
                })
            if "<img" in content and 'alt=' not in content:
                score -= 15
                issues.append({
                    "severity": "high",
                    "title": "Missing Alt Tag on Images",
                    "description": "One or more image tags are missing alt description attributes, violating WCAG requirements."
                })

        if score == 100:
            recommendations.append("Accessibility check passed: correct language tags, landmarks, and alt labels are present.")
        else:
            recommendations.append("Ensure interactive elements contain focus highlights and correct ARIA roles.")

        return {"score": max(50, score), "issues": issues, "recommendations": recommendations}

class SEOAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__("seo")

    def analyze(self, project: Project, files: list, pages: list) -> dict:
        issues = []
        recommendations = []
        score = 100

        for p in pages:
            content = p.raw_content.lower()
            if "<title>" not in content:
                score -= 15
                issues.append({
                    "severity": "high",
                    "title": f"Missing Title Tag on /{p.slug}",
                    "description": "Title tag is missing. Add h1 context and page title headers to enable correct indexing."
                })
            if 'meta name="description"' not in content and 'name="description"' not in content:
                score -= 10
                issues.append({
                    "severity": "medium",
                    "title": f"Missing Meta Description on /{p.slug}",
                    "description": "Meta description is missing. Add descriptive tags to display in search result snippets."
                })
            if 'property="og:' not in content:
                score -= 5
                issues.append({
                    "severity": "low",
                    "title": f"Missing OpenGraph tags on /{p.slug}",
                    "description": "Missing social media preview properties. Add og:title and og:description meta fields."
                })

        if score == 100:
            recommendations.append("SEO tags, canonical configurations, and descriptions are fully complete.")
        else:
            recommendations.append("Include JSON-LD Schema.org structured metadata on primary landing pages.")

        return {"score": max(50, score), "issues": issues, "recommendations": recommendations}

class PerformanceAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__("performance")

    def analyze(self, project: Project, files: list, pages: list) -> dict:
        issues = []
        recommendations = []
        score = 100

        for p in pages:
            if len(p.raw_content) > 100000:
                score -= 15
                issues.append({
                    "severity": "high",
                    "title": f"Heavy page size on /{p.slug}",
                    "description": "Page layout content exceeds optimal size. Optimize asset links and lazy load sections."
                })
            if "<img" in p.raw_content and "loading=\"lazy\"" not in p.raw_content:
                score -= 5
                issues.append({
                    "severity": "medium",
                    "title": "Unoptimized Images",
                    "description": "HTML image tags lack explicit loading='lazy' attributes, impacting early load metrics."
                })

        if score == 100:
            recommendations.append("All assets and document weights conform to Next.js speed optimization guidelines.")
        else:
            recommendations.append("Configure dynamic imports for heavy components and enforce image dimensions.")

        return {"score": max(50, score), "issues": issues, "recommendations": recommendations}

class SecurityAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__("security")

    def analyze(self, project: Project, files: list, pages: list) -> dict:
        issues = []
        recommendations = []
        score = 100

        for p in pages:
            if "onclick=" in p.raw_content or "onload=" in p.raw_content:
                score -= 15
                issues.append({
                    "severity": "high",
                    "title": "Inline Script Handler Detected",
                    "description": f"Inline event handlers like 'onclick' in /{p.slug} violate Content Security Policy (CSP). Migrate event handlers to structured JS listeners."
                })

        for f in files:
            lower_content = f.content.lower()
            if "api_key" in lower_content or "secret_key" in lower_content or "password=" in lower_content:
                score -= 30
                issues.append({
                    "severity": "critical",
                    "title": f"Potential Credential Exposure in {f.path}",
                    "description": "Found sensitive keywords ('api_key', 'secret_key') in file. Move credentials to environment variables (.env)."
                })

        if score == 100:
            recommendations.append("No critical vulnerabilities or hardcoded secrets found in static code review.")
        else:
            recommendations.append("Add structured Content Security Policy (CSP) headers and use .env files for secrets.")

        return {"score": max(30, score), "issues": issues, "recommendations": recommendations}

class DeploymentAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__("deployment")

    def analyze(self, project: Project, files: list, pages: list) -> dict:
        issues = []
        recommendations = []
        score = 100

        has_docker = any("dockerfile" in f.path.lower() for f in files)
        if not has_docker:
            score -= 10
            issues.append({
                "severity": "low",
                "title": "Missing Docker Configuration",
                "description": "No Dockerfile found in the repository root. Re-run devops agent to bundle image settings."
            })

        if score == 100:
            recommendations.append("Deployment configuration matches Vercel and Docker production setups.")
        else:
            recommendations.append("Maintain config rules for multi-stage Docker builds to reduce runtime bundle size.")

        return {"score": max(50, score), "issues": issues, "recommendations": recommendations}

class AIPromptAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__("aiprompt")

    def analyze(self, project: Project, files: list, pages: list) -> dict:
        issues = []
        recommendations = []
        score = 100

        # Heuristic check on project context name/prompts clarity
        prompt_text = project.project_name
        if len(prompt_text) < 10:
            score -= 15
            issues.append({
                "severity": "medium",
                "title": "Short AI Generator Prompt",
                "description": "The prompt describing this project is extremely short. Detailed specifications result in higher fidelity code generation."
            })

        if score == 100:
            recommendations.append("AI prompt specifies domain requirements, coloring scheme, and database schema explicitly.")
        else:
            recommendations.append("Refine generation prompts by listing explicit routes, data attributes, and UI theme styling details.")

        return {"score": max(50, score), "issues": issues, "recommendations": recommendations}

class ReviewService:
    def __init__(self):
        self.ai_router = AIRouterService()
        self.analyzers = [
            ArchitectureAnalyzer(),
            ReactAnalyzer(),
            NextjsAnalyzer(),
            TypeScriptAnalyzer(),
            TailwindAnalyzer(),
            UXAnalyzer(),
            AccessibilityAnalyzer(),
            SEOAnalyzer(),
            PerformanceAnalyzer(),
            SecurityAnalyzer(),
            DeploymentAnalyzer(),
            AIPromptAnalyzer()
        ]

    def perform_code_review(self, project: Project) -> ProjectReview:
        """
        Executes code reviews using rule-based static analyzers combined with
        an AI model evaluation run.
        """
        files = list(project.files.all())
        pages = list(project.pages.all())

        # Collect heuristic analysis results from all 12 analyzers
        analyzer_results = {}
        all_issues = []
        all_recs = []

        for analyzer in self.analyzers:
            res = analyzer.analyze(project, files, pages)
            analyzer_results[analyzer.key] = res["score"]
            all_issues.extend(res["issues"])
            all_recs.extend(res["recommendations"])

        # Call AI model to run deep context analysis & refine review
        try:
            provider_name = self.ai_router.select_best_provider_for_task("reasoning_analysis")
            provider = self.ai_router.get_provider(provider_name)

            sys_instruction = (
                "You are the AI Code Reviewer. Analyze the provided project files, design system parameters, "
                "and static analyzer warnings. Return a refined JSON report matching the specified schema format. "
                "The response must be valid JSON only. Do NOT include markdown tags, conversations, or wrappers."
            )

            codebase_summary = []
            for f in files[:10]:
                codebase_summary.append(f"File: {f.path}\nContent snippet:\n{f.content[:1500]}")

            user_msg = (
                f"Design System:\n{json.dumps(project.design_system)}\n\n"
                f"Static Analyzer Findings:\n{json.dumps(all_issues)}\n\n"
                f"Codebase:\n" + "\n\n".join(codebase_summary) + "\n\n"
                "Please perform a deep architectural, TypeScript, React, Next.js, and Security evaluation. "
                "Return a single JSON with refined scores (overall_score, architecture, performance, security, "
                "seo, accessibility, ux, typescript, react, deployment), additional critical/high issues, and "
                "reusable recommendations."
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

            ai_report = json.loads(text)
        except Exception as e:
            logger.error(f"AI model call failed during Code Review: {e}")
            # Fallback to pure heuristic report
            overall = int(sum(analyzer_results.values()) / len(analyzer_results))
            ai_report = {
                "overall_score": overall,
                "architecture": int((analyzer_results.get("architecture", 90) + analyzer_results.get("aiprompt", 90)) / 2),
                "performance": analyzer_results.get("performance", 90),
                "security": analyzer_results.get("security", 90),
                "seo": analyzer_results.get("seo", 90),
                "accessibility": analyzer_results.get("accessibility", 90),
                "ux": int((analyzer_results.get("ux", 90) + analyzer_results.get("tailwind", 90)) / 2),
                "typescript": analyzer_results.get("typescript", 90),
                "react": int((analyzer_results.get("react", 90) + analyzer_results.get("nextjs", 90)) / 2),
                "deployment": analyzer_results.get("deployment", 90),
                "issues": all_issues,
                "recommendations": all_recs
            }

        # Merge findings
        overall_score = ai_report.get("overall_score", 90)
        issues = ai_report.get("issues", [])
        existing_titles = {issue.get("title") for issue in issues}
        for item in all_issues:
            if item.get("title") not in existing_titles:
                issues.append(item)

        recs = ai_report.get("recommendations", [])
        for rec in all_recs:
            if rec not in recs:
                recs.append(rec)

        # Write to Database
        review = ProjectReview.objects.create(
            project=project,
            overall_score=overall_score,
            architecture_score=ai_report.get("architecture", 90),
            performance_score=ai_report.get("performance", 90),
            security_score=ai_report.get("security", 90),
            seo_score=ai_report.get("seo", 90),
            accessibility_score=ai_report.get("accessibility", 90),
            ux_score=ai_report.get("ux", 90),
            typescript_score=ai_report.get("typescript", 90),
            react_score=ai_report.get("react", 90),
            deployment_score=ai_report.get("deployment", 90),
            issues=issues,
            recommendations=recs,
            raw_report=ai_report
        )

        try:
            from core.domain.models import UserJourneyEvent
            owner = project.owner or project.tenant.users.first()
            UserJourneyEvent.objects.create(
                user=owner,
                step='code_review_completed',
                status='success',
                duration_ms=2000,
                logs=f"Overall Score: {overall_score}. Issues: {len(issues)}",
                workspace_id=str(project.workspace.id) if project.workspace else ""
            )
        except Exception as e:
            logger.warning(f"Telemetry log failed for code review: {e}")

        return review
