"""
BevHub AI — Reasoning Engine
Version 1.0

The cognitive core of BevHub AI. Transforms raw user requests into structured,
validated, production-ready engineering decisions before any specialist executes.

Every agent call is preceded by a ReasoningEngine analysis pass.
"""

import logging
import os
from enum import Enum
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from django.conf import settings

logger = logging.getLogger(__name__)


# ==================================================
# ENUMS
# ==================================================

class ThinkingMode(str, Enum):
    FAST       = "fast"        # simple fixes, minor changes
    ANALYTICAL = "analytical"  # architecture, system design
    CREATIVE   = "creative"    # design, UX, branding
    CRITICAL   = "critical"    # security, compliance
    STRATEGIC  = "strategic"   # business, growth, monetisation
    RESEARCH   = "research"    # unknown or novel domains


class ProblemCategory(str, Enum):
    BUSINESS     = "business"
    TECHNICAL    = "technical"
    UX           = "ux"
    PERFORMANCE  = "performance"
    SECURITY     = "security"
    SCALABILITY  = "scalability"
    OPERATIONAL  = "operational"


class ComplexityLevel(str, Enum):
    TINY       = "tiny"
    SMALL      = "small"
    MEDIUM     = "medium"
    LARGE      = "large"
    ENTERPRISE = "enterprise"
    PLATFORM   = "platform"


class RequestClass(str, Enum):
    WEBSITE          = "website"
    LANDING_PAGE     = "landing_page"
    CRM              = "crm"
    ERP              = "erp"
    MARKETPLACE      = "marketplace"
    PORTFOLIO        = "portfolio"
    DASHBOARD        = "dashboard"
    AI_SAAS          = "ai_saas"
    MOBILE_APP       = "mobile_app"
    TELEGRAM_BOT     = "telegram_bot"
    BROWSER_EXT      = "browser_extension"
    DESKTOP_APP      = "desktop_app"
    API              = "api"
    BACKEND          = "backend"
    FRONTEND         = "frontend"
    DATABASE         = "database"
    INFRASTRUCTURE   = "infrastructure"
    BUG_FIX          = "bug_fix"
    OPTIMIZATION     = "optimization"
    SECURITY         = "security"
    TESTING          = "testing"
    DOCUMENTATION    = "documentation"


# ==================================================
# DATA MODELS
# ==================================================

@dataclass
class DecisionScore:
    """Numeric evaluation of a candidate solution across 9 dimensions."""
    business_value:       float = 0.0   # 0–10
    engineering_complexity: float = 0.0 # 0–10  (lower = better)
    maintainability:      float = 0.0
    performance:          float = 0.0
    security:             float = 0.0
    scalability:          float = 0.0
    developer_experience: float = 0.0
    user_experience:      float = 0.0
    operational_cost:     float = 0.0   # 0–10 (lower = better)

    @property
    def overall(self) -> float:
        """Weighted composite score. Complexity and cost are inverted."""
        return round(
            self.business_value        * 1.5
            + self.maintainability     * 1.2
            + self.performance         * 1.0
            + self.security            * 1.3
            + self.scalability         * 1.1
            + self.developer_experience * 0.8
            + self.user_experience     * 1.0
            - self.engineering_complexity * 0.7
            - self.operational_cost    * 0.5,
            2
        )


@dataclass
class CandidateSolution:
    """One of ≥3 alternative approaches evaluated during reasoning."""
    title:       str
    description: str
    score:       DecisionScore = field(default_factory=DecisionScore)
    risks:       List[str]     = field(default_factory=list)


@dataclass
class QualityScore:
    """Internal confidence report generated after self-critique."""
    correctness:       float = 0.0
    completeness:      float = 0.0
    reliability:       float = 0.0
    maintainability:   float = 0.0
    business_alignment: float = 0.0
    security:          float = 0.0

    @property
    def overall_confidence(self) -> float:
        scores = [
            self.correctness, self.completeness, self.reliability,
            self.maintainability, self.business_alignment, self.security,
        ]
        return round(sum(scores) / len(scores), 2)


