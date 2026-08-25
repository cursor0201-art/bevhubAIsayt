"""DatabaseDesignerAgent — AI Database Designer (Part 26)."""
from ai.agents.base_agent import BaseAgent, AgentOutput

class DatabaseDesignerAgent(BaseAgent):
    agent_id          = "database_designer_agent"
    system_prompt_part = 26
    task_type         = "layout_code_generation"

    def run(self, context: dict, prompt: str) -> AgentOutput:
        reasoning = self.get_reasoning_context(context)
        sys_inst  = self.get_system_instruction() + reasoning
        user_msg  = (
            f"Design a production PostgreSQL schema for: '{prompt}'.\n"
            "Include: CREATE TABLE statements, indexes, foreign keys, "
            "constraints, and an ER diagram description."
        )
        text, provider = self.call_llm(user_msg, sys_inst)
        return AgentOutput(
            agent_id=self.agent_id, success=True,
            data={"ddl_schema": text}, provider=provider,
            reasoning="Database schema designed.",
        )
