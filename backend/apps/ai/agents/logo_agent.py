"""LogoAgent — AI Logo & Brand Identity Engine (Part 22)."""
from ai.agents.base_agent import BaseAgent, AgentOutput

class LogoAgent(BaseAgent):
    agent_id          = "logo_agent"
    system_prompt_part = 22
    task_type         = "image_generation"

    def run(self, context: dict, prompt: str) -> AgentOutput:
        sys_inst = self.get_system_instruction()
        logo_prompt = (
            f"Professional minimalist logo for '{prompt}'. "
            f"Clean vector style, bold typography, transparent background. "
            f"Specifications: {sys_inst[:200]}"
        )
        provider_name = self.router.select_best_provider_for_task(self.task_type)
        provider = self.router.get_provider(provider_name)
        result = provider.generate_image(prompt=logo_prompt)
        return AgentOutput(
            agent_id=self.agent_id, success=True,
            data={"logo_url": result.image_url}, provider=provider_name,
            reasoning="Logo design prompt submitted to image generator.",
        )
