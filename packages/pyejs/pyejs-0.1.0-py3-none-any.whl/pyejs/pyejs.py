import re
from pathlib import Path

class TemplateError(Exception):
    pass

class TemplateVariableError(TemplateError):
    pass

class TemplateSyntaxError(TemplateError):
    pass

class Template:
    VAR_PATTERN = re.compile(r"<%=\s*(.*?)\s*%>")
    CODE_PATTERN = re.compile(r"<%(?!\=)(.*?)%>", re.DOTALL)

    def __init__(self, template_str):
        self.template_str = template_str

    def render(self, context):
        cursor = 0
        result = []

        for match in self.CODE_PATTERN.finditer(self.template_str):
            start, end = match.span()

            # Text before code block
            text_block = self.template_str[cursor:start]
            text_block = self._replace_vars(text_block, context)
            result.append(text_block)

            # Execute the Python code block
            code = match.group(1).strip()
            try:
                exec_result = self._exec_code(code, context)
                if exec_result:
                    result.append(exec_result)
            except Exception as e:
                raise TemplateSyntaxError(f"Error executing code block: {e}")

            cursor = end

        # Remaining text
        text_block = self.template_str[cursor:]
        text_block = self._replace_vars(text_block, context)
        result.append(text_block)

        return ''.join(result)

    def _replace_vars(self, text, context):
        def repl(match):
            expr = match.group(1).strip()
            try:
                return str(eval(expr, {}, context))
            except Exception as e:
                raise TemplateVariableError(f"Error evaluating expression '{expr}': {e}")
        return self.VAR_PATTERN.sub(repl, text)

    def _exec_code(self, code, context):
        local_context = dict(context)
        local_context["output"] = []
        try:
            exec(code, {}, local_context)
        except Exception as e:
            raise TemplateSyntaxError(f"{e}")
        return ''.join(local_context["output"])

    @classmethod
    def render_file(cls, file_path, context):
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Template file '{file_path}' not found")
        with open(path, "r", encoding="utf-8") as f:
            template_str = f.read()
        return cls(template_str).render(context)
