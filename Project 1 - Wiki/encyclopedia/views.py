# Add random for randomizer function
from random import choice

from django.shortcuts import redirect, render

from . import util


def index(request):
    # Define variables
    entry_list = util.list_entries()
    q = request.GET.get('q', '').strip()

    # Mechanism
    entries = []
    for e in entry_list:
        # If exact match, redirect
        if q.lower() == e.lower():
            return redirect('wiki_content', title=q)
        # Otherwise, put entries closer to text
        # If none, it will still put all entry list
        elif q.lower() in e.lower():
            entries.append(e)

    return render(request, "encyclopedia/index.html", {
        "search_query": q,
        "entries": entries
    })

def wiki_content(request, title):
    # Using utility
    entry = util.get_entry(title)

    # Check if it exist
    if entry is None:
        return render(request, "wiki/content.html", {
            "title": title.capitalize(),
            "content_bool": False
        })

    # Title
    split = entry.splitlines()[0]
    if split.startswith('# '):
        page_title = split[2:].strip()
    else:
        page_title = title

    # Return if it does
    return render(request, "wiki/content.html", {
        "title": page_title,
        "sub_title": title,
        "content_bool": True,
        "page_content": util.markdown_convert(entry)
    })

def create_new_page(request):
    # POST request
    if request.method == "POST":
        # Define variables
        entries = util.list_entries()
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()

        # Check if title exist
        for e in entries:
            if title.lower() == e.lower():
                return render(request, "encyclopedia/add.html", {
                    "message_log": f"The title {title} is already exist."
                })

        # If does not exist, we add
        util.save_entry(title, content)
        return redirect('wiki_content', title=title)

    return render(request, "encyclopedia/add.html") 

def edit_page(request, title):
    # Define variable/s
    content = util.get_entry(title)

    # Countermeasure if user attempt to edit a non-exist title
    if content is None:
        return redirect('index')

    # Mechanism
    if request.method == "POST":
        new_content = request.POST.get('content', '').strip()
        util.save_entry(title, new_content)
        return redirect('wiki_content', title=title)

    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "content": content,
    })

def random_page(request):
    # Random module
    # https://www.programiz.com/python-programming/modules/random
    # Define variable/s
    entries = util.list_entries()
    random_title = choice(entries)

    return redirect('wiki_content', title=random_title)