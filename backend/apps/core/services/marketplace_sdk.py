import importlib
import logging

logger = logging.getLogger(__name__)

class MarketplaceSDK:
    """
    Marketplace SDK Registry.
    Enables third-party developers to register custom:
    - AI Workers
    - Template Packs
    - Theme Packs
    - Deployment Providers
    - Billing Providers
    - Validators
    - Context Providers
    - Model Adapters
    
    Loads modules dynamically without modifying core orchestrator files.
    """
    _registry = {
        "workers": {},
        "templates": {},
        "themes": {},
        "deployment_providers": {},
        "billing_providers": {},
        "validators": {},
        "context_providers": {},
        "model_adapters": {}
    }

    @classmethod
    def register_extension(cls, extension_type: str, name: str, class_path: str, metadata: dict = None):
        """
        Registers a third-party plugin extension class.
        """
        if extension_type not in cls._registry:
            raise ValueError(f"Unknown extension type: {extension_type}. Available: {list(cls._registry.keys())}")
        
        cls._registry[extension_type][name] = {
            "class_path": class_path,
            "metadata": metadata or {}
        }
        logger.info(f"Extension '{name}' registered under '{extension_type}'")

    @classmethod
    def get_extension(cls, extension_type: str, name: str):
        """
        Dynamically imports and returns the plugin class.
        """
        if extension_type not in cls._registry or name not in cls._registry[extension_type]:
            return None
        
        config = cls._registry[extension_type][name]
        class_path = config["class_path"]
        
        try:
            module_name, class_name = class_path.rsplit(".", 1)
            module = importlib.import_module(module_name)
            return getattr(module, class_name)
        except Exception as e:
            logger.error(f"Failed to load extension {name} from path {class_path}: {str(e)}")
            return None

    @classmethod
    def list_extensions(cls, extension_type: str = None):
        """
        Returns registered plugins.
        """
        if extension_type:
            return cls._registry.get(extension_type, {})
        return cls._registry


# Pre-register default built-in core provider engines for compatibility
MarketplaceSDK.register_extension(
    extension_type="model_adapters",
    name="anthropic",
    class_path="core.services.ai_router.AIRouterService",
    metadata={"provider": "Anthropic", "supported_models": ["claude-3-5-sonnet"]}
)

MarketplaceSDK.register_extension(
    extension_type="deployment_providers",
    name="vercel",
    class_path="ai.agents.devops_agent.DevOpsDeploymentAgent",
    metadata={"provider": "Vercel", "region": "global-edge"}
)
