# simple_md2html
a very simple python package to convert markdown document into html document.

## Usage

### Command Line Interface

```bash
pip install simple-md2html
python -m simple_md2html a.md
python -m simple_md2html a.md -o a.html
```

### Python Scripts

```python
import simple_md2html
markdown_text = """
# here is some markdown code
math block:
$$f(x)=e^x$$
$f(x)=e^x$ is a inline mathcode
codeblock and quotablock are also supported
"""
print(simple_md2html.get_html_content_for_markdown(markdown_text))
```
