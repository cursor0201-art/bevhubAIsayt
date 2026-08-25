"""SaaSGeneratorAgent — AI SaaS Generator Engine (Part 15)."""
from ai.agents.base_agent import BaseAgent, AgentOutput

class SaaSGeneratorAgent(BaseAgent):
    agent_id          = "saas_generator_agent"
    system_prompt_part = 15
    task_type         = "copywriting_text"

    def run(self, context: dict, prompt: str) -> AgentOutput:
        reasoning = self.get_reasoning_context(context)
        sys_inst  = self.get_system_instruction() + reasoning
        user_msg  = f"Apply SaaS generator configuration pipelines to: '{prompt}'."
        text, provider = self.call_llm(user_msg, sys_inst)
        return AgentOutput(
            agent_id=self.agent_id, success=True,
            data={"saas_config": text}, provider=provider,
            reasoning="AI SaaS generator engine components configured.",
        )
