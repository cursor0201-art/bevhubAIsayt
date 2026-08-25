"""PlatformArchitectAgent — Platform Architect Specialist (Part 2)."""
from ai.agents.base_agent import BaseAgent, AgentOutput

class PlatformArchitectAgent(BaseAgent):
    agent_id          = "platform_architect_agent"
    system_prompt_part = 2
    task_type         = "copywriting_text"

    def run(self, context: dict, prompt: str) -> AgentOutput:
        reasoning = self.get_reasoning_context(context)
        sys_inst  = self.get_system_instruction() + reasoning
        user_msg  = f"Apply platform architecture principles and structures to: '{prompt}'."
        text, provider = self.call_llm(user_msg, sys_inst)
        return AgentOutput(
            agent_id=self.agent_id, success=True,
            data={"platform_architecture": text}, provider=provider,
            reasoning="Platform architecture guidelines generated.",
        )
