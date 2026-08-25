"""DjangoBackendAgent — Django Backend Specialist (Part 3)."""
from ai.agents.base_agent import BaseAgent, AgentOutput

class DjangoBackendAgent(BaseAgent):
    agent_id          = "django_backend_agent"
    system_prompt_part = 3
    task_type         = "backend_code"

    def run(self, context: dict, prompt: str) -> AgentOutput:
        reasoning = self.get_reasoning_context(context)
        sys_inst  = self.get_system_instruction() + reasoning
        user_msg  = f"Apply Django backend design rules and build server logic for: '{prompt}'."
        text, provider = self.call_llm(user_msg, sys_inst)
        return AgentOutput(
            agent_id=self.agent_id, success=True,
            data={"django_code": text}, provider=provider,
            reasoning="Django backend code rules generated.",
        )
