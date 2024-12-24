import re

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def list_entries():
    """
    Returns a list of all names of encyclopedia entries.
    """
    _, filenames = default_storage.listdir("entries")
    return list(sorted(re.sub(r"\.md$", "", filename)
                for filename in filenames if filename.endswith(".md")))


def save_entry(title, content):
    """
    Saves an encyclopedia entry, given its title and Markdown
    content. If an existing entry with the same title already exists,
    it is replaced.
    """
    filename = f"entries/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
    default_storage.save(filename, ContentFile(content))


def get_entry(title):
    """
    Retrieves an encyclopedia entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(f"entries/{title}.md")
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None

# Convert markdown to HTML content
def markdown_convert(content):
    # Note to myself:
    # supporting headings, boldface text, unordered lists, links, and paragraphs

    if not content:
        return ''

    # Headings
    content = re.sub(r'(?m)^### (.+)$', r'<h3>\1</h3>', content)
    content = re.sub(r'(?m)^## (.+)$', r'<h2>\1</h2>', content)
    content = re.sub(r'(?m)^# (.+)$', r'<h1>\1</h1>', content)

    # Bold text
    content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)

    # Unordered list
    # content = re.sub(r'(?m)^\* (.+)$', r'<li>\1</li>', content)
    # content = re.sub(r'(?s)(<li>.*?</li>)', r'<ul>\1</ul>', content)

    # Links
    content = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', content)

    # Paragraph/Unordered list
    # Fixed: Bug content when viewing wiki/HTML
    paragraph = content.split('\n')
    var = []
    is_list = False

    for p in paragraph:
        p = p.strip()

        if p.startswith('* '):
            if not is_list:
                var.append('<ul>')
                is_list = True
            var.append(f'<li>{p[2:].strip()}</li>')
        else:
            if is_list:
                var.append('</ul>')
                is_list = False

            if p.startswith('<h') or p.startswith('<ul>') or p.startswith('</ul>'):
                var.append(p)
            elif p:
                var.append(f'<p>{p}</p>')

    if is_list:
        var.append('</ul>')

    content = ''.join(var)

    return content