import os
from pathlib import Path
from typing import List, Optional
from jinja2 import Environment, FileSystemLoader, Template


class PromptManager:
    """Manages Jinja2 prompt templates for VibeCoder app generation."""
    
    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize the prompt manager with Jinja2 environment.
        
        Args:
            templates_dir: Custom templates directory path. If None, uses prompts/templates/
        """
        if templates_dir is None:
            # Get the directory where this file is located
            current_dir = Path(__file__).parent
            templates_dir = current_dir / "templates"
        
        self.templates_dir = Path(templates_dir)
        
        # Ensure templates directory exists
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False  # We're generating code, not HTML
        )
    
    def render_template(self, template_name: str, **kwargs) -> str:
        """
        Render a Jinja2 template with provided variables.
        
        Args:
            template_name: Name of the template file (e.g., 'main_prompt.j2')
            **kwargs: Variables to pass to the template
            
        Returns:
            Rendered template as string
        """
        template = self.env.get_template(template_name)
        return template.render(**kwargs)
    
    def render_main_prompt(
        self, 
        app_name: str,
        app_description: str,
        additional_requirements: Optional[List[str]] = None,
        tech_stack: Optional[str] = None,
        feature_name: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Render the main application generation prompt.
        
        Args:
            app_name: Name of the application to generate
            app_description: Description of what the app should do
            additional_requirements: List of additional requirements
            tech_stack: Technology stack description
            feature_name: Main feature name
            **kwargs: Additional template variables
            
        Returns:
            Rendered prompt ready for CodeAgent
        """
        template_vars = {
            'app_name': app_name,
            'app_description': app_description,
            'additional_requirements': additional_requirements or [],
            'tech_stack': tech_stack or "React 19, Vite, TailwindCSS v4, Shadcn UI, TypeScript",
            'feature_name': feature_name or app_name.replace('-', ' ').replace('_', ' ').title(),
            **kwargs
        }
        
        return self.render_template('main_prompt.j2', **template_vars)
    
    def list_templates(self) -> List[str]:
        """
        List all available template files.
        
        Returns:
            List of template filenames
        """
        if not self.templates_dir.exists():
            return []
        
        return [
            f.name for f in self.templates_dir.iterdir() 
            if f.is_file() and f.suffix in ['.j2', '.jinja', '.jinja2']
        ]
    
    def template_exists(self, template_name: str) -> bool:
        """
        Check if a template file exists.
        
        Args:
            template_name: Name of the template file
            
        Returns:
            True if template exists, False otherwise
        """
        template_path = self.templates_dir / template_name
        return template_path.exists() and template_path.is_file()


if __name__ == "__main__":
    # Example usage
    pm = PromptManager()
    
    # Example template rendering
    try:
        prompt = pm.render_main_prompt(
            app_name="todo-app",
            app_description="A modern todo management application",
            additional_requirements=[
                "Use functional React components",
                "Implement responsive design",
                "Include dark/light theme toggle"
            ]
        )
        print("Generated prompt:")
        print(prompt)
    except Exception as e:
        print(f"Template not found: {e}")
        print(f"Available templates: {pm.list_templates()}")