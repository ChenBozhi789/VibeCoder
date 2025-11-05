"""
Template loader utility for agent prompts using Jinja2.
"""
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import os


class PromptTemplateLoader:
    """Load and render Jinja2 templates for agent prompts."""
    
    def __init__(self, templates_dir: str = "prompts"):
        """
        Initialize the template loader.
        
        Args:
            templates_dir: Path to the templates directory
        """
        self.templates_dir = Path(templates_dir).resolve()
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def load_agent_prompt(self, agent_name: str, **kwargs) -> str:
        """
        Load and render an agent prompt template.
        
        Args:
            agent_name: Name of the agent (e.g., 'prd_agent', 'spec_agent')
            **kwargs: Template variables
            
        Returns:
            Rendered prompt string
        """
        template_path = f"agents/{agent_name}.j2"
        try:
            template = self.env.get_template(template_path)
            return template.render(**kwargs)
        except Exception as e:
            raise FileNotFoundError(f"Could not load template {template_path}: {e}")
    
    def list_available_templates(self) -> list:
        """List all available agent templates."""
        agents_dir = self.templates_dir / "agents"
        if not agents_dir.exists():
            return []
        
        templates = []
        for file in agents_dir.glob("*.j2"):
            templates.append(file.stem)
        return sorted(templates)


# Global instance
prompt_loader = PromptTemplateLoader()
