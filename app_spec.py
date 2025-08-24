from pydantic import BaseModel
from typing import Optional, List


class AppSpec(BaseModel):
    """Specification for generating React app from template."""
    
    # Basic app information
    app_name: str                    # "my-todo-app" (kebab-case, used for directory/package name)
    display_name: str               # "My Todo App" (human-readable title)
    description: str                # "A simple todo management application"
    
    # Optional metadata
    author: Optional[str] = None    # "John Doe"
    version: Optional[str] = "0.1.0"
    
    # Template selection
    template_name: str = "react-simple-spa"  # Template to use from templates/ directory
    
    # Output configuration
    output_dir: str = "result"      # Where to generate the app
    
    # Custom content (used by editing tools)
    custom_content: Optional[str] = None     # Custom JSX content for App.tsx
    features: List[str] = []                 # ["localStorage", "dark-mode"] - for future use

    class Config:
        # Example for documentation
        schema_extra = {
            "example": {
                "app_name": "task-manager",
                "display_name": "Task Manager",
                "description": "A modern task management application with localStorage",
                "author": "Developer",
                "template_name": "react-simple-spa",
                "output_dir": "result",
                "custom_content": "<h1>Welcome to Task Manager</h1>",
                "features": ["localStorage"]
            }
        }


if __name__ == "__main__":
    # Example usage
    app_spec = AppSpec(
        app_name="todo-app",
        display_name="Todo App", 
        description="A simple todo management application",
        author="Developer"
    )
    
    print("AppSpec created successfully:")
    print(app_spec.model_dump_json(indent=2))