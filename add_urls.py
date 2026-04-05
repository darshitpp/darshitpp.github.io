import os
import re

def insert_url(filepath, url_path):
    with open(filepath, 'r') as f: content = f.read()
    # Ensure we don't double-insert
    if f'url: "{url_path}"' in content: return
    # Find the first '---' and insert after it
    new_content = re.sub(r'^(---\s*\n)', rf'\1url: "{url_path}"\n', content, count=1)
    with open(filepath, 'w') as f: f.write(new_content)

insert_url('content/musings/review-devi-for-millennials.md', '/posts/review-devi-for-millennials/')
if os.path.exists('content/musings/review-the-bhagavad-gita-millennials/index.md'):
    insert_url('content/musings/review-the-bhagavad-gita-millennials/index.md', '/posts/review-the-bhagavad-gita-millennials/')
if os.path.exists('content/musings/review-the-white-tiger/index.md'):
    insert_url('content/musings/review-the-white-tiger/index.md', '/posts/review-the-white-tiger/')
