# PyEJS

**A Python template engine inspired by EJS**  
Render dynamic HTML using `<%= variable %>` for data and `<% code %>` for logic like loops and conditionals.

---

## ✨ Features

- Variable interpolation: `<%= variable %>`  
- Code blocks: `<% code %>` (loops, conditionals, etc.)  
- Render templates from strings or files  
- Simple and lightweight  
- Custom error handling for missing variables or syntax errors

---

## ⚙️ Installation

```bash
git clone https://github.com/your-username/pyejs.git
cd pyejs
🚀 Usage
🔹 Render from string
from pyejs import Template

template = """
<h1>Hello, <%= user %>!</h1>
<ul>
<% 
for item in items:
    output.append(f"  <li>{item}</li>\\n")
%>
</ul>
"""

context = {
    "user": "Alice",
    "items": ["Apple", "Banana", "Cherry"]
}

t = Template(template)
html = t.render(context)
print(html)

🔹 Render from file
from pyejs import Template

html = Template.render_file("templates/my_template.html", context)
print(html)

⚠️ Error Handling

TemplateVariableError → Raised if a variable is missing in context

TemplateSyntaxError → Raised for invalid code blocks

🛠️ Roadmap

✅ Variable interpolation <%= %>

✅ Code blocks <% %>

⚡ Support if-else and nested loops

⚡ Template includes <% include %>

⚡ CLI tool for rendering templates from terminal

🤝 Contributing

Contributions are welcome!
Feel free to submit issues, feature requests, or pull requests
# Optional: install in your environment
pip install .
