import re
import glob

def replace_icons(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Map for FontAwesome
    fa_map = {
        'fa-bars': 'ph-list',
        'fa-building': 'ph-buildings',
        'fa-tachometer-alt': 'ph-gauge',
        'fa-users': 'ph-users',
        'fa-calendar-check': 'ph-calendar-check',
        'fa-sitemap': 'ph-tree-structure',
        'fa-cog': 'ph-gear',
        'fa-sign-out-alt': 'ph-sign-out',
        'fa-plus': 'ph-plus',
        'fa-calendar-times': 'ph-calendar-x',
        'fa-times-circle': 'ph-x-circle',
        'fa-hourglass-half': 'ph-hourglass',
        'fa-check-circle': 'ph-check-circle',
        'fa-arrow-left': 'ph-arrow-left',
        'fa-times': 'ph-x',
        'fa-trash': 'ph-trash',
        'fa-lightbulb': 'ph-lightbulb',
        'fa-paperclip': 'ph-paperclip',
        'fa-envelope': 'ph-envelope',
        'fa-inbox': 'ph-tray',
        'fa-calendar-alt': 'ph-calendar-blank',
        'fa-exclamation-circle': 'ph-warning-circle',
        'fa-briefcase': 'ph-briefcase',
        'fa-question-circle': 'ph-question',
        'fa-download': 'ph-download-simple',
        'fa-clock': 'ph-clock',
        'fa-chevron-right': 'ph-caret-right',
        'fa-pen': 'ph-pencil-simple',
        'fa-save': 'ph-floppy-disk',
        'fa-user': 'ph-user',
        'fa-list-check': 'ph-list-checks',
        'fa-exclamation-triangle': 'ph-warning',
        'fa-search': 'ph-magnifying-glass',
        'fa-chevron-left': 'ph-caret-left',
        'fa-edit': 'ph-pencil-simple',
        'fa-phone-alt': 'ph-phone',
        'fa-bell': 'ph-bell',
        'fa-calendar': 'ph-calendar',
        'fa-check': 'ph-check',
        'fa-calendar-plus': 'ph-calendar-plus',
        'fa-eye': 'ph-eye',
        'fa-umbrella-beach': 'ph-umbrella',
        'fa-align-left': 'ph-text-align-left',
        'fa-history': 'ph-clock-counter-clockwise',
        'fa-pen-square': 'ph-pencil-simple',
        'fa-flag': 'ph-flag',
        'fa-chart-bar': 'ph-chart-bar',
        'fa-comment-alt': 'ph-chat-circle',
        'fa-paper-plane': 'ph-paper-plane-tilt',
        'fa-user-check': 'ph-user-check',
        'fa-list': 'ph-list',
        'fa-ban': 'ph-prohibit',
        'fa-info-circle': 'ph-info'
    }
    
    # Map for Bootstrap Icons
    bi_map = {
        'bi-search': 'ph-magnifying-glass',
        'bi-people': 'ph-users',
        'bi-person-check': 'ph-user-check',
        'bi-clock-history': 'ph-clock-counter-clockwise',
        'bi-calendar-x': 'ph-calendar-x',
        'bi-arrow-up-short': 'ph-arrow-up',
        'bi-check2': 'ph-check',
        'bi-arrow-down-short': 'ph-arrow-down',
        'bi-hourglass': 'ph-hourglass',
        'bi-eye': 'ph-eye',
        'bi-pencil': 'ph-pencil-simple',
        'bi-trash': 'ph-trash',
        'bi-download': 'ph-download-simple',
        'bi-file-earmark-excel': 'ph-file-xls',
        'bi-file-earmark-pdf': 'ph-file-pdf',
        'bi-calendar-check': 'ph-calendar-check',
        'bi-check-circle': 'ph-check-circle',
        'bi-info-circle': 'ph-info',
        'bi-journal-text': 'ph-notebook',
        'bi-lightbulb': 'ph-lightbulb',
        'bi-send': 'ph-paper-plane-tilt',
        'bi-paperclip': 'ph-paperclip',
        'bi-clock': 'ph-clock'
    }
    
    # Replace fa-spin and handle it differently
    content = content.replace('fas fa-spinner fa-spin', 'ph-thin ph-spinner ph-spin')
    
    # Replace FontAwesome
    for fa, ph in fa_map.items():
        content = re.sub(rf'<i class="([^"]*)fas {fa}([^"]*)"></i>', rf'<i class="\1ph-thin {ph}\2"></i>', content)
        # also handle case where class string has other classes
        content = re.sub(rf'fas {fa}', f'ph-thin {ph}', content)
        
    # Replace Bootstrap Icons
    for bi, ph in bi_map.items():
        content = re.sub(rf'<i class="([^"]*)bi {bi}([^"]*)"></i>', rf'<i class="\1ph-thin {ph}\2"></i>', content)
        content = re.sub(rf'bi {bi}', f'ph-thin {ph}', content)
        
    # Clean up duplicate ph-thin classes if any were created
    content = content.replace('ph-thin ph-thin', 'ph-thin')
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

for filepath in glob.glob('c:/Users/USER/Desktop/RH_PROJECT/personnel/templates/personnel/*.html'):
    replace_icons(filepath)
    print(f"Processed {filepath}")
