import os
from dotenv import load_dotenv
from am_tools import read_file, write_file, mkdir, list_files
from smolagents import CodeAgent, WebSearchTool
from smolagents.models import OpenAIServerModel
from template_generator import generate_app_from_template
from app_spec import AppSpec

# Load environment variables from .env file
load_dotenv()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    """Generate React app using template-based approach with smolagents."""
    
    # Create app specification
    app_spec = AppSpec(
        app_name="task-manager-app",
        display_name="Task Manager",
        description="A modern React task management application with localStorage persistence",
        author="VibeCoder",
        template_name="react-simple-spa",
        output_dir="result",
        custom_content='''<h1 className="text-4xl font-bold">Task Manager</h1>
      <p className="text-lg text-gray-600 mb-8">Organize your tasks efficiently</p>
      <Button>Get Started</Button>''',
        features=["localStorage", "responsive", "dark-mode"]
    )

    # Initialize CodeAgent with template generator tool
    agent = CodeAgent(
        tools=[
            # Template generation
            generate_app_from_template,
            # File system operations
            read_file, 
            write_file, 
            list_files, 
            mkdir
        ],
        model=OpenAIServerModel("gpt-5"),
        stream_outputs=False,
        additional_authorized_imports=["subprocess", "shutil", "json", "re"],
    )

    # Create the prompt for the agent
    prompt = f"""
Generate a React application using the template system with the following specifications:

App Name: {app_spec.app_name}
Display Name: {app_spec.display_name}
Description: {app_spec.description}
Template: {app_spec.template_name}
Output Directory: {app_spec.output_dir}
Custom Content: {app_spec.custom_content}

Use the generate_app_from_template tool with these parameters to create the base application:
- app_name: "{app_spec.app_name}"
- display_name: "{app_spec.display_name}"
- description: "{app_spec.description}"
- author: "{app_spec.author}"
- template_name: "{app_spec.template_name}"
- output_dir: "{app_spec.output_dir}"
- custom_content: "{app_spec.custom_content}"

After generation, you may enhance the application with additional features as needed.

The generated app should be a complete, working React application that can be run with:
cd {app_spec.output_dir}/{app_spec.app_name} && npm install && npm run dev
"""

    print(f"🚀 Generating React app: {app_spec.display_name}")
    print(f"📍 Output location: {app_spec.output_dir}/{app_spec.app_name}")
    
    # Run the agent
    try:
        result = agent.run(prompt)
        print("✅ App generation completed!")
        print(f"🎯 Your app is ready in: {app_spec.output_dir}/{app_spec.app_name}")
        print(f"🏃 To run: cd {app_spec.output_dir}/{app_spec.app_name} && npm install && npm run dev")
        return result
    except Exception as e:
        print(f"❌ Error during app generation: {e}")
        return None


if __name__ == "__main__":
    main()