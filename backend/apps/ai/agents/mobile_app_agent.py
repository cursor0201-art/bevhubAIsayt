"""MobileAppAgent — AI Mobile App Generator (Part 25)."""
from ai.agents.base_agent import BaseAgent, AgentOutput

class MobileAppAgent(BaseAgent):
    agent_id          = "mobile_app_agent"
    system_prompt_part = 25
    task_type         = "layout_code_generation"

    def run(self, context: dict, prompt: str) -> AgentOutput:
        reasoning = self.get_reasoning_context(context)
        sys_inst  = self.get_system_instruction() + reasoning
        user_msg  = (
            f"Design mobile app screens and navigation for: '{prompt}'.\n"
            "Include: screen list, navigation structure, key components, "
            "and React Native/Expo code scaffold."
        )
        text, provider = self.call_llm(user_msg, sys_inst)
        return AgentOutput(
            agent_id=self.agent_id, success=True,
            data={"mobile_layout": text}, provider=provider,
            reasoning="Mobile app layout generated.",
        )
