"""TailwindDesignAgent — Tailwind CSS Specialist (Part 5)."""
from ai.agents.base_agent import BaseAgent, AgentOutput

class TailwindDesignAgent(BaseAgent):
    agent_id          = "tailwind_design_agent"
    system_prompt_part = 5
    task_type         = "design_style"

    def run(self, context: dict, prompt: str) -> AgentOutput:
        reasoning = self.get_reasoning_context(context)
        sys_inst  = self.get_system_instruction() + reasoning
        user_msg  = f"Formulate Tailwind CSS styling specifications for: '{prompt}'."
        text, provider = self.call_llm(user_msg, sys_inst)
        return AgentOutput(
            agent_id=self.agent_id, success=True,
            data={"tailwind_style": text}, provider=provider,
            reasoning="Tailwind CSS design guidelines generated.",
        )
