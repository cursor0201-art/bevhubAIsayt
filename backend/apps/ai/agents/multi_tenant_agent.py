"""MultiTenantAgent — Multi-Tenant Architecture Specialist (Part 20)."""
from ai.agents.base_agent import BaseAgent, AgentOutput

class MultiTenantAgent(BaseAgent):
    agent_id          = "multi_tenant_agent"
    system_prompt_part = 20
    task_type         = "database_schema"

    def run(self, context: dict, prompt: str) -> AgentOutput:
        reasoning = self.get_reasoning_context(context)
        sys_inst  = self.get_system_instruction() + reasoning
        user_msg  = f"Apply multi-tenancy rules and data isolation policies to: '{prompt}'."
        text, provider = self.call_llm(user_msg, sys_inst)
        return AgentOutput(
            agent_id=self.agent_id, success=True,
            data={"multi_tenancy_setup": text}, provider=provider,
            reasoning="Multi-tenant schema scope isolation rules generated.",
        )
