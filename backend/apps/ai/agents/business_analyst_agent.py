"""BusinessAnalystAgent — AI Business Analyst (Part 31)."""
from ai.agents.base_agent import BaseAgent, AgentOutput

class BusinessAnalystAgent(BaseAgent):
    agent_id          = "business_analyst_agent"
    system_prompt_part = 31
    task_type         = "copywriting_text"

    def run(self, context: dict, prompt: str) -> AgentOutput:
        reasoning = self.get_reasoning_context(context)
        sys_inst  = self.get_system_instruction() + reasoning
        user_msg  = (
            f"Produce a business analysis for: '{prompt}'.\n"
            "Include: target market, value proposition, revenue model, "
            "competitive landscape, SWOT analysis, and go-to-market strategy."
        )
        text, provider = self.call_llm(user_msg, sys_inst)
        return AgentOutput(
            agent_id=self.agent_id, success=True,
            data={"business_analysis": text}, provider=provider,
            reasoning="Business analysis generated.",
        )
