"""CodeStudioAgent — AI Code Studio Engine (Part 24)."""
from ai.agents.base_agent import BaseAgent, AgentOutput

class CodeStudioAgent(BaseAgent):
    agent_id          = "code_studio_agent"
    system_prompt_part = 24
    task_type         = "layout_code_generation"

    def run(self, context: dict, prompt: str) -> AgentOutput:
        reasoning = self.get_reasoning_context(context)
        sys_inst  = self.get_system_instruction() + reasoning
        user_msg  = (
            f"Generate complete, production-ready backend code for: '{prompt}'.\n"
            "Include: API endpoints, service layer, data models, "
            "validation, error handling, and docstrings."
        )
        text, provider = self.call_llm(user_msg, sys_inst)
        return AgentOutput(
            agent_id=self.agent_id, success=True,
            data={"code": text}, provider=provider,
            reasoning="Backend code generated.",
        )
