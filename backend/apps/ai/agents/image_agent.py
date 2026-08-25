"""ImageAgent — AI Image Studio (Part 23)."""
from ai.agents.base_agent import BaseAgent, AgentOutput

class ImageAgent(BaseAgent):
    agent_id          = "image_agent"
    system_prompt_part = 23
    task_type         = "image_generation"

    def run(self, context: dict, prompt: str) -> AgentOutput:
        image_prompt = (
            f"Hero banner image for '{prompt}'. "
            "Ultra-wide format, professional photography, cinematic lighting, "
            "suitable for web hero section."
        )
        provider_name = self.router.select_best_provider_for_task(self.task_type)
        provider = self.router.get_provider(provider_name)
        result = provider.generate_image(prompt=image_prompt, size="1792x1024")
        return AgentOutput(
            agent_id=self.agent_id, success=True,
            data={"image_url": result.image_url}, provider=provider_name,
            reasoning="Hero image prompt submitted.",
        )
