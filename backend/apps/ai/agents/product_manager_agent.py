"""ProductManagerAgent — AI Product Manager (Part 30)."""
from ai.agents.base_agent import BaseAgent, AgentOutput

class ProductManagerAgent(BaseAgent):
    agent_id          = "product_manager_agent"
    system_prompt_part = 30
    task_type         = "copywriting_text"

    def run(self, context: dict, prompt: str) -> AgentOutput:
        reasoning = self.get_reasoning_context(context)
        sys_inst  = self.get_system_instruction() + reasoning
        user_msg  = (
            f"Create a product specification for: '{prompt}'.\n"
            "Include: product vision, user stories (as a / I want / so that), "
            "acceptance criteria, MVP feature list, and roadmap phases."
        )
        text, provider = self.call_llm(user_msg, sys_inst)
        return AgentOutput(
            agent_id=self.agent_id, success=True,
            data={"product_spec": text}, provider=provider,
            reasoning="Product specification generated.",
        )
