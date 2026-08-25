"""NotificationAgent — Notification System Specialist (Part 17)."""
from ai.agents.base_agent import BaseAgent, AgentOutput

class NotificationAgent(BaseAgent):
    agent_id          = "notification_agent"
    system_prompt_part = 17
    task_type         = "copywriting_text"

    def run(self, context: dict, prompt: str) -> AgentOutput:
        reasoning = self.get_reasoning_context(context)
        sys_inst  = self.get_system_instruction() + reasoning
        user_msg  = f"Configure emails, SMS and websocket live notifications templates for: '{prompt}'."
        text, provider = self.call_llm(user_msg, sys_inst)
        return AgentOutput(
            agent_id=self.agent_id, success=True,
            data={"notifications_rules": text}, provider=provider,
            reasoning="Asynchronous notification system channels registered.",
        )
