"""
generate_prompt.py
Scans a generated React SPA and writes an enhancement prompt (.j2) for your agent.

Usage examples:
  python generate_prompt.py --app result/my-app -p baseline --change-budget 8
  python generate_prompt.py --app result/my-app --goal "add dark mode and a README"
"""

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List

# -----------------------------
# Step 1: Utilities (helpers)

# What: tiny helpers for reading/writing files safely.
# Why: keep the rest of the code clean and focused.
# -----------------------------

def read_json(path: Path) -> Dict:
    """
    What it does: Reads a JSON file (like package.json) and returns it as a Python dictionary.

    Why: The script needs to know dependencies, scripts, etc.

    Failsafe: If the file can't be read, it just returns {} instead of crashing.
    """
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def file_exists(root: Path, *parts: str) -> bool:
    return (root.joinpath(*parts)).exists()

def read_text_safe(p: Path, limit: int = 3000) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")[:limit]
    except Exception:
        return ""

def ensure_parent_written(path: Path, text: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return str(path)

# -----------------------------
# Step 2: Scanner (collect facts about the app)

# What: build a small “snapshot” of the project.
# Why: the rule engine needs facts to decide what tasks to add.
# -----------------------------
def scan_app(app_path: Path) -> Dict:
    """
    Scans a project directory and builds a snapshot of key information.

    - Reads package.json to extract dependencies, devDependencies, and scripts.
    - Detects whether TypeScript is used (by checking tsconfig.json or .ts/.tsx files).
    - Flags the presence of common tools (Tailwind, ESLint, Prettier, Vitest, Router, shadcn).
    - Collects existing entry files (main.tsx/jsx, App.tsx/jsx, index.html).
    - Performs a heuristic check on App.tsx/jsx to detect default starter content (e.g., "Hello Vite").
    - Returns a dictionary summarizing project path, name, scripts, dependencies, flags, entry files, and findings.
    """
    # Load dependencies, devDependencies, scripts
    pkg = read_json(app_path / "package.json")
    deps = pkg.get("dependencies", {}) or {}
    dev_deps = pkg.get("devDependencies", {}) or {}
    scripts = pkg.get("scripts", {}) or {}

    has_tsconfig = file_exists(app_path, "tsconfig.json")
    has_ts_files = any(
        p.suffix in (".ts", ".tsx")
        for p in (app_path / "src").rglob("*")
    ) if (app_path / "src").exists() else False

    flags = {
        "has_typescript": has_tsconfig or has_ts_files,
        "has_tailwind": file_exists(app_path, "tailwind.config.js") or file_exists(app_path, "tailwind.config.ts"),
        # "has_eslint": any(file_exists(app_path, n) for n in [".eslintrc", ".eslintrc.js", ".eslintrc.cjs", ".eslintrc.json"]),
        "has_eslint": any(file_exists(app_path, n) for n in [
            ".eslintrc", ".eslintrc.js", ".eslintrc.cjs", ".eslintrc.json", 
            "eslint.config.js", "eslint.config.cjs", "eslint.config.mjs", "eslint.config.ts"
        ]) or ("eslintConfig" in read_json(app_path / "package.json")),
        "has_prettier": any(file_exists(app_path, n) for n in [".prettierrc", ".prettierrc.json", "prettier.config.js", "prettier.config.cjs"]),
        "has_vitest": "vitest" in {**deps, **dev_deps},
        "has_test_script": "test" in scripts or "vitest" in scripts.get("test", ""),
        "has_router": "react-router-dom" in deps,
        # 
        "has_shadcn": any("shadcn" in k.lower() for k in list(deps.keys()) + list(dev_deps.keys())), 
    }

    entry_files = [p for p in ["src/main.tsx","src/main.jsx","src/App.tsx","src/App.jsx","index.html"]
                   if file_exists(app_path, p)]

    # Heuristic: detect a starter hero → suggest UI polish
    # Store "special circumstances" that are discovered during scanning
    findings = []
    app_tsx = app_path / "src" / "App.tsx"
    app_jsx = app_path / "src" / "App.jsx"
    app_file = app_tsx if app_tsx.exists() else app_jsx if app_jsx.exists() else None
    if app_file:
        txt = read_text_safe(app_file)
        if re.search(r"\b(Hello|Vite|React|Welcome|Getting Started)\b", txt, re.I):
            findings.append("default_hero_detected")

    # Return the project snapshot
    return {
        "app_path": str(app_path),
        "package_name": (pkg.get("name") or Path(app_path).name),
        "scripts": scripts,
        "deps": deps,
        "dev_deps": dev_deps,
        "flags": flags,
        "entry_files": entry_files,
        "findings": findings,
    }


# -----------------------------
# Step 3 - Rule engine (turn facts into tasks)

# What you get: a deterministic list of tasks your agent should do. No LLM here.
# -----------------------------
def pick_tasks(ctx: Dict, goal: str, profile: str, allow_new_deps: bool) -> List[Dict]:
    f = ctx["flags"]
    # Initialize empty task list
    # Type hint
    tasks: List[Dict] = []

    def add(id, title, actions, why, severity="info"):
        tasks.append({"id": id, "title": title, "actions": actions, "why": why, "severity": severity})

    # Baseline quality
    if not f["has_eslint"]:
        add("eslint.setup",
            "Add ESLint (TypeScript + React)",
            ["Create .eslintrc.* with recommended React+TS rules", "Add npm scripts: lint, lint:fix"],
            "Consistent code quality and fewer future bugs.",
            "warning"
        )

    # Prettier
    if not f["has_prettier"]:
        add("prettier.setup",
            "Add Prettier formatting",
            ["Add Prettier config and scripts: format, format:check", "Ensure ESLint + Prettier integration"],
            "Keeps diffs small and readable."
        )

    # Tests
    if not f["has_vitest"]:
        add("vitest.setup",
            "Add Vitest + a sample test",
            ["Create one example test in src/, wire npm script: test"],
            "Guardrail for future changes."
        )

    # README
    if not file_exists(Path(ctx["app_path"]), "README.md"):
        add("docs.readme",
            "Create README.md",
            ["Document scripts (dev, build, preview, lint, test)", "Quickstart + tech stack + folder structure"],
            "Every app needs a minimal README."
        )

    # Tailwind sanity
    if f["has_tailwind"]:
        add("tailwind.verify",
            "Verify Tailwind v4 content globs and base styles",
            ["content = ['index.html','src/**/*.{ts,tsx,js,jsx}']", "Import base styles in main entry"],
            "Avoid missing classes/bloated CSS.","perf"
        )

    # UI polish
    if "default_hero_detected" in ctx["findings"]:
        add("ui.polish_hero",
            "Polish the landing hero",
            ["Replace the placeholder hero with a full-width section including: H1 'Welcome to Tester App', subheading text, and a CTA button. Use semantic HTML with accessible contrast.", 
             "Accessible headings/contrast; optional dark mode toggle"],
            "First impressions matter.","a11y"
        )

    # Router perf
    if f["has_router"]:
        add("router.split",
            "Route-based code splitting",
            ["Use React.lazy/Suspense for heavy routes", "Dynamic import large components"],
            "Improves initial load.","perf"
        )

    # Goal keywords
    g = goal.lower()
    if "readme" in g:
        add("docs.readme_goal",
            "Enhance README details",
            ["Add sections: Tech Stack, Scripts, Known Issues"],
            "Requested in goal."
        )
    if "dark" in g:
        add("ui.dark_mode_goal",
            "Implement dark mode",
            ["Add theme state + toggle; persist in localStorage"],
            "Requested in goal."
        )
    if "test" in g:
        add("testing.goal",
            "Add more tests",
            ["Add at least one unit test and wire CI script"],
            "Requested in goal."
        )
    if any(k in g for k in ["eslint","format","prettier"]):
        add("lint.goal",
            "Ensure lint/format",
            ["Run lint + format; fix obvious issues"],
            "Requested in goal."
        )

    # Profiles
    # Profile represents the "mode" or "scenario" in which the user is currently running.
    # 想象你生成的 app，有不同的用途：
    # baseline → 基础模式，只做最基本的检查（eslint、prettier、readme …）。
    # demo → 演示模式，可能需要更炫的 UI（比如自动加暗黑模式）。
    # ui_polish → 界面美化模式，也要加 UI 改进（暗黑模式、hero 页面优化）。
    # testing → 测试模式，自动加更多测试任务。
    profile = (profile or "baseline").lower()
    if profile in ("ui_polish","demo"):
        add("ui.dark_mode_toggle",
            "Add a dark mode toggle",
            ["Persist theme in localStorage", "Toggle 'class' on <html> for Tailwind dark:"],
            "Better demo experience with minimal changes."
        )
    if profile in ("testing",):
        add("testing.more",
            "Strengthen test setup",
            ["Add react-testing-library baseline test for <App/>"],
            "Catches regressions."
        )

    # De-duplicate by id
    seen, deduped = set(), []
    for t in tasks:
        if t["id"] in seen:
            continue
        seen.add(t["id"])
        deduped.append(t)
    return deduped


# -----------------------------
# Step 4 - Render a single enhancement prompt (text)
# What this is: the to-do list your agent will follow later.
# -----------------------------
PROMPT_HEADER = """You are an expert React engineer enhancing an existing SPA.
You must return ONE <code>...</code> block of executable Python that uses ONLY:
read_file, write_file, list_files, mkdir. Use ASCII only.
For long text (e.g., README), build with parentheses or "\\n".join(...).
End with: print('DONE').
"""

def render_prompt(ctx: Dict, tasks: List[Dict], change_budget: int, allow_new_deps: bool) -> str:
    f = ctx["flags"]
    # bullets = string
    bullets = [
        f"App path: {ctx['app_path']}",
        f"Package name: {ctx['package_name']}",
        f"Has TypeScript: {f['has_typescript']}",
        f"Tailwind: {f['has_tailwind']}",
        f"ESLint: {f['has_eslint']}",
        f"Prettier: {f['has_prettier']}",
        f"Vitest present: {f['has_vitest']}",
        f"Router: {f['has_router']}",
        f"Shadcn: {f['has_shadcn']}",
        f"Entry files: {', '.join(ctx['entry_files']) or 'n/a'}",
    ]

    out = [PROMPT_HEADER]
    out.append("## Project Snapshot")
    out += [f"- {b}" for b in bullets]

    out.append("\n## Rules")
    out.append(f"- Max files to change: {change_budget}")
    out.append("- Installing new dependencies is allowed if truly necessary." if allow_new_deps
               else "- Do NOT add or install new dependencies.")
    out.append("- Keep edits minimal; prefer small patches over rewrites.")
    out.append("- Maintain TypeScript correctness if TS is present.")
    out.append("- Follow WCAG 2.1 AA accessibility criteria:")
    out.append("  - Provide alt text for all images.")
    out.append("  - Use semantic headings (<h1>, <h2>, etc.) in order.")
    out.append("  - Ensure text/background contrast ratio ≥ 4.5:1.")
    out.append("  - Ensure all interactive elements (buttons, links) are keyboard accessible.")
    out.append("  - Provide labels for all form inputs.")
    out.append("  - Use ARIA roles/states where needed (e.g., aria-pressed for toggles).")
    out.append("- Output must use only plain ASCII characters (no smart quotes, em-dash, etc.)")
    out.append("- Always output complete, syntactically correct code. Do not truncate.")

    # out.append("- If requirements are unclear or ambiguous, do not make assumptions.")
    # out.append("- Instead of producing a patch, respond with:")
    
    # out.append("\n## Clarification Needed")
    # out.append("[One or two specific questions asking for the missing details]")

    out.append("\n## Tasks (do these in order)")

    if not tasks:
        out.append("- Nothing critical detected. Perform a light pass: ensure README and a quick code polish.")
    else:
        for i, t in enumerate(tasks, 1):
            out.append(f"### [{i}] {t['title']} ({t['id']})")
            out.append(f"- Why: {t['why']}")
            out.append("- Actions:")
            for a in t["actions"]:
                out.append(f"  - {a}")

    out.append("\n## Deliverables")
    out.append("- A short summary of what changed.")
    out.append("- A list of files you modified or created.")
    out.append("- Keep diffs small; only modify lines directly needed for the change. Do not adjust indentation, comments, or imports unless strictly necessary")

    # Enforce output format
    out.append("\n## Output Format")
    out.append("- DO NOT import anything. Use only the provided tools: read_file, write_file, list_files, mkdir.")
    out.append("- If you think you need os/pathlib/sys/subprocess/shutil/etc, you do not. Rewrite to use the tools.")
    out.append("You have EXACTLY ONE step.")
    out.append("Respond with ONE and ONLY ONE <code>...</code> block, with NO text before or after.")
    out.append("If you want to show a summary, PRINT it inside the code, then print('DONE') and STOP.")
    out.append("EVERY message you produce MUST follow this; never answer with plain text.")
    out.append("For long strings, build with parentheses or '\\n'.join([...]); use ASCII only.")
    out.append("")
    out.append("Example (skeleton):")
    out.append("<code>")
    out.append("# use only: read_file, write_file, list_files, mkdir, run_npm")
    out.append("txt = read_file('README.md') if True else ''")
    out.append("write_file('README.md', (txt.rstrip() + '\\n\\nAdded by agent.\\n'))")
    out.append("print('Summary: updated README.md')")
    out.append("print('DONE')")
    out.append("</code>")
    out.append("After printing the final summary and print('DONE'), stop.")


    return "\n".join(out) + "\n"

# -----------------------------
# Step 5 - CLI / Orchestrator (glue everything)
# What it does: parses args → runs scanner → runs rules → renders prompt → saves to <app>/prompts/enhancement_prompt.j2.
# -----------------------------
def main():    
    ap = argparse.ArgumentParser(description="Generate an enhancement prompt (.j2) for an existing React SPA")
    ap.add_argument("--app", required=True, help="Path to the app folder (where package.json lives)")
    ap.add_argument("--goal", default="", help="Optional goal, e.g. 'add dark mode and README'")
    ap.add_argument("-p", "--profile", default="baseline", help="baseline | ui_polish | testing | demo")
    ap.add_argument("--change-budget", type=int, default=8, help="Max number of files to modify")
    ap.add_argument("--allow-new-deps", action="store_true", help="Allow installing new deps if needed")
    ap.add_argument("--out", default="prompts/enhancement_prompt.j2", help="Relative path INSIDE app to write the prompt")

    args = ap.parse_args()

    app_path = Path(args.app).resolve()
    if not (app_path / "package.json").exists():
        raise SystemExit(f"[Error] No package.json found at: {app_path}")

    ctx = scan_app(app_path) # Step 2 - scan
    tasks = pick_tasks(ctx, goal=args.goal, profile=args.profile, allow_new_deps=args.allow_new_deps) # Step 3 - rules
    prompt_text = render_prompt(ctx, tasks, change_budget=args.change_budget, allow_new_deps=args.allow_new_deps) # Step 4 - render

    saved = ensure_parent_written(app_path / args.out, prompt_text) # Step 1 - write

    print("Enhancement prompt generated.")
    print(f"- Saved to: {saved}")
    print(f"- Scripts detected: {', '.join(ctx['scripts'].keys()) or 'none'}")
    print(f"- Tasks selected: {len(tasks)}")

if __name__ == "__main__":
    main()

# -----------------------------
# Step 6 - Run it (quick test)
# -----------------------------

# After you’ve generated an app into result/my-app
# py .\generate_prompt.py --app .\result\tester-app -p baseline --change-budget 8
