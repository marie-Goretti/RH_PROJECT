import re
import glob

# Mapping everything to Phosphor Icons
icon_map = {
    'eye': 'ph-eye',
    'envelope': 'ph-envelope',
    'paperclip': 'ph-paperclip',
    'lightbulb': 'ph-lightbulb',
    'times-circle': 'ph-x-circle',
    'hourglass-half': 'ph-hourglass',
    'clock': 'ph-clock',
    'question-circle': 'ph-question',
    'chevron-right': 'ph-caret-right',
    'arrow-left': 'ph-arrow-left',
    'info-circle': 'ph-info',
    'calendar': 'ph-calendar',
    'exclamation-triangle': 'ph-warning',
    'bell': 'ph-bell',
    'inbox': 'ph-tray',
    'calendar-plus': 'ph-calendar-plus',
    'plus': 'ph-plus',
    'exclamation-circle': 'ph-warning-circle',
    'times': 'ph-x',
    'check-circle': 'ph-check-circle',
    'check': 'ph-check',
    'umbrella-beach': 'ph-umbrella',
    'download': 'ph-download-simple',
    'paper-plane': 'ph-paper-plane-right',
    'calendar-alt': 'ph-calendar-blank',
    'pen': 'ph-pencil-simple',
    'chart-bar': 'ph-chart-bar',
    'list-check': 'ph-list-checks',
    'calendar-times': 'ph-calendar-x',
    'history': 'ph-clock-counter-clockwise',
    'edit': 'ph-pencil-simple',
    'list': 'ph-list',
    'briefcase': 'ph-briefcase',
    'comment-alt': 'ph-chat-teardrop',
    'pen-square': 'ph-pencil-simple',
    'user': 'ph-user',
    'user-check': 'ph-user-check',
    'spinner': 'ph-spinner',
    'flag': 'ph-flag',
    'trash': 'ph-trash',
    'chevron-left': 'ph-caret-left',
    'search': 'ph-magnifying-glass',
    'save': 'ph-floppy-disk',
    'phone-alt': 'ph-phone',
    'ban': 'ph-prohibit',
    'align-left': 'ph-text-align-left',
    'send': 'ph-paper-plane-right',
    'calendar-check': 'ph-calendar-check',
    'journal-text': 'ph-notebook'
}

def replace_match(match):
    prefix = match.group(1) # e.g. "fas fa-" or "bi bi-"
    icon_name = match.group(2)
    
    if icon_name in icon_map:
        return f'ph-thin {icon_map[icon_name]}'
    return match.group(0) # Keep original if not found

for filepath in glob.glob('c:/Users/USER/Desktop/RH_PROJECT/personnel/templates/personnel/*.html'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Replace the classes
    # e.g., <i class="fas fa-eye me-1">
    # Matches "fas fa-" or "bi bi-" followed by word chars and hyphens
    new_content = re.sub(r'(fas fa-|bi bi-)([\w-]+)', replace_match, content)
    
    # Also clean up any lingering 'fas' or 'bi' isolated classes that might have been part of the tag but not attached (though the regex above catches the prefix)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filepath}")
