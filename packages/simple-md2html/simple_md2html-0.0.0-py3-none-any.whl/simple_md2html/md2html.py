import markdown2
import re
import base64
import string
import secrets

def generate_random_sequence(length): 
    characters = string.ascii_lowercase + string.ascii_uppercase + string.digits # Define character set, including lowercase letters, uppercase letters, and digits
    random_sequence = ''.join(secrets.choice(characters) for _ in range(length)) # Use secrets.choice to generate random sequence
    return random_sequence

def pre_scan(content: str) -> str: # Some lines have leading spaces that must be removed, which can affect title recognition
    new_content = ""
    for line in content.split("\n"):
        if line.lstrip().startswith("#"):
            new_content += line.lstrip() + "\n"
        else:
            new_content += line + "\n"
    return new_content

# Intermediate constants: must be random alphanumeric sequences
RAW_DOLLAR                     = generate_random_sequence(64)
MATH_CONTENT_BEGIN             = generate_random_sequence(64)
MATH_CONTENT_END               = generate_random_sequence(64)
HTML_LINK_BEGIN                = generate_random_sequence(64)
HTML_LINK_END                  = generate_random_sequence(64)
CODE_BEGIN                     = generate_random_sequence(64)
CODE_END                       = generate_random_sequence(64)
OFFCANVAS_CONTENT_PALCE_HOLDER = generate_random_sequence(64)
NAVBAR_CONTENT_PALCE_HOLDER    = generate_random_sequence(64)

CDN = """
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>

<!-- Highlight.js -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/styles/default.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/highlight.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/languages/go.min.js"></script>
"""

NAVBAR = f"""
<div style="display: none;">
  {NAVBAR_CONTENT_PALCE_HOLDER}
</div>
"""

OFFCANVAS = f"""
<div style="display: none;">
  {OFFCANVAS_CONTENT_PALCE_HOLDER}
</div>
"""

STYLE="""
<style>
    blockquote {
        border-left: 4px solid #007bff;
        padding-left: 1rem;
        border-radius: 0.25rem;
        font-style: italic;
    }
</style>
"""

# Used to generate the html version of the specified markdown file
def get_html_from_md(md_text: str):
    html = markdown2.markdown(md_text, extras=['mathjax', "fenced-code-blocks", "code-friendly", 'tables'])
    return html

# Encapsulate http and https links
# One important thing to consider: shorter links may be a prefix of longer ones, so it's correct to replace longer ones first during replacement
def wrap_http_link(md_text):
    regex = r"[^\[\(]{1}(http(s)?://[^\s\n]+)[\s\n]{1}"
    new_text = md_text
    action_pair_list = []
    for match in re.finditer(regex, md_text):
        old_link = match.group(1)
        new_link = HTML_LINK_BEGIN + base64.b64encode(old_link.encode("utf-8")).decode("utf-8") + HTML_LINK_END
        action_pair_list.append((old_link, new_link))
    action_pair_list = sorted(action_pair_list, key=lambda x:-len(x[0])) # Must replace longer ones first
    for old_link, new_link in action_pair_list:
        new_text = new_text.replace(old_link, new_link)
    return new_text

# Protect math block content
def wrap_math_content(md_text):
    regex = r"\$+[^\$]+\$+"
    new_text = md_text
    for match in re.finditer(regex, md_text):
        old_link = match.group(0)
        new_link = MATH_CONTENT_BEGIN + base64.b64encode(old_link.encode("utf-8")).decode("utf-8") + MATH_CONTENT_END
        new_text = new_text.replace(old_link, new_link)
    return new_text

# Change links pointing to markdown files to point to html files
def rename_link(md_text): 
    regex = r"\[[^\]]*\]\([^\)]*.md\)"
    new_text = md_text
    for match in re.finditer(regex, md_text):
        old_link = (match.group(0))
        new_link = (match.group(0).replace(".md]", ".html]").replace(".md)", ".html)"))
        new_text = new_text.replace(old_link, new_link)
    return new_text

# Protect dollar signs
def wrap_raw_dollar(md_text):
    new_text = md_text
    new_text = new_text.replace(r"\$", RAW_DOLLAR)
    return new_text

# Render strikethrough
def render_del(md_text):
    regex = "~~[^~]*~~"
    new_text = md_text
    for match in re.finditer(regex, md_text):
        old_link = (match.group(0))
        new_link = ("<del>" + match.group(0)[2:-2] + "</del>")
        new_text = new_text.replace(old_link, new_link)
    return new_text

# Restore protected dollar signs
def unwrap_raw_dollar(html_content):
    new_text = html_content
    new_text = new_text.replace(RAW_DOLLAR, "$")
    return new_text

# Special handling for text fields in latex
def process_text_wrap(html_content):
    regex = r"\\text{.*?}"
    output_val = html_content
    for match in re.finditer(regex, html_content):
        old_content = match.group(0)
        new_content = old_content.replace(r"\;", " ").replace(r"\lt", r"} \lt \text{").replace(r"\gt", r"} \gt \text{")
        output_val = output_val.replace(old_content, new_content)
    return output_val

