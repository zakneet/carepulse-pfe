import re

with open('frontend/src/app/home/home.component.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Replace Logo
html = html.replace(
    '<span class="text-xl font-extrabold text-slate-900 tracking-tight">OptiClinic</span>',
    '<img src="assets/logo_opticlinic.svg.jpeg" class="h-10" alt="OptiClinic">'
)

# 2. Update specialities links
import re

# We will match routerLink="/patient/booking" [queryParams]="{specialite: 'X'}" and replace with (click)="onSearch('X', '')" style="cursor: pointer"
def replacer(match):
    spec = match.group(1)
    return f"(click)=\"onSearch('{spec}', '')\" style=\"cursor: pointer\""

html = re.sub(
    r'routerLink="/patient/booking" \[queryParams\]="\{specialite:\s*\'([^\']+)\'\}"',
    replacer,
    html
)

# 3. Update doctor card button
html = html.replace(
    '(click)="onSearch(doc.specialite, \'\')"',
    '(click)="bookDoctor(doc)"'
)

with open('frontend/src/app/home/home.component.html', 'w', encoding='utf-8') as f:
    f.write(html)
