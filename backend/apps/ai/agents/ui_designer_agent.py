"""UIDesignerAgent — AI UI Designer (Part 35) & Website Builder Engine (Part 14)."""
import json
import logging
from typing import List
from pydantic import BaseModel, Field
from ai.agents.base_agent import BaseAgent, AgentOutput

logger = logging.getLogger(__name__)

class GeneratedPage(BaseModel):
    path: str = Field(description="The path of the file, e.g., 'src/pages/index.html', 'src/pages/products.html', 'src/pages/about.html', 'src/pages/contact.html'")
    title: str = Field(description="Title of the page, e.g., 'Home', 'Products', 'About Us', 'Contact'")
    html: str = Field(description="The complete, production-ready HTML code, styled using Tailwind CSS CDN, including modern visual components, copywriting context, and header/footer.")

class GeneratedWebsite(BaseModel):
    pages: List[GeneratedPage] = Field(description="List of all files to generate for the website")

class UIDesignerAgent(BaseAgent):
    agent_id          = "ui_designer_agent"
    system_prompt_part = 35
    task_type         = "layout_code_generation"

    def run(self, context: dict, prompt: str) -> AgentOutput:
        reasoning = self.get_reasoning_context(context)
        is_website_builder = hasattr(self, 'active_part_number') and self.active_part_number == 14
        
        sys_inst  = self.get_system_instruction() + reasoning

        if is_website_builder:
            ds = context.get("project", {}).get("design_system", {})
            copywriting = context.get("copywriting", {}).get("copy", "")
            
            user_msg = (
                f"You are the Website Builder Engine. Generate a fully-functional, multi-page website matching: '{prompt}'.\n"
                f"Design System:\n{json.dumps(ds)}\n"
                f"Copywriting context:\n{copywriting}\n\n"
                "Requirements:\n"
                "1. Generate multiple pages: Home (src/pages/index.html), Products/Services (src/pages/products.html), About Us (src/pages/about.html), and Contact Us (src/pages/contact.html).\n"
                "2. Every page must contain complete, high-quality, professional code. Do not use any placeholders, TODOs, comments like 'rest of page here', or generic text. Every paragraph, headline, button, and image placeholder must be contextual and high quality.\n"
                "3. Visual & Aesthetic Quality:\n"
                "   - CRITICAL: You MUST include `<script src=\"https://cdn.tailwindcss.com\"></script>` inside the `<head>` of EVERY page.\n"
                "   - CRITICAL: You MUST include `<link href=\"https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap\" rel=\"stylesheet\">` inside the `<head>` and apply `style=\"font-family: 'Outfit', sans-serif;\"` to the `<body>` tag.\n"
                "   - Deliver premium Vercel/Stripe/Apple-level design aesthetics with dark modes, harmonious color schemes, glassmorphism backdrop blurs, glowing text/gradients, and smooth hover micro-animations.\n"
                "   - Include essential sections: navigation headers, heroes, feature cards, testimonials, pricing, FAQ tabs, CTAs, and a detailed footer.\n"
                "4. Fluid Responsiveness & Layout Safety:\n"
                "   - Use mobile-first Tailwind design modifiers (sm:, md:, lg:, xl:).\n"
                "   - Enforce wrapper elements with max-w-full and overflow-x-hidden to fully prevent horizontal scrolling.\n"
                "5. High-Performance and Clean Code:\n"
                "   - Lazy load images using loading=\"lazy\" on all <img> tags and specify width/height properties.\n"
                "   - Keep codebase clean, satisfying SOLID principles and clean organization.\n"
                "6. Strict Accessibility (WCAG):\n"
                "   - Every image must have a descriptive, contextual 'alt' tag.\n"
                "   - Every interactive element (inputs, buttons) must contain a clear, descriptive 'aria-label' or associated label tag.\n"
                "   - Use correct semantic elements: <header>, <main>, <footer>, <nav>, <section>, <article>.\n"
                "7. Advanced SEO optimization:\n"
                "   - Every page MUST contain: a descriptive <title> tag, a <meta name=\"description\"> snippet, OpenGraph meta tags (og:title, og:description, og:image), Twitter Card properties, and structured JSON-LD schema metadata.\n"
                "8. Safety and CSP compliance:\n"
                "   - Do NOT use inline JS event handlers (like onclick=\"...\"). Write clean JS script elements using addEventListener instead.\n"
                "9. Return the pages strictly conforming to the response schema."
            )
            
            try:
                provider_name = self.router.select_best_provider_for_task(self.task_type)
                provider = self.router.get_provider(provider_name)
                result = provider.generate_text(
                    prompt=user_msg,
                    system_instruction=sys_inst,
                    response_schema=GeneratedWebsite
                )
                
                parsed = json.loads(result.text)
                return AgentOutput(
                    agent_id=self.agent_id, success=True,
                    data={"website": parsed}, provider=provider_name,
                    reasoning="Dynamic multi-page website files generated.",
                )
            except Exception as e:
                logger.error(f"Failed to generate structured website in UIDesignerAgent: {e}")
                return AgentOutput(
                    agent_id=self.agent_id, success=False,
                    error=str(e), reasoning="Structured website generation failed."
                )
        else:
            # Standard UI Spec Generation (Part 35)
            user_msg  = (
                f"Design the complete UI specification for: '{prompt}'.\n"
                "Include: layout grid, spacing system, color tokens, typography scale, "
                "component library list, and responsive breakpoints."
            )
            text, provider = self.call_llm(user_msg, sys_inst)
            return AgentOutput(
                agent_id=self.agent_id, success=True,
                data={"ui_spec": text}, provider=provider,
                reasoning="UI specification generated.",
            )
