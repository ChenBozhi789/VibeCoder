We want to create an app generator that creates simple SPA React Apps that use localStorage to store data. How can we generate the source files in a way that we can use a package.json and some sort of compiler or linter stage?

The resulting files should run in a browser without a backend api component. Please create a directory called `templates/` that contains a `simple` react app with localStorage. Try to keep the HTML file minial and use an external CSS file linked from the HTML file. We want to make is easiy for an LLM to make edits or changesto a specific part of either file.

Can we use tailwindcss, shadcn, and vite to simplify the workflow? Can we include a linter step so if the linter fails, we can provide feedback to the LLM to have another go at generating code? We also want to be able to run unit tests and use the failures to provide feedback to the LLM so it can regenerate code and fix the errors.

We'll be doing this with smolagents.


---


Let's create a smolagent tool that creates an app from a template. How might this work? Please use the `context7` tool to find documentation for smolagents and their tools.

Do we need to parameterize our template in `templates/react-simple-spa`?


After we create our app, how can we iterate on it and change it? What is the best way to enable an agent to edit files without burning through tokens?

Then ultrathink about how to implement this and write your plan to a file like `plans/2025_08_21_plan_name.md`
