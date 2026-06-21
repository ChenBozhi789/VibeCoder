"""
Prompt loader module for VibeCoder agents.
Loads prompts from Jinja2 template files in prompts/agents/ directory.
"""
from pathlib import Path
from typing import Dict, Optional
from jinja2 import Environment, FileSystemLoader, Template


class PromptLoader:
    """Loads and manages prompts for different agents from .j2 template files."""
    
    def __init__(self, templates_dir: Optional[Path] = None):
        """
        Initialize the prompt loader.
        
        Args:
            templates_dir: Directory containing .j2 template files. 
                          Defaults to prompts/agents/ relative to this file.
        """
        if templates_dir is None:
            # Get the directory where this file is located
            current_dir = Path(__file__).parent
            templates_dir = current_dir / "prompts" / "agents"
        
        self.templates_dir = Path(templates_dir)
        
        # Ensure templates directory exists
        if not self.templates_dir.exists():
            raise FileNotFoundError(
                f"Templates directory not found: {self.templates_dir}. "
                f"Please ensure the prompts/agents/ directory exists with .j2 template files."
            )
        
        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False  # We're generating prompts, not HTML
        )
        
        # Cache for loaded templates
        self._template_cache: Dict[str, Template] = {}
    
    def load_agent_prompt(self, agent_name: str, **kwargs) -> str:
        """
        Load a prompt for a specific agent from a .j2 template file.
        
        Args:
            agent_name: Name of the agent (e.g., "prd_agent", "ui_agent")
                       The corresponding template file should be {agent_name}.j2
            **kwargs: Optional variables to pass to the Jinja2 template
        
        Returns:
            The rendered prompt string for the agent
            
        Raises:
            FileNotFoundError: If the template file doesn't exist
            TemplateError: If there's an error rendering the template
        """
        template_file = f"{agent_name}.j2"
        
        # Check if template is in cache
        if agent_name not in self._template_cache:
            try:
                template = self.env.get_template(template_file)
                self._template_cache[agent_name] = template
            except Exception as e:
                raise FileNotFoundError(
                    f"Template file not found: {self.templates_dir / template_file}. "
                    f"Error: {e}"
                )
        else:
            template = self._template_cache[agent_name]
        
        # Render the template with any provided variables
        try:
            return template.render(**kwargs)
        except Exception as e:
            raise RuntimeError(
                f"Error rendering template for {agent_name}: {e}"
            )
    
    def list_agents(self) -> list:
        """
        List all available agent template files.
        
        Returns:
            List of agent names (without .j2 extension)
        """
        if not self.templates_dir.exists():
            return []
        
        agents = []
        for template_file in self.templates_dir.glob("*.j2"):
            agent_name = template_file.stem  # filename without extension
            agents.append(agent_name)
        
        return sorted(agents)
    
    def template_exists(self, agent_name: str) -> bool:
        """
        Check if a template file exists for an agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            True if template exists, False otherwise
        """
        template_file = self.templates_dir / f"{agent_name}.j2"
        return template_file.exists() and template_file.is_file()


# Create a singleton instance
prompt_loader = PromptLoader()