@dataclass
class ReasoningResult:
    """Full structured output of a single Reasoning Engine analysis pass."""
    prompt:             str
    request_class:      RequestClass
    thinking_mode:      ThinkingMode
    complexity:         ComplexityLevel

    # problem decomposition
    problems:           Dict[ProblemCategory, str] = field(default_factory=dict)

    # risk register
    risks:              List[str]                  = field(default_factory=list)

    # solution candidates + winner
    candidates:         List[CandidateSolution]    = field(default_factory=list)
    chosen_solution:    Optional[CandidateSolution] = None

    # active specialist parts (loaded by Orchestrator)
    required_parts:     List[int]                  = field(default_factory=list)

    # quality
    quality:            QualityScore               = field(default_factory=QualityScore)

    # learning record
    insights:           List[str]                  = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"[ReasoningEngine] Class={self.request_class.value} | "
            f"Mode={self.thinking_mode.value} | "
            f"Complexity={self.complexity.value} | "
            f"Confidence={self.quality.overall_confidence:.1f}/10 | "
            f"Parts={self.required_parts}"
        )


# ==================================================
# REASONING ENGINE
# ==================================================

class ReasoningEngine:
    """
    The cognitive core of BevHub AI.

    Usage:
        engine = ReasoningEngine()
        result = engine.analyze(prompt, context)
        # then pass result.required_parts and result.chosen_solution to Orchestrator
    """

    # keyword → RequestClass
    _CLASS_MAP: Dict[str, RequestClass] = {
        "crm":              RequestClass.CRM,
        "erp":              RequestClass.ERP,
        "marketplace":      RequestClass.MARKETPLACE,
        "portfolio":        RequestClass.PORTFOLIO,
        "dashboard":        RequestClass.DASHBOARD,
        "saas":             RequestClass.AI_SAAS,
        "mobile":           RequestClass.MOBILE_APP,
        "telegram":         RequestClass.TELEGRAM_BOT,
        "extension":        RequestClass.BROWSER_EXT,
        "desktop":          RequestClass.DESKTOP_APP,
        "api":              RequestClass.API,
        "backend":          RequestClass.BACKEND,
        "frontend":         RequestClass.FRONTEND,
        "database":         RequestClass.DATABASE,
        "deploy":           RequestClass.INFRASTRUCTURE,
        "infrastructure":   RequestClass.INFRASTRUCTURE,
        "bug":              RequestClass.BUG_FIX,
        "fix":              RequestClass.BUG_FIX,
        "optimize":         RequestClass.OPTIMIZATION,
        "performance":      RequestClass.OPTIMIZATION,
        "security":         RequestClass.SECURITY,
        "test":             RequestClass.TESTING,
        "doc":              RequestClass.DOCUMENTATION,
        "landing":          RequestClass.LANDING_PAGE,
        "website":          RequestClass.WEBSITE,
        "store":            RequestClass.MARKETPLACE,
        "shop":             RequestClass.MARKETPLACE,
        "ecommerce":        RequestClass.MARKETPLACE,
    }

    # RequestClass → ThinkingMode
    _MODE_MAP: Dict[RequestClass, ThinkingMode] = {
        RequestClass.BUG_FIX:        ThinkingMode.FAST,
        RequestClass.OPTIMIZATION:   ThinkingMode.ANALYTICAL,
        RequestClass.WEBSITE:        ThinkingMode.CREATIVE,
        RequestClass.LANDING_PAGE:   ThinkingMode.CREATIVE,
        RequestClass.PORTFOLIO:      ThinkingMode.CREATIVE,
        RequestClass.SECURITY:       ThinkingMode.CRITICAL,
        RequestClass.CRM:            ThinkingMode.STRATEGIC,
        RequestClass.ERP:            ThinkingMode.STRATEGIC,
        RequestClass.AI_SAAS:        ThinkingMode.ANALYTICAL,
        RequestClass.DATABASE:       ThinkingMode.ANALYTICAL,
        RequestClass.INFRASTRUCTURE: ThinkingMode.ANALYTICAL,
        RequestClass.DOCUMENTATION:  ThinkingMode.FAST,
    }

    # RequestClass → required specialist part numbers
    _PARTS_MAP: Dict[RequestClass, List[int]] = {
        RequestClass.WEBSITE:        [13, 30, 32, 14, 18, 36, 28, 33],
        RequestClass.LANDING_PAGE:   [13, 30, 14, 18, 37, 36, 28],
        RequestClass.CRM:            [13, 31, 30, 32, 26, 24, 14, 28, 29, 33],
        RequestClass.ERP:            [13, 31, 30, 32, 26, 24, 14, 27, 28, 29, 33],
        RequestClass.MARKETPLACE:    [13, 31, 30, 32, 26, 24, 14, 36, 37, 28, 29, 33],
        RequestClass.DASHBOARD:      [13, 32, 26, 24, 14, 35, 28, 33],
        RequestClass.AI_SAAS:        [13, 31, 30, 32, 26, 24, 14, 36, 37, 28, 29, 33],
        RequestClass.MOBILE_APP:     [13, 30, 32, 25, 35, 34, 28, 29, 33],
        RequestClass.TELEGRAM_BOT:   [13, 32, 24, 28, 29, 33],
        RequestClass.API:            [13, 32, 26, 24, 28, 29, 33],
        RequestClass.BACKEND:        [13, 32, 26, 24, 28, 29, 33],
        RequestClass.FRONTEND:       [13, 14, 35, 34, 36, 28, 33],
        RequestClass.DATABASE:       [13, 32, 26, 29, 28, 33],
        RequestClass.INFRASTRUCTURE: [13, 27, 24, 29, 28, 33],
        RequestClass.SECURITY:       [13, 29, 32, 28, 33],
        RequestClass.OPTIMIZATION:   [13, 32, 24, 28, 33],
        RequestClass.BUG_FIX:        [13, 24, 28, 33],
        RequestClass.TESTING:        [13, 28, 29, 33],
        RequestClass.DOCUMENTATION:  [13, 33],
    }

    def __init__(self):
        self._system_prompt_cache: Dict[int, str] = {}

    # --------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------

    def analyze(self, prompt: str, context: dict) -> ReasoningResult:
        """
        Full reasoning pass. Returns ReasoningResult before any agent runs.
        """
        logger.info(f"[ReasoningEngine] Starting analysis for: '{prompt[:60]}...'")

        request_class = self._classify_request(prompt)
        thinking_mode = self._select_thinking_mode(request_class, prompt)
        complexity    = self._estimate_complexity(prompt)
        problems      = self._decompose_problems(prompt, request_class)
        risks         = self._analyze_risks(prompt, problems, complexity)
        candidates    = self._generate_candidates(prompt, request_class, thinking_mode)
        chosen        = self._select_best_candidate(candidates)
        required_parts = self._resolve_required_parts(request_class, prompt)
        quality       = self._self_critique(chosen, risks, required_parts)
        insights      = self._extract_insights(prompt, chosen, risks)

        result = ReasoningResult(
            prompt=prompt,
            request_class=request_class,
            thinking_mode=thinking_mode,
            complexity=complexity,
            problems=problems,
            risks=risks,
            candidates=candidates,
            chosen_solution=chosen,
            required_parts=required_parts,
            quality=quality,
            insights=insights,
        )

        logger.info(result.summary())
        return result

    # --------------------------------------------------
    # STEP 1: REQUEST CLASSIFICATION
    # --------------------------------------------------

    def _classify_request(self, prompt: str) -> RequestClass:
        lowered = prompt.lower()
        for keyword, cls in self._CLASS_MAP.items():
            if keyword in lowered:
                return cls
        return RequestClass.WEBSITE  # sensible default

    # --------------------------------------------------
    # STEP 2: THINKING MODE SELECTION
    # --------------------------------------------------

    def _select_thinking_mode(self, cls: RequestClass, prompt: str) -> ThinkingMode:
        lowered = prompt.lower()
        if any(w in lowered for w in ["security", "hack", "vulnerability", "auth", "permission"]):
            return ThinkingMode.CRITICAL
        if any(w in lowered for w in ["business", "revenue", "monetize", "pricing", "growth"]):
            return ThinkingMode.STRATEGIC
        if any(w in lowered for w in ["design", "ux", "ui", "color", "brand", "logo"]):
            return ThinkingMode.CREATIVE
        if any(w in lowered for w in ["unknown", "research", "explore", "novel"]):
            return ThinkingMode.RESEARCH
        return self._MODE_MAP.get(cls, ThinkingMode.ANALYTICAL)

    # --------------------------------------------------
    # STEP 3: COMPLEXITY ESTIMATION
    # --------------------------------------------------

    def _estimate_complexity(self, prompt: str) -> ComplexityLevel:
        word_count = len(prompt.split())
        lowered = prompt.lower()

        if any(w in lowered for w in ["platform", "ecosystem", "enterprise", "saas"]):
            return ComplexityLevel.PLATFORM
        if any(w in lowered for w in ["marketplace", "erp", "crm", "multi-tenant"]):
            return ComplexityLevel.ENTERPRISE
        if word_count > 50:
            return ComplexityLevel.LARGE
        if word_count > 20:
            return ComplexityLevel.MEDIUM
        if any(w in lowered for w in ["fix", "bug", "typo", "rename"]):
            return ComplexityLevel.TINY
        return ComplexityLevel.SMALL

    # --------------------------------------------------
    # STEP 4: PROBLEM DECOMPOSITION
    # --------------------------------------------------

    def _decompose_problems(
        self,
        prompt: str,
        cls: RequestClass,
    ) -> Dict[ProblemCategory, str]:
        lowered = prompt.lower()
        decomposition: Dict[ProblemCategory, str] = {}

        decomposition[ProblemCategory.BUSINESS] = (
            f"Deliver '{prompt}' that creates measurable business value, "
            "aligns with revenue goals, and serves the target audience."
        )
        decomposition[ProblemCategory.TECHNICAL] = (
            f"Select the right technology stack and architecture for '{cls.value}'. "
            "Ensure the system is maintainable and extensible."
        )

        if any(w in lowered for w in ["user", "interface", "page", "design", "layout"]):
            decomposition[ProblemCategory.UX] = (
                "Design an intuitive, accessible interface that minimises cognitive load "
                "and drives user engagement."
            )

        if any(w in lowered for w in ["fast", "speed", "load", "performance", "latency"]):
            decomposition[ProblemCategory.PERFORMANCE] = (
                "Ensure response times < 200ms for API calls and < 2s for page loads. "
                "Implement caching and lazy loading where applicable."
            )

        if any(w in lowered for w in ["auth", "login", "payment", "user data", "secure"]):
            decomposition[ProblemCategory.SECURITY] = (
                "Enforce authentication, authorisation, input validation, "
                "HTTPS, rate limiting, and data encryption at rest."
            )

        if any(w in lowered for w in ["scale", "concurrent", "users", "traffic", "growth"]):
            decomposition[ProblemCategory.SCALABILITY] = (
                "Design for horizontal scaling. Use stateless services, "
                "database read replicas, and CDN distribution."
            )

        decomposition[ProblemCategory.OPERATIONAL] = (
            "Implement logging, monitoring, alerting, and automated deployment pipelines "
            "to ensure production reliability."
        )

        return decomposition

    # --------------------------------------------------
    # STEP 5: RISK ANALYSIS
    # --------------------------------------------------

    def _analyze_risks(
        self,
        prompt: str,
        problems: Dict[ProblemCategory, str],
        complexity: ComplexityLevel,
    ) -> List[str]:
        risks: List[str] = []
        lowered = prompt.lower()

        if ProblemCategory.SECURITY in problems:
            risks.append("SECURITY: Missing or weak authentication may expose user data.")
            risks.append("SECURITY: Unvalidated inputs could allow SQL injection or XSS.")

        if complexity in (ComplexityLevel.LARGE, ComplexityLevel.ENTERPRISE, ComplexityLevel.PLATFORM):
            risks.append("SCALABILITY: Monolithic design may bottleneck under high load.")
            risks.append("TECHNICAL: Scope creep risk — requirements may expand mid-delivery.")

        if "payment" in lowered or "billing" in lowered:
            risks.append("FINANCIAL: Payment provider failure could halt revenue operations.")
            risks.append("LEGAL: PCI-DSS compliance required for card data handling.")

        if "ai" in lowered or "llm" in lowered:
            risks.append("TECHNICAL: LLM API rate limits and token costs must be budgeted.")
            risks.append("SECURITY: Prompt injection attacks must be mitigated.")

        if "deploy" in lowered or "production" in lowered:
            risks.append("OPERATIONAL: Deployment failures without rollback strategy cause downtime.")

        if not risks:
            risks.append("LOW: Standard implementation risks — covered by QA and code review.")

        return risks

    # --------------------------------------------------
    # STEP 6: CANDIDATE SOLUTIONS (≥3 ALTERNATIVES)
    # --------------------------------------------------

    def _generate_candidates(
        self,
        prompt: str,
        cls: RequestClass,
        mode: ThinkingMode,
    ) -> List[CandidateSolution]:
        """
        Generate three architectural approaches: Minimal, Standard, Comprehensive.
        Scores are estimated heuristically; LLM refinement can override these.
        """
        minimal = CandidateSolution(
            title="Minimal Viable Approach",
            description=(
                f"Build the core '{cls.value}' with minimal dependencies. "
                "Fast to deliver, limited extensibility."
            ),
            score=DecisionScore(
                business_value=5.0, engineering_complexity=3.0, maintainability=5.0,
                performance=6.0, security=5.0, scalability=4.0,
                developer_experience=7.0, user_experience=5.0, operational_cost=3.0,
            ),
            risks=["Limited future extensibility.", "Technical debt accumulation."],
        )

        standard = CandidateSolution(
            title="Production-Grade Standard Approach",
            description=(
                f"Implement '{cls.value}' with a clean layered architecture, "
                "REST API, proper auth, tests, and CI/CD."
            ),
            score=DecisionScore(
                business_value=8.0, engineering_complexity=6.0, maintainability=8.0,
                performance=7.5, security=8.0, scalability=7.0,
                developer_experience=8.0, user_experience=8.0, operational_cost=5.0,
            ),
            risks=["Medium delivery time.", "Requires skilled engineering team."],
        )

        comprehensive = CandidateSolution(
            title="Enterprise-Scale Comprehensive Approach",
            description=(
                f"Full '{cls.value}' platform: microservices, event-driven architecture, "
                "multi-tenancy, observability stack, and auto-scaling."
            ),
            score=DecisionScore(
                business_value=10.0, engineering_complexity=9.0, maintainability=9.0,
                performance=9.5, security=9.5, scalability=10.0,
                developer_experience=7.0, user_experience=9.0, operational_cost=8.0,
            ),
            risks=[
                "High engineering cost and delivery time.",
                "Over-engineering risk for early-stage product.",
            ],
        )

        return [minimal, standard, comprehensive]

    def _select_best_candidate(
        self, candidates: List[CandidateSolution]
    ) -> CandidateSolution:
        return max(candidates, key=lambda c: c.score.overall)

    # --------------------------------------------------
    # STEP 7: SPECIALIST PARTS RESOLUTION
    # --------------------------------------------------

    def _resolve_required_parts(self, cls: RequestClass, prompt: str) -> List[int]:
        base = self._PARTS_MAP.get(cls, [13, 30, 32, 26, 24, 14, 28, 33])
        lowered = prompt.lower()

        # add extra specialists based on prompt keywords
        if "seo" in lowered and 36 not in base:
            base.append(36)
        if "marketing" in lowered and 37 not in base:
            base.append(37)
        if "logo" in lowered and 22 not in base:
            base.append(22)
        if "image" in lowered and 23 not in base:
            base.append(23)
        if "mobile" in lowered and 25 not in base:
            base.append(25)
        if "devops" in lowered and 27 not in base:
            base.append(27)

        # always keep sorted for deterministic ordering
        return sorted(set(base))

    # --------------------------------------------------
    # STEP 8: SELF-CRITIQUE → QUALITY SCORE
    # --------------------------------------------------

    def _self_critique(
        self,
        solution: CandidateSolution,
        risks: List[str],
        parts: List[int],
    ) -> QualityScore:
        s = solution.score
        q = QualityScore(
            correctness=min(10.0, s.business_value),
            completeness=min(10.0, len(parts) * 0.7),     # more specialists = more complete
            reliability=min(10.0, s.security * 0.9 + s.performance * 0.1),
            maintainability=s.maintainability,
            business_alignment=s.business_value,
            security=s.security,
        )

        # penalise for unmitigated high-severity risks
        critical_risks = [r for r in risks if r.startswith("SECURITY") or r.startswith("LEGAL")]
        q.security = max(0.0, q.security - len(critical_risks) * 0.5)

        return q

    # --------------------------------------------------
    # STEP 9: LEARNING / INSIGHT EXTRACTION
    # --------------------------------------------------

    def _extract_insights(
        self,
        prompt: str,
        solution: CandidateSolution,
        risks: List[str],
    ) -> List[str]:
        return [
            f"Selected approach: '{solution.title}' with confidence score "
            f"{solution.score.overall:.1f}.",
            f"Identified {len(risks)} risks that must be addressed during implementation.",
            "Recommendation: validate architecture with Solution Architect before coding.",
        ]

    # --------------------------------------------------
    # SYSTEM PROMPT LOADER (shared with agents)
    # --------------------------------------------------

    def load_system_prompt(self, part_number: int) -> str:
        if part_number in self._system_prompt_cache:
            return self._system_prompt_cache[part_number]
        try:
            root = settings.BASE_DIR.parent
            path = os.path.join(root, f"SYSTEM_PROMPT_PART_{part_number:02d}.md")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    self._system_prompt_cache[part_number] = content
                    return content
        except Exception as e:
            logger.warning(f"[ReasoningEngine] Could not load Part {part_number}: {e}")
        fallback = f"You are a world-class AI specialist (Part {part_number})."
        self._system_prompt_cache[part_number] = fallback
        return fallback
