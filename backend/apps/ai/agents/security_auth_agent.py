"""SecurityAuthAgent — Security and OAuth2 Specialist (Part 8)."""
from ai.agents.base_agent import BaseAgent, AgentOutput

class SecurityAuthAgent(BaseAgent):
    agent_id          = "security_auth_agent"
    system_prompt_part = 8
    task_type         = "security_rules"

    def run(self, context: dict, prompt: str) -> AgentOutput:
        reasoning = self.get_reasoning_context(context)
        sys_inst  = self.get_system_instruction() + reasoning
        user_msg  = f"Apply OAuth2, token signing and password encryption rules to: '{prompt}'."
        text, provider = self.call_llm(user_msg, sys_inst)
        return AgentOutput(
            agent_id=self.agent_id, success=True,
            data={"security_auth_rules": text}, provider=provider,
            reasoning="Security authentication and encryption guidelines generated.",
        )
