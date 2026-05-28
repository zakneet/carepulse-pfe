import re

with open('frontend/src/app/home/home.component.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Split into sections using re.split or find
hero_match = re.search(r'(<main.*?</header>.*?<section id="top".*?</section>)', content, re.DOTALL)
spec_match = re.search(r'(<section id="specialites".*?</section>)', content, re.DOTALL)
med_match = re.search(r'(<section id="medecins".*?</section>)', content, re.DOTALL)
feat_match = re.search(r'(<section id="fonctionnalites".*?</section>)', content, re.DOTALL)
cta_match = re.search(r'(<section class="py-24 relative z-10".*?</section>)', content, re.DOTALL)

# Modify Hero
hero = hero_match.group(1)
old_div = '<div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-primary to-cyan-500 flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-primary/30">\n                  RD\n                </div>'
new_div = '<div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-primary to-cyan-500 flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-primary/30 overflow-hidden">\n                  <img src="assets/telemedicine_doctor.png" alt="Doctor" class="w-full h-full object-cover">\n                </div>'
hero = hero.replace(old_div, new_div)
hero = hero.replace('Dr. Rania Dhaou', 'Dr. Youssef Haddad')
hero = hero.replace('Médecine Générale • Tunis', 'Téléconsultation • Tunis')

how_it_works = """
  <section id="comment-ca-marche" class="py-24 bg-slate-50 relative z-10 border-t border-slate-100">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center max-w-3xl mx-auto mb-16">
        <p class="text-primary font-bold uppercase tracking-wider text-sm mb-2">Simple & Rapide</p>
        <h2 class="text-4xl lg:text-5xl font-extrabold mb-6 tracking-tight text-slate-900">Comment ça marche ?</h2>
      </div>
      <div class="grid md:grid-cols-3 gap-8 relative">
        <div class="hidden md:block absolute top-1/2 left-[15%] right-[15%] h-0.5 bg-gradient-to-r from-primary/20 via-primary/40 to-primary/20 -translate-y-1/2 z-0"></div>
        
        <div class="relative z-10 flex flex-col items-center text-center group">
          <div class="w-20 h-20 rounded-full bg-white border-4 border-slate-50 flex items-center justify-center text-2xl font-black text-primary shadow-xl mb-6 group-hover:scale-110 transition-transform">1</div>
          <h3 class="text-xl font-bold text-slate-900 mb-3">Recherchez</h3>
          <p class="text-slate-500 font-medium">Trouvez le bon spécialiste près de chez vous ou en ligne.</p>
        </div>
        
        <div class="relative z-10 flex flex-col items-center text-center group">
          <div class="w-20 h-20 rounded-full bg-white border-4 border-slate-50 flex items-center justify-center text-2xl font-black text-primary shadow-xl mb-6 group-hover:scale-110 transition-transform">2</div>
          <h3 class="text-xl font-bold text-slate-900 mb-3">Prenez RDV</h3>
          <p class="text-slate-500 font-medium">Choisissez le créneau qui vous convient et réservez en 1 clic.</p>
        </div>
        
        <div class="relative z-10 flex flex-col items-center text-center group">
          <div class="w-20 h-20 rounded-full bg-white border-4 border-slate-50 flex items-center justify-center text-2xl font-black text-primary shadow-xl mb-6 group-hover:scale-110 transition-transform">3</div>
          <h3 class="text-xl font-bold text-slate-900 mb-3">Consultez</h3>
          <p class="text-slate-500 font-medium">Rendez-vous au cabinet ou consultez en vidéo simplement.</p>
        </div>
      </div>
    </div>
  </section>
"""

new_content = hero + '\n\n' + feat_match.group(1) + '\n\n' + how_it_works + '\n\n' + spec_match.group(1) + '\n\n' + med_match.group(1) + '\n\n' + cta_match.group(1) + '\n\n</main>'

with open('frontend/src/app/home/home.component.html', 'w', encoding='utf-8') as f:
    f.write(new_content)
