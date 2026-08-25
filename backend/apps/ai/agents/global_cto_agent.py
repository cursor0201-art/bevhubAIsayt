"""GlobalCTOAgent — Global CTO Prompt Specialist (Part 1)."""
from ai.agents.base_agent import BaseAgent, AgentOutput

class GlobalCTOAgent(BaseAgent):
    agent_id          = "global_cto_agent"
    system_prompt_part = 1
    task_type         = "copywriting_text"

    def run(self, context: dict, prompt: str) -> AgentOutput:
        reasoning = self.get_reasoning_context(context)
        sys_inst  = self.get_system_instruction() + reasoning
        user_msg  = f"Execute high level CTO strategy and platform planning guidelines for: '{prompt}'."
        text, provider = self.call_llm(user_msg, sys_inst)
        return AgentOutput(
            agent_id=self.agent_id, success=True,
            data={"cto_strategy": text}, provider=provider,
            reasoning="High level CTO strategy and guidelines compiled.",
        )
