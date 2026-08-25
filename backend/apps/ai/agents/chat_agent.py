"""ChatAgent — AI Chat Engine Bible (Part 21)."""
from ai.agents.base_agent import BaseAgent, AgentOutput

class ChatAgent(BaseAgent):
    agent_id          = "chat_agent"
    system_prompt_part = 21
    task_type         = "general_chat"

    def run(self, context: dict, prompt: str) -> AgentOutput:
        reasoning = self.get_reasoning_context(context)
        sys_inst  = self.get_system_instruction() + reasoning
        text, provider = self.call_llm(prompt, sys_inst)
        return AgentOutput(
            agent_id=self.agent_id, success=True,
            data={"response": text}, provider=provider,
            reasoning="Chat response generated.",
        )
