"""CacheCeleryAgent — Redis Cache and Celery Task Specialist (Part 6)."""
from ai.agents.base_agent import BaseAgent, AgentOutput

class CacheCeleryAgent(BaseAgent):
    agent_id          = "cache_celery_agent"
    system_prompt_part = 6
    task_type         = "backend_code"

    def run(self, context: dict, prompt: str) -> AgentOutput:
        reasoning = self.get_reasoning_context(context)
        sys_inst  = self.get_system_instruction() + reasoning
        user_msg  = f"Apply Redis caching and background Celery task specifications for: '{prompt}'."
        text, provider = self.call_llm(user_msg, sys_inst)
        return AgentOutput(
            agent_id=self.agent_id, success=True,
            data={"cache_celery_config": text}, provider=provider,
            reasoning="Redis & Celery asynchronous tasks configurations generated.",
        )
