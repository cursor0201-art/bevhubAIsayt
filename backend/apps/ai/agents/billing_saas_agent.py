"""BillingSaaSAgent — SaaS Billing and Subscription Specialist (Part 12)."""
from ai.agents.base_agent import BaseAgent, AgentOutput

class BillingSaaSAgent(BaseAgent):
    agent_id          = "billing_saas_agent"
    system_prompt_part = 12
    task_type         = "billing_rules"

    def run(self, context: dict, prompt: str) -> AgentOutput:
        reasoning = self.get_reasoning_context(context)
        sys_inst  = self.get_system_instruction() + reasoning
        user_msg  = f"Apply SaaS pricing tiers and Stripe checkout guidelines for: '{prompt}'."
        text, provider = self.call_llm(user_msg, sys_inst)
        return AgentOutput(
            agent_id=self.agent_id, success=True,
            data={"billing_strategy": text}, provider=provider,
            reasoning="SaaS billing structures and subscription tiers guidelines generated.",
        )
