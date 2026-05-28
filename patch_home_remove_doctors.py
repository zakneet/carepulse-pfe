import re

with open('frontend/src/app/home/home.component.html', 'r', encoding='utf-8') as f:
    html = f.read()

# I will find the #medecins section and remove it.
# The section looks like:
# <section id="medecins" class="py-24 relative z-10 bg-white">
#   ...
# </section>

pattern = re.compile(r'<section id="medecins" class="py-24 relative z-10 bg-white">.*?</section>', re.DOTALL)
html = pattern.sub('', html)

# Also update the navigation link if any:
# <a href="#medecins" ...>Pour les médecins</a>
# Let's change it to point to /doctors
html = html.replace('href="#medecins"', 'routerLink="/doctors"')

with open('frontend/src/app/home/home.component.html', 'w', encoding='utf-8') as f:
    f.write(html)
