"""BrandingAgent — Design System Bible (Part 18)."""
import json
from ai.agents.base_agent import BaseAgent, AgentOutput

class BrandingAgent(BaseAgent):
    agent_id          = "branding_agent"
    system_prompt_part = 18
    task_type         = "layout_code_generation"

    def run(self, context: dict, prompt: str) -> AgentOutput:
        reasoning = self.get_reasoning_context(context)
        sys_inst  = self.get_system_instruction() + reasoning
        user_msg  = (
            f"Generate a design system for: '{prompt}'.\n"
            "Return JSON with keys: font_family, border_radius, "
            "primary_color, secondary_color, background_color."
        )
        text, provider = self.call_llm(user_msg, sys_inst)
        try:
            ds = json.loads(text)
        except Exception:
            ds = {
                "font_family":      "Outfit, sans-serif",
                "border_radius":    "0.75rem",
                "primary_color":    "#8b5cf6",
                "secondary_color":  "#d946ef",
                "background_color": "#030303",
            }
        return AgentOutput(
            agent_id=self.agent_id, success=True,
            data={"design_system": ds}, provider=provider,
            reasoning=f"Design system generated for: {prompt}",
        )
