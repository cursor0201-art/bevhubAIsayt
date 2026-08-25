"""DevOpsAgent — AI DevOps Engine (Part 27)."""
from ai.agents.base_agent import BaseAgent, AgentOutput

class DevOpsAgent(BaseAgent):
    agent_id          = "devops_agent"
    system_prompt_part = 27
    task_type         = "layout_code_generation"

    def run(self, context: dict, prompt: str) -> AgentOutput:
        reasoning = self.get_reasoning_context(context)
        sys_inst  = self.get_system_instruction() + reasoning
        user_msg  = (
            f"Create a complete DevOps configuration for: '{prompt}'.\n"
            "Include: Dockerfile, docker-compose.yml, GitHub Actions CI/CD pipeline, "
            "Nginx config, and environment variable template."
        )
        text, provider = self.call_llm(user_msg, sys_inst)
        return AgentOutput(
            agent_id=self.agent_id, success=True,
            data={"devops_config": text}, provider=provider,
            reasoning="DevOps configuration generated.",
        )
