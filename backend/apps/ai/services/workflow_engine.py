import logging
from typing import Dict, Any
from core.domain.models import Project, User
from ai.services.context_engine import ContextEngine
from ai.services.credit_service import CreditService
from ai.agents.branding_agent import BrandingAgent
from ai.agents.copywriting_agent import CopywritingAgent
from ai.agents.seo_agent import SEOAgent

logger = logging.getLogger(__name__)

class WorkflowEngine:
    """
    Orchestrates the multi-agent pipeline: gathers context, runs credit audits, 
    triggers specialized agents, and compiles output parameters.
    """
    def __init__(self):
        self.branding_agent = BrandingAgent()
        self.copywriting_agent = CopywritingAgent()
        self.seo_agent = SEOAgent()

    def execute_business_generation_workflow(self, project: Project, user: User, prompt: str) -> Dict[str, Any]:
        logger.info(f"Starting Multi-Agent Workflow for Project: {project.id}")

        # 1. Assemble complete context package
        context = ContextEngine.get_generation_context(project, user)

        # 2. Check estimated costs (estimated at 3 transactions, ~1.0 credit total)
        estimated_credits = CreditService.calculate_cost("openai", 1000, 1000) * 3
        if not CreditService.has_sufficient_credits(project.tenant, estimated_credits):
            raise ValueError("Insufficient AI credits in Tenant account to run generation workflow.")

        # 3. Trigger branding agent (designs color scheme and font choices)
        branding_results = self.branding_agent.run(context, prompt)
        
        # Log branding agent usage (approx 500 input, 100 output tokens)
        CreditService.record_usage(
            tenant=project.tenant,
            provider="openai",
            input_tokens=500,
            output_tokens=100,
            task_desc="Branding Agent Style Design"
        )

        # Update context memory
        context["project"]["design_system"] = branding_results["design_system"]

        # 4. Trigger copywriting agent (generates conversion text copy)
        copy_results = self.copywriting_agent.run(context, prompt)
        
        # Log copywriting agent usage (approx 600 input, 300 output tokens)
        CreditService.record_usage(
            tenant=project.tenant,
            provider="deepseek",
            input_tokens=600,
            output_tokens=300,
            task_desc="Copywriting Agent Section Generation"
        )

        # 5. Trigger SEO agent (optimizes meta titles and sitemap elements)
        seo_results = self.seo_agent.run(context, prompt)
        
        # Log SEO agent usage (approx 400 input, 150 output tokens)
        CreditService.record_usage(
            tenant=project.tenant,
            provider="openai",
            input_tokens=400,
            output_tokens=150,
            task_desc="SEO Agent Meta Tags Optimization"
        )

        # 6. Merge outputs
        compiled_results = {
            "design_system": branding_results["design_system"],
            "copy": copy_results["copy"],
            "seo": seo_results["seo"]
        }

        logger.info(f"Multi-Agent Workflow complete for Project: {project.id}")
        return compiled_results
