"""SolutionArchitectAgent — AI Solution Architect (Part 32)."""
from ai.agents.base_agent import BaseAgent, AgentOutput

class SolutionArchitectAgent(BaseAgent):
    agent_id          = "solution_architect_agent"
    system_prompt_part = 32
    task_type         = "layout_code_generation"

    def run(self, context: dict, prompt: str) -> AgentOutput:
        reasoning = self.get_reasoning_context(context)
        sys_inst  = self.get_system_instruction() + reasoning
        user_msg  = (
            f"Design the complete system architecture for: '{prompt}'.\n"
            "Include: component diagram, technology stack decision matrix, "
            "API contract summary, data flow, and scaling strategy."
        )
        text, provider = self.call_llm(user_msg, sys_inst)
        return AgentOutput(
            agent_id=self.agent_id, success=True,
            data={"architecture": text}, provider=provider,
            reasoning="Solution architecture designed.",
        )
