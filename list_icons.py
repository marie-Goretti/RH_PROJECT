import re
import glob

all_icons = set()
for filepath in glob.glob('c:/Users/USER/Desktop/RH_PROJECT/personnel/templates/personnel/*.html'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    icons = re.findall(r'<i class="([^"]*(?:fas fa-|bi bi-)[^"]*)"></i>', content)
    for icon in icons:
        all_icons.add(icon)

for icon in all_icons:
    print(icon)
