# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VibeCoder is an AI-powered application generator that creates React Single Page Applications (SPAs) using smolagents and OpenAI's CodeAgent. The system generates modern React applications with Vite, TailwindCSS, and Shadcn UI components that use localStorage for data persistence.

## Architecture

### Core Components

- **main.py** - Entry point for the generator; configures prompt templates and runs the CodeAgent
- **generate_app.py** - Main generator logic using smolagents framework with OpenAI GPT-5 model
- **am_tools.py** - Custom file system tools for the CodeAgent (read_file, write_file, list_files, mkdir)
- **templates/react-simple-spa/** - React template with Vite, TailwindCSS, Shadcn UI, and TypeScript

### Technology Stack

- **Backend**: Python 3.13+ with smolagents framework
- **Frontend Template**: React 19, Vite, TailwindCSS v4, Shadcn UI, TypeScript
- **Package Management**: uv (Python), pnpm (Node.js)
- **AI Model**: OpenAI GPT-5 via smolagents

## Development Commands

### Python Environment
```bash
# Run the main application
uv run main.py

# Run the generator directly
uv run generate_app.py

# Install Python dependencies
uv add <package_name>
```

### React Template Development
```bash
# Navigate to template directory
cd templates/react-simple-spa/

# Install dependencies
pnpm install

# Start development server
pnpm dev

# Build for production
pnpm build

# Run linter
pnpm lint

# Preview production build
pnpm preview
```

## File Structure

```
VibeCoder/
├── main.py                    # Entry point
├── generate_app.py           # Generator implementation
├── am_tools.py              # Custom file system tools
├── pyproject.toml           # Python dependencies
├── templates/
│   └── react-simple-spa/    # React template
│       ├── src/
│       │   ├── App.tsx      # Main application component
│       │   ├── components/ui/ # Shadcn UI components
│       │   └── lib/         # Utilities
│       ├── package.json     # Node dependencies
│       └── vite.config.ts   # Vite configuration
└── result/                  # Generated applications output
```

## Code Generation Workflow

1. **Template Configuration**: Modify variables in `generate_app.py` or `main.py`
2. **Prompt Rendering**: System uses Jinja2 templates for prompt generation
3. **CodeAgent Execution**: smolagents CodeAgent generates React application
4. **File Operations**: Uses custom tools from `am_tools.py` for secure file system access
5. **Output**: Generated app appears in `result/` directory

## Security Features

The custom file tools in `am_tools.py` include security measures:
- Path traversal protection
- Current directory containment
- File type validation
- Secure path resolution

## Template Customization

The React template includes:
- Functional React components with hooks
- Responsive design with TailwindCSS
- Dark/light theme capability
- LocalStorage integration
- Shadcn UI component library
- TypeScript for type safety

## Dependencies

- **Python**: smolagents, OpenAI API client
- **Node.js**: React 19, Vite 7, TailwindCSS 4, TypeScript 5.8
- **Development**: ESLint, TypeScript compiler

## Notes

- Uses OpenAI GPT-5 model for code generation
- All generated apps are self-contained SPAs
- No backend API required for generated applications
- Template uses modern React patterns and latest package versions