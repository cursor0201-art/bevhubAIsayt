"""SEOAgent — AI SEO Expert (Part 36)."""
from ai.agents.base_agent import BaseAgent, AgentOutput

class SEOAgent(BaseAgent):
    agent_id          = "seo_agent"
    system_prompt_part = 36
    task_type         = "copywriting_text"

    def run(self, context: dict, prompt: str) -> AgentOutput:
        reasoning = self.get_reasoning_context(context)
        sys_inst  = self.get_system_instruction() + reasoning
        user_msg  = (
            f"Generate a complete SEO strategy for: '{prompt}'.\n"
            "Include: title tag, meta description, H1, 10 target keywords, "
            "schema markup type, and internal linking recommendations."
        )
        text, provider = self.call_llm(user_msg, sys_inst)
        return AgentOutput(
            agent_id=self.agent_id, success=True,
            data={"seo_strategy": text}, provider=provider,
            reasoning="SEO strategy generated.",
        )
