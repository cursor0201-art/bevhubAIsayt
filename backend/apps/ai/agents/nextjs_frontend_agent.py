"""NextjsFrontendAgent — Next.js Frontend Specialist (Part 4)."""
from ai.agents.base_agent import BaseAgent, AgentOutput

class NextjsFrontendAgent(BaseAgent):
    agent_id          = "nextjs_frontend_agent"
    system_prompt_part = 4
    task_type         = "frontend_code"

    def run(self, context: dict, prompt: str) -> AgentOutput:
        reasoning = self.get_reasoning_context(context)
        sys_inst  = self.get_system_instruction() + reasoning
        user_msg  = f"Apply Next.js and React frontend architecture standards for: '{prompt}'."
        text, provider = self.call_llm(user_msg, sys_inst)
        return AgentOutput(
            agent_id=self.agent_id, success=True,
            data={"nextjs_frontend": text}, provider=provider,
            reasoning="Next.js frontend design architecture generated.",
        )