# Decode math block content from protected data
def unwrap_math_content(html_content):
    regex = MATH_CONTENT_BEGIN + r"[a-z0-9A-Z\=\+\-\/]+" + MATH_CONTENT_END
    new_text = html_content
    for match in re.finditer(regex, html_content):
        old_link = (match.group(0))
        new_link = old_link.replace(MATH_CONTENT_BEGIN, "").replace(MATH_CONTENT_END, "").strip()
        new_link = base64.b64decode(new_link).decode("utf-8")
        new_link = process_text_wrap(new_link.replace("<", r" \lt ").replace(">", r" \gt "))
        if new_link.startswith("$$"):
            new_text = new_text.replace(old_link, new_link)
        else:
            # Assume starts with a single $
            new_text = new_text.replace(old_link, "\\(" +new_link[1:-1] + "\\)")
    return new_text

def unwrap_html_link(html_content):
    regex = HTML_LINK_BEGIN + r"[a-z0-9A-Z\=\+\-\/]+" + HTML_LINK_END
    new_text = html_content
    for match in re.finditer(regex, html_content):
        old_link = (match.group(0))
        new_link = old_link.replace(HTML_LINK_BEGIN, "").replace(HTML_LINK_END, "").strip()
        new_link = base64.b64decode(new_link).decode("utf-8")
        new_link = '<a href="%s">%s</a>' % (new_link, new_link)
        new_text = new_text.replace(old_link, new_link)
    return new_text

def get_menu_from_list(menu_list):
    content = ''
    for index, grade, value in menu_list:
        content += '<a style="margin-left: %dpx;" class="nav-link" onclick="jump_to_lable(%d)">%s</a>' % (grade * 10, index, value)
    return content

def html_make_title_menu_section(html_content: str): # Build table of contents for indexing
    regex = r"<h\d>(.|\n)+?</h\d>"
    new_html = html_content
    cnt = 0
    menu_list = []
    for match in re.finditer(regex, html_content):
        cnt += 1
        old_link      = match.group(0)
        title_content = old_link[4:-5]
        title_level   = int(old_link[2])
        title_index   = cnt
        new_link      = '<h%d id="scrollspyHeading%d">%s</h%d>' % (title_level, title_index, title_content, title_level)
        new_html = new_html.replace(old_link, new_link)
        menu_list.append((title_index, title_level, title_content))
    menu_content = get_menu_from_list(menu_list)
    return new_html, menu_content

def process_table_class(html_content: str) -> str:
    return html_content.replace("<table>", "<table class=\"table table-striped\">")


CODE_PATTERN = re.compile(r'\n```.*?\n```', re.DOTALL)
def find_code_blocks(text):
    matches = CODE_PATTERN.finditer(text)
    results = []
    for match in matches:
        results.append({
            'start': match.start(),
            'end': match.end(),
            'content': match.group()
        })
    return results

def wrap_code_block(markdown_content:str) -> str:
    code_data = find_code_blocks(markdown_content)
    markdown_content_parts = CODE_PATTERN.split(markdown_content)
    merge_list = []
    for i in range(max(len(code_data), len(markdown_content_parts))):
        if i < len(markdown_content_parts):
            merge_list.append(markdown_content_parts[i])
        if i < len(code_data):
            code_content = CODE_BEGIN + base64.b64encode(code_data[i]["content"].encode("utf-8")).decode("utf-8") + CODE_END
            merge_list.append(code_content)
    return "".join(merge_list)

def unwrap_code_block(html_content:str) -> str:
    regex = CODE_BEGIN + r"[a-z0-9A-Z\=\+\-\/]+" + CODE_END
    new_text = html_content
    for match in re.finditer(regex, html_content):
        old_code = (match.group(0))
        new_code = old_code.replace(CODE_BEGIN, "").replace(CODE_END, "").strip()
        new_code = base64.b64decode(new_code).decode("utf-8")
        lang_detected = new_code.lstrip().split("\n", maxsplit=1)[0].replace("`", "").strip()
        code_content = new_code.lstrip().split("\n", maxsplit=1)[-1].rstrip()[:-3].rstrip()
        if lang_detected != "":
            new_code = f"<pre><code class=\"language-{lang_detected}\">{code_content}</code></pre>"
        else:
            new_code = f"<pre><code>{code_content}</code></pre>" # auto detect
        new_text = new_text.replace(old_code, new_code)
    return new_text

# Render a single html page
def get_html_content_for_markdown(markdown_content:str, finalize=True):
    markdown_content = wrap_code_block(markdown_content)
    markdown_content = wrap_http_link(markdown_content) # Rendering pipeline
    markdown_content = render_del(markdown_content)
    markdown_content = rename_link(markdown_content)
    markdown_content = wrap_raw_dollar(markdown_content)
    markdown_content = wrap_math_content(markdown_content)
    html_content     = get_html_from_md(markdown_content) # Render html
    html_content     = unwrap_math_content(html_content) # Render html
    html_content     = unwrap_raw_dollar(html_content)
    html_content     = unwrap_html_link(html_content)
    html_content     = unwrap_code_block(html_content)
    html_content     = process_table_class(html_content)

    # Only wrap the outer content of HTML document when finalize=True
    if finalize:
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            {STYLE}
        </head>
        <body data-bs-theme="light">
            {NAVBAR}
            {OFFCANVAS}
            <div data-bs-spy="scroll" data-bs-target="#navbar-example2" data-bs-root-margin="0px 0px -40%" data-bs-smooth-scroll="true" class="scrollspy-example bg-body-tertiary p-3 rounded-2" tabindex="0">
                {html_content}
            </div>
            {CDN}
            <script>
                // init all code block
                document.addEventListener('DOMContentLoaded', function() {{
                    hljs.highlightAll();
                }});
            </script>
        </body>
        </html>
            """
    return html_content
