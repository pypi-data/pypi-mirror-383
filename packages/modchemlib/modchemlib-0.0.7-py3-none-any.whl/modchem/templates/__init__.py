import re

def generate_code(template_file, output_file, placeholders):
    with open(template_file, 'r') as f:
        content = f.read()
    
    for key, value in placeholders.items():
        pattern = r'{{\s*' + re.escape(key) + '\s*}}'
        content = re.sub(pattern, str(value), content)
    
    with open(output_file, 'w') as f:
        f.write(content)