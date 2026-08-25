"""CTOAgent — AI CTO (Part 33)."""
from ai.agents.base_agent import BaseAgent, AgentOutput

class CTOAgent(BaseAgent):
    agent_id          = "cto_agent"
    system_prompt_part = 33
    task_type         = "layout_code_generation"

    def run(self, context: dict, prompt: str) -> AgentOutput:
        reasoning = self.get_reasoning_context(context)
        sys_inst  = self.get_system_instruction() + reasoning
        user_msg  = (
            f"As CTO, review and approve the technical strategy for: '{prompt}'.\n"
            "Provide: technology standards sign-off, risk assessment, "
            "build-vs-buy decisions, team structure recommendation, "
            "and 90-day technical roadmap."
        )
        text, provider = self.call_llm(user_msg, sys_inst)
        return AgentOutput(
            agent_id=self.agent_id, success=True,
            data={"cto_review": text}, provider=provider,
            reasoning="CTO review and approval generated.",
        )
