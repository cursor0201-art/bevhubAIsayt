"""LandingPageAgent — Landing Page Builder Specialist (Part 19)."""
from ai.agents.base_agent import BaseAgent, AgentOutput

class LandingPageAgent(BaseAgent):
    agent_id          = "landing_page_agent"
    system_prompt_part = 19
    task_type         = "frontend_code"

    def run(self, context: dict, prompt: str) -> AgentOutput:
        reasoning = self.get_reasoning_context(context)
        sys_inst  = self.get_system_instruction() + reasoning
        user_msg  = f"Apply landing page layout elements and conversion optimization to: '{prompt}'."
        text, provider = self.call_llm(user_msg, sys_inst)
        return AgentOutput(
            agent_id=self.agent_id, success=True,
            data={"landing_page_layout": text}, provider=provider,
            reasoning="Landing page layouts structures generated.",
        )
