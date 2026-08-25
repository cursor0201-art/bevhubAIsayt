"""QAAgent — AI QA Engine (Part 28)."""
from ai.agents.base_agent import BaseAgent, AgentOutput

class QAAgent(BaseAgent):
    agent_id          = "qa_agent"
    system_prompt_part = 28
    task_type         = "layout_code_generation"

    def run(self, context: dict, prompt: str) -> AgentOutput:
        reasoning = self.get_reasoning_context(context)
        sys_inst  = self.get_system_instruction() + reasoning
        user_msg  = (
            f"Create a comprehensive test suite for: '{prompt}'.\n"
            "Include: unit tests (pytest), integration tests, E2E test scenarios, "
            "edge cases, and a test coverage plan."
        )
        text, provider = self.call_llm(user_msg, sys_inst)
        return AgentOutput(
            agent_id=self.agent_id, success=True,
            data={"test_suite": text}, provider=provider,
            reasoning="QA test suite generated.",
        )
