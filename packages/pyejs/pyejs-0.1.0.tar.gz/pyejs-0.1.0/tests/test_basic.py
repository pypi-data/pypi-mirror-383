from pyejs import Template

def test_basic_render():
    template = "<h1>Hello, <%= name %></h1>"
    context = {"name": "World"}
    html = Template(template).render(context)
    assert "Hello, World" in html
def handle_output(data, use_buffer=False):
    if use_buffer:
        return data  # Return variable
    else:
        print("Writing data:", data)
        # with open("output.txt", "w") as f:
        #     f.write(data)

# Example usage
result = handle_output("Test Data", use_buffer=True)
print("Buffered result:", result)

handle_output("Actual write", use_buffer=False)

