"""SecurityAgent — AI Security Engine (Part 29)."""
from ai.agents.base_agent import BaseAgent, AgentOutput

class SecurityAgent(BaseAgent):
    agent_id          = "security_agent"
    system_prompt_part = 29
    task_type         = "layout_code_generation"

    def run(self, context: dict, prompt: str) -> AgentOutput:
        reasoning = self.get_reasoning_context(context)
        sys_inst  = self.get_system_instruction() + reasoning
        user_msg  = (
            f"Perform a security audit plan for: '{prompt}'.\n"
            "Cover: authentication flow, authorisation matrix, "
            "input validation, OWASP Top 10 checklist, "
            "secrets management, and rate-limiting strategy."
        )
        text, provider = self.call_llm(user_msg, sys_inst)
        return AgentOutput(
            agent_id=self.agent_id, success=True,
            data={"security_audit": text}, provider=provider,
            reasoning="Security audit plan generated.",
        )
