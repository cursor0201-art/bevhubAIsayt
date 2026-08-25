"""QACDAgent — QA and CI/CD Pipeline Specialist (Part 10)."""
from ai.agents.base_agent import BaseAgent, AgentOutput

class QACDAgent(BaseAgent):
    agent_id          = "qa_cd_agent"
    system_prompt_part = 10
    task_type         = "test_code"

    def run(self, context: dict, prompt: str) -> AgentOutput:
        reasoning = self.get_reasoning_context(context)
        sys_inst  = self.get_system_instruction() + reasoning
        user_msg  = f"Formulate testing suites and CI/CD quality assurance rules for: '{prompt}'."
        text, provider = self.call_llm(user_msg, sys_inst)
        return AgentOutput(
            agent_id=self.agent_id, success=True,
            data={"qa_cd_rules": text}, provider=provider,
            reasoning="Testing suite rules and quality assurance guidelines generated.",
        )
