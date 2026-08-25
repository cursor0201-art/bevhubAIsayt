"""AnalyticsAgent — Analytics & Telemetry Specialist (Part 16)."""
from ai.agents.base_agent import BaseAgent, AgentOutput

class AnalyticsAgent(BaseAgent):
    agent_id          = "analytics_agent"
    system_prompt_part = 16
    task_type         = "copywriting_text"

    def run(self, context: dict, prompt: str) -> AgentOutput:
        reasoning = self.get_reasoning_context(context)
        sys_inst  = self.get_system_instruction() + reasoning
        user_msg  = f"Apply business analytics trackers, page view logs, and conversions telemetry to: '{prompt}'."
        text, provider = self.call_llm(user_msg, sys_inst)
        return AgentOutput(
            agent_id=self.agent_id, success=True,
            data={"analytics_setup": text}, provider=provider,
            reasoning="Analytics event tracking system configured.",
        )
