"""UXResearcherAgent — AI UX Researcher (Part 34)."""
from ai.agents.base_agent import BaseAgent, AgentOutput

class UXResearcherAgent(BaseAgent):
    agent_id          = "ux_researcher_agent"
    system_prompt_part = 34
    task_type         = "copywriting_text"

    def run(self, context: dict, prompt: str) -> AgentOutput:
        reasoning = self.get_reasoning_context(context)
        sys_inst  = self.get_system_instruction() + reasoning
        user_msg  = (
            f"Conduct UX research planning for: '{prompt}'.\n"
            "Include: user personas (3), jobs-to-be-done, pain points, "
            "user journey map, accessibility requirements, and usability heuristics checklist."
        )
        text, provider = self.call_llm(user_msg, sys_inst)
        return AgentOutput(
            agent_id=self.agent_id, success=True,
            data={"ux_research": text}, provider=provider,
            reasoning="UX research plan generated.",
        )
