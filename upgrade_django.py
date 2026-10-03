import os
import re

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # 1. Update url routing
    content = content.replace('from django.conf.urls import url', 'from django.urls import re_path')
    content = content.replace('from django.conf.urls import include, url', 'from django.urls import include, re_path')
    # Use regex to safely replace url( with re_path( but only if it's likely a routing url
    # We might accidentally replace url( in other contexts, but django urls usually look like url(r'^...', ...)
    # Let's replace ' url(' and '    url(' etc.
    content = re.sub(r'\burl\(', 're_path(', content)

    # 2. Update is_authenticated()
    content = content.replace('.is_authenticated()', '.is_authenticated')

    # 3. Add on_delete=models.CASCADE to ForeignKey
    # This is tricky with multiline ForeignKeys, but we can try our best on single line ones
    # and then rely on flake8/Django checks to find the rest
    
    # We'll use a regex that looks for models.ForeignKey(...) and adds on_delete=models.CASCADE if not present.
    # To handle multiline, we can just replace `models.ForeignKey(` with a check later, but regex on Python is easier
    # Let's just do a simple pass on ones that look like `models.ForeignKey(ModelName)` or `models.ForeignKey('ModelName')`
    
    # A robust way is to find `models.ForeignKey(` and the matching closing `)`. 
    # But a regex like `models\.ForeignKey\(([^)]+)\)` works if there are no nested parens.
    def replacer(match):
        inner = match.group(1)
        if 'on_delete=' not in inner:
            return f"models.ForeignKey({inner}, on_delete=models.CASCADE)"
        return match.group(0)
    
    content = re.sub(r'models\.ForeignKey\(([^)]+)\)', replacer, content)

    # 4. Remove python_2_unicode_compatible
    content = content.replace('from django.utils.encoding import python_2_unicode_compatible\n', '')
    content = content.replace('@python_2_unicode_compatible\n', '')

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")

for root, dirs, files in os.walk('opentreemap'):
    for file in files:
        if file.endswith('.py'):
            process_file(os.path.join(root, file))
