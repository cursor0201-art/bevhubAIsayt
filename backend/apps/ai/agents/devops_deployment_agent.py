"""DevOpsDeploymentAgent — DevOps & Deployment Specialist (Part 9)."""
from ai.agents.base_agent import BaseAgent, AgentOutput

class DevOpsDeploymentAgent(BaseAgent):
    agent_id          = "devops_deployment_agent"
    system_prompt_part = 9
    task_type         = "devops_config"

    def run(self, context: dict, prompt: str) -> AgentOutput:
        reasoning = self.get_reasoning_context(context)
        sys_inst  = self.get_system_instruction() + reasoning
        user_msg  = f"Apply DevOps deployment scripts and Docker/Kubernetes rules to: '{prompt}'."
        text, provider = self.call_llm(user_msg, sys_inst)
        return AgentOutput(
            agent_id=self.agent_id, success=True,
            data={"deployment_config": text}, provider=provider,
            reasoning="DevOps deployment configurations compiled.",
        )
