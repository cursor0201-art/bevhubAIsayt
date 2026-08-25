"""I18nAgent — Internationalization and Localization Specialist (Part 11)."""
from ai.agents.base_agent import BaseAgent, AgentOutput

class I18nAgent(BaseAgent):
    agent_id          = "i18n_agent"
    system_prompt_part = 11
    task_type         = "copywriting_text"

    def run(self, context: dict, prompt: str) -> AgentOutput:
        reasoning = self.get_reasoning_context(context)
        sys_inst  = self.get_system_instruction() + reasoning
        user_msg  = f"Apply internationalization (i18n) and localization standards for: '{prompt}'."
        text, provider = self.call_llm(user_msg, sys_inst)
        return AgentOutput(
            agent_id=self.agent_id, success=True,
            data={"i18n_locales": text}, provider=provider,
            reasoning="Internationalization standards and translation configurations generated.",
        )
