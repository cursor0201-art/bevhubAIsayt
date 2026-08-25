"""PostgresDatabaseAgent — PostgreSQL Database Specialist (Part 7)."""
from ai.agents.base_agent import BaseAgent, AgentOutput

class PostgresDatabaseAgent(BaseAgent):
    agent_id          = "postgres_database_agent"
    system_prompt_part = 7
    task_type         = "database_schema"

    def run(self, context: dict, prompt: str) -> AgentOutput:
        reasoning = self.get_reasoning_context(context)
        sys_inst  = self.get_system_instruction() + reasoning
        user_msg  = f"Apply PostgreSQL design rules and query performance rules for: '{prompt}'."
        text, provider = self.call_llm(user_msg, sys_inst)
        return AgentOutput(
            agent_id=self.agent_id, success=True,
            data={"postgres_design": text}, provider=provider,
            reasoning="Postgres database constraints and index rules generated.",
        )
