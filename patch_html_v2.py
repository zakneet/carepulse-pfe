import re

with open('frontend/src/app/home/home.component.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Remove the blue heartbeat logo. It is inside:
# <a routerLink="/" class="flex items-center gap-2" aria-label="OptiClinic accueil">
#   <div class="w-10 h-10 ...">
#     <svg ...></svg>
#   </div>
#   <img ...>
# </a>

pattern_logo = re.compile(r'(<a routerLink="/" class="flex items-center gap-2" aria-label="OptiClinic accueil">)\s*<div.*?</div>\s*(<img src="assets/logo_opticlinic\.svg\.jpeg" class="h-10" alt="OptiClinic">\s*</a>)', re.DOTALL)
html = pattern_logo.sub(r'\1\n          \2', html)

# 2. Replace the avatar div with the doctor photo.
# Currently it is:
# <div [class]="getAvatarColor(doc.nom) + ' w-[56px] h-[56px] rounded-full flex items-center justify-center text-white font-bold text-xl shrink-0 group-hover:scale-105 transition-transform duration-300'">
#   {{ getInitials(doc.nom || doc.prenom) }}
# </div>
# I will replace it with:
# <img src="assets/telemedicine_doctor.png" class="w-[56px] h-[56px] rounded-full object-cover shrink-0 group-hover:scale-105 transition-transform duration-300" alt="Dr. {{ doc.nom }}">

pattern_avatar = re.compile(r'<div \[class\]="getAvatarColor\(doc\.nom\)[^>]*>\s*\{\{\s*getInitials[^\}]*\}\}\s*</div>', re.DOTALL)
html = pattern_avatar.sub(r'<img src="assets/telemedicine_doctor.png" class="w-[56px] h-[56px] rounded-full object-cover shrink-0 group-hover:scale-105 transition-transform duration-300" alt="Dr. {{ doc.nom }} {{ doc.prenom }}">', html)


with open('frontend/src/app/home/home.component.html', 'w', encoding='utf-8') as f:
    f.write(html)
