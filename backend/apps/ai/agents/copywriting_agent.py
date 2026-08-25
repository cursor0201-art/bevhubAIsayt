"""CopywritingAgent — AI Marketing Strategist (Part 37)."""
from ai.agents.base_agent import BaseAgent, AgentOutput

class CopywritingAgent(BaseAgent):
    agent_id          = "copywriting_agent"
    system_prompt_part = 37
    task_type         = "copywriting_text"

    def run(self, context: dict, prompt: str) -> AgentOutput:
        reasoning = self.get_reasoning_context(context)
        sys_inst  = self.get_system_instruction() + reasoning
        user_msg  = (
            f"Write compelling marketing copy for: '{prompt}'.\n"
            "Include: headline, subheadline, hero paragraph, CTA text, "
            "and 3 feature highlights."
        )
        text, provider = self.call_llm(user_msg, sys_inst)
        return AgentOutput(
            agent_id=self.agent_id, success=True,
            data={"copy": text}, provider=provider,
            reasoning="Marketing copy generated.",
        )
