from core.domain.models import Project, User
from ai.models import ProjectMemory, UserMemory

class ContextEngine:
    """
    Assembles user, workspace, and historical project settings to build a rich context package.
    """
    @staticmethod
    def get_generation_context(project: Project, user: User) -> dict:
        # Retrieve or provision project memory
        project_memory, _ = ProjectMemory.objects.get_or_create(
            project=project,
            defaults={
                'preferred_language': 'English',
                'brand_voice': 'Modern & Professional'
            }
        )

        # Retrieve user preference profiles
        user_memory, _ = UserMemory.objects.get_or_create(
            user=user,
            defaults={
                'writing_style': 'Professional',
                'preferred_language': 'English'
            }
        )

        return {
            "project": {
                "name": project.project_name,
                "subdomain": project.subdomain,
                "custom_domain": project.custom_domain,
                "design_system": project.design_system,
            },
            "memory": {
                "industry": project_memory.industry,
                "target_audience": project_memory.target_audience,
                "brand_voice": project_memory.brand_voice,
                "preferred_language": project_memory.preferred_language,
                "products": project_memory.products_metadata,
                "user_preferences": project_memory.user_preferences,
            },
            "user": {
                "writing_style": user_memory.writing_style,
                "preferred_language": user_memory.preferred_language,
            }
        }

    @classmethod
    def format_context_prompt_header(cls, project: Project, user: User) -> str:
        ctx = cls.get_generation_context(project, user)
        
        return (
            f"=== BUSINESS BRAND PROFILE ===\n"
            f"Name: {ctx['project']['name']}\n"
            f"Industry: {ctx['memory']['industry'] or 'Not Specified'}\n"
            f"Target Audience: {ctx['memory']['target_audience'] or 'General Public'}\n"
            f"Brand Tone: {ctx['memory']['brand_voice'] or 'Professional'}\n"
            f"Language: {ctx['memory']['preferred_language']}\n"
            f"Writing Style: {ctx['user']['writing_style']}\n"
            f"=== DESIGN GUIDELINES ===\n"
            f"Style Colors & CSS Theme Variables: {ctx['project']['design_system']}\n"
            f"================================\n"
        )
