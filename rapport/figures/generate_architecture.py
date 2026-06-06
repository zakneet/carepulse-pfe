#!/usr/bin/env python3
"""
Generates the OptiClinic conceptual architecture diagram as SVG (and PNG if cairosvg is available).
Output: opticlinic-architecture-conceptuelle.svg
"""

SVG = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="820" viewBox="0 0 1200 820"
     font-family="Arial, Helvetica, sans-serif">

  <defs>
    <!-- Gradients -->
    <linearGradient id="headerGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#0d47a1"/>
      <stop offset="100%" stop-color="#0288d1"/>
    </linearGradient>
    <linearGradient id="frontendGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#e3f2fd"/>
      <stop offset="100%" stop-color="#bbdefb"/>
    </linearGradient>
    <linearGradient id="backendGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#1a237e"/>
      <stop offset="100%" stop-color="#283593"/>
    </linearGradient>
    <linearGradient id="mysqlGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#e8eaf6"/>
      <stop offset="100%" stop-color="#c5cae9"/>
    </linearGradient>
    <linearGradient id="brevoGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#e0f7fa"/>
      <stop offset="100%" stop-color="#b2ebf2"/>
    </linearGradient>
    <!-- Drop shadow -->
    <filter id="shadow" x="-5%" y="-5%" width="115%" height="115%">
      <feDropShadow dx="2" dy="3" stdDeviation="4" flood-color="#00000033"/>
    </filter>
    <filter id="shadowLight" x="-5%" y="-5%" width="115%" height="115%">
      <feDropShadow dx="1" dy="2" stdDeviation="3" flood-color="#0000001a"/>
    </filter>
    <!-- Arrow marker -->
    <marker id="arrowBlue" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#0288d1"/>
    </marker>
    <marker id="arrowGreen" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#00897b"/>
    </marker>
    <marker id="arrowGray" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#546e7a"/>
    </marker>
    <marker id="arrowIndigo" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#3949ab"/>
    </marker>
  </defs>

  <!-- Background -->
  <rect width="1200" height="820" fill="#f8faff" rx="0"/>

  <!-- ═══════════════════════════════════════════════
       HEADER BAND
  ═══════════════════════════════════════════════ -->
  <rect x="0" y="0" width="1200" height="58" fill="url(#headerGrad)"/>
  <text x="600" y="34" text-anchor="middle" fill="white" font-size="18" font-weight="bold" letter-spacing="0.5">
    Figure 4.1 — Architecture conceptuelle du système OptiClinic
  </text>
  <text x="600" y="52" text-anchor="middle" fill="#90caf9" font-size="11">
    Diagramme C4 — Vue Conteneurs
  </text>

  <!-- ═══════════════════════════════════════════════
       ROW 1 — ACTORS
  ═══════════════════════════════════════════════ -->

  <!-- Patient -->
  <g filter="url(#shadowLight)">
    <rect x="60" y="82" width="148" height="90" rx="12" fill="white" stroke="#0288d1" stroke-width="2"/>
  </g>
  <!-- Person icon -->
  <circle cx="134" cy="107" r="16" fill="#e3f2fd" stroke="#0288d1" stroke-width="1.5"/>
  <circle cx="134" cy="102" r="7" fill="#0288d1"/>
  <path d="M118 122 Q118 113 134 113 Q150 113 150 122" fill="#0288d1"/>
  <text x="134" y="148" text-anchor="middle" fill="#0d47a1" font-size="13" font-weight="bold">Patient</text>
  <text x="134" y="163" text-anchor="middle" fill="#546e7a" font-size="9">[Acteur externe]</text>

  <!-- Médecin -->
  <g filter="url(#shadowLight)">
    <rect x="526" y="82" width="148" height="90" rx="12" fill="white" stroke="#0288d1" stroke-width="2"/>
  </g>
  <circle cx="600" cy="107" r="16" fill="#e3f2fd" stroke="#0288d1" stroke-width="1.5"/>
  <circle cx="600" cy="102" r="7" fill="#0288d1"/>
  <path d="M584 122 Q584 113 600 113 Q616 113 616 122" fill="#0288d1"/>
  <text x="600" y="145" text-anchor="middle" fill="#0d47a1" font-size="12" font-weight="bold">Médecin /</text>
  <text x="600" y="159" text-anchor="middle" fill="#0d47a1" font-size="12" font-weight="bold">Personnel de santé</text>
  <text x="600" y="167" text-anchor="middle" fill="#546e7a" font-size="9">[Acteur externe]</text>

  <!-- Administrateur -->
  <g filter="url(#shadowLight)">
    <rect x="992" y="82" width="148" height="90" rx="12" fill="white" stroke="#0288d1" stroke-width="2"/>
  </g>
  <circle cx="1066" cy="107" r="16" fill="#e3f2fd" stroke="#0288d1" stroke-width="1.5"/>
  <circle cx="1066" cy="102" r="7" fill="#0288d1"/>
  <path d="M1050 122 Q1050 113 1066 113 Q1082 113 1082 122" fill="#0288d1"/>
  <text x="1066" y="148" text-anchor="middle" fill="#0d47a1" font-size="13" font-weight="bold">Administrateur</text>
  <text x="1066" y="163" text-anchor="middle" fill="#546e7a" font-size="9">[Acteur externe]</text>

  <!-- ═══════════════════════════════════════════════
       ROW 2 — FRONTEND CONTAINER
  ═══════════════════════════════════════════════ -->
  <g filter="url(#shadow)">
    <rect x="40" y="210" width="1120" height="165" rx="14" fill="url(#frontendGrad)" stroke="#1565c0" stroke-width="2"/>
  </g>
  <!-- Label -->
  <rect x="40" y="210" width="270" height="30" rx="7" fill="#1565c0"/>
  <text x="175" y="230" text-anchor="middle" fill="white" font-size="12" font-weight="bold">Interface Web Angular</text>
  <text x="950" y="228" text-anchor="end" fill="#1565c0" font-size="10" font-style="italic">[Conteneur : Application SPA]</text>

  <!-- Sub-panel: Réservation / Espace Patient -->
  <rect x="65" y="250" width="290" height="108" rx="10" fill="white" fill-opacity="0.75" stroke="#0288d1" stroke-width="1.5" stroke-dasharray="5,3"/>
  <rect x="65" y="250" width="290" height="26" rx="7" fill="#0288d1" fill-opacity="0.8"/>
  <text x="210" y="267" text-anchor="middle" fill="white" font-size="11" font-weight="bold">Réservation en ligne</text>
  <text x="210" y="300" text-anchor="middle" fill="#0d47a1" font-size="11">• Prise de rendez-vous</text>
  <text x="210" y="318" text-anchor="middle" fill="#0d47a1" font-size="11">• Espace Patient</text>
  <text x="210" y="336" text-anchor="middle" fill="#0d47a1" font-size="11">• Suivi des dossiers</text>

  <!-- Sub-panel: Tableau de bord médical -->
  <rect x="845" y="250" width="290" height="108" rx="10" fill="white" fill-opacity="0.75" stroke="#0288d1" stroke-width="1.5" stroke-dasharray="5,3"/>
  <rect x="845" y="250" width="290" height="26" rx="7" fill="#0288d1" fill-opacity="0.8"/>
  <text x="990" y="267" text-anchor="middle" fill="white" font-size="11" font-weight="bold">Tableau de bord médical</text>
  <text x="990" y="300" text-anchor="middle" fill="#0d47a1" font-size="11">• Gestion du planning</text>
  <text x="990" y="318" text-anchor="middle" fill="#0d47a1" font-size="11">• Gestion des urgences</text>
  <text x="990" y="336" text-anchor="middle" fill="#0d47a1" font-size="11">• Suivi des patients</text>

  <!-- Angular shield icon center -->
  <text x="600" y="295" text-anchor="middle" fill="#1565c0" font-size="13" font-weight="bold" opacity="0.6">⬡ Angular</text>
  <text x="600" y="315" text-anchor="middle" fill="#1565c0" font-size="10" opacity="0.5">Single Page Application</text>

  <!-- ═══════════════════════════════════════════════
       ROW 3 — BACKEND CONTAINER
  ═══════════════════════════════════════════════ -->
  <g filter="url(#shadow)">
    <rect x="40" y="415" width="1120" height="185" rx="14" fill="url(#backendGrad)" stroke="#0d1b6e" stroke-width="2"/>
  </g>
  <rect x="40" y="415" width="290" height="30" rx="7" fill="#0d1b6e"/>
  <text x="185" y="435" text-anchor="middle" fill="white" font-size="12" font-weight="bold">Système OptiClinic — Backend</text>
  <text x="1145" y="434" text-anchor="end" fill="#90caf9" font-size="10" font-style="italic">[Conteneurs : API + Services]</text>

  <!-- API Backend Flask -->
  <g filter="url(#shadowLight)">
    <rect x="390" y="450" width="240" height="120" rx="12" fill="#1a237e" stroke="#5c6bc0" stroke-width="2"/>
  </g>
  <rect x="390" y="450" width="240" height="30" rx="8" fill="#3949ab"/>
  <text x="510" y="470" text-anchor="middle" fill="white" font-size="12" font-weight="bold">API Backend Flask</text>
  <text x="510" y="490" text-anchor="middle" fill="#90caf9" font-size="10">[Conteneur : API REST]</text>
  <text x="510" y="510" text-anchor="middle" fill="#c5cae9" font-size="10">• Logique métier</text>
  <text x="510" y="528" text-anchor="middle" fill="#c5cae9" font-size="10">• Authentification JWT</text>
  <text x="510" y="546" text-anchor="middle" fill="#c5cae9" font-size="10">• Gestion des rendez-vous</text>

  <!-- Socket.IO -->
  <g filter="url(#shadowLight)">
    <rect x="680" y="450" width="220" height="120" rx="12" fill="#006064" stroke="#00acc1" stroke-width="2"/>
  </g>
  <rect x="680" y="450" width="220" height="30" rx="8" fill="#00838f"/>
  <text x="790" y="470" text-anchor="middle" fill="white" font-size="11" font-weight="bold">Canal temps réel</text>
  <text x="790" y="485" text-anchor="middle" fill="white" font-size="11" font-weight="bold">Socket.IO</text>
  <text x="790" y="502" text-anchor="middle" fill="#b2ebf2" font-size="10">[Conteneur : WebSocket]</text>
  <text x="790" y="522" text-anchor="middle" fill="#e0f7fa" font-size="10">• Notifications temps réel</text>
  <text x="790" y="540" text-anchor="middle" fill="#e0f7fa" font-size="10">• Alertes urgences</text>
  <text x="790" y="558" text-anchor="middle" fill="#e0f7fa" font-size="10">• Mises à jour planning</text>

  <!-- OR-Tools -->
  <g filter="url(#shadowLight)">
    <rect x="90" y="450" width="240" height="120" rx="12" fill="#1a237e" stroke="#7986cb" stroke-width="2"/>
  </g>
  <rect x="90" y="450" width="240" height="30" rx="8" fill="#3f51b5"/>
  <text x="210" y="470" text-anchor="middle" fill="white" font-size="12" font-weight="bold">Module d'optimisation</text>
  <text x="210" y="485" text-anchor="middle" fill="white" font-size="12" font-weight="bold">OR-Tools</text>
  <text x="210" y="503" text-anchor="middle" fill="#c5cae9" font-size="10">[Conteneur : Optimisation]</text>
  <text x="210" y="522" text-anchor="middle" fill="#c5cae9" font-size="10">• Optimisation des créneaux</text>
  <text x="210" y="540" text-anchor="middle" fill="#c5cae9" font-size="10">• Réorganisation planning</text>
  <text x="210" y="558" text-anchor="middle" fill="#c5cae9" font-size="10">• Résolution de conflits</text>

  <!-- ═══════════════════════════════════════════════
       ROW 4 — DATA / EXTERNAL SERVICES
  ═══════════════════════════════════════════════ -->

  <!-- Base MySQL -->
  <g filter="url(#shadow)">
    <rect x="60" y="640" width="420" height="130" rx="14" fill="url(#mysqlGrad)" stroke="#3949ab" stroke-width="2"/>
  </g>
  <rect x="60" y="640" width="230" height="28" rx="7" fill="#3949ab"/>
  <text x="175" y="659" text-anchor="middle" fill="white" font-size="11" font-weight="bold">Base de données MySQL</text>
  <text x="270" y="659" text-anchor="start" fill="#3949ab" font-size="9" font-style="italic">  [Conteneur : BDD relationnelle]</text>
  <!-- Cylinder icon -->
  <ellipse cx="108" cy="700" rx="22" ry="8" fill="#7986cb" opacity="0.6"/>
  <rect x="86" y="700" width="44" height="30" fill="#7986cb" opacity="0.4"/>
  <ellipse cx="108" cy="730" rx="22" ry="8" fill="#5c6bc0" opacity="0.7"/>
  <text x="270" y="698" text-anchor="middle" fill="#1a237e" font-size="10">• patients · rendez-vous</text>
  <text x="270" y="715" text-anchor="middle" fill="#1a237e" font-size="10">• plannings · notifications</text>
  <text x="270" y="732" text-anchor="middle" fill="#1a237e" font-size="10">• paramètres d'optimisation</text>
  <text x="270" y="749" text-anchor="middle" fill="#546e7a" font-size="9">Lecture / Écriture des données</text>

  <!-- Brevo -->
  <g filter="url(#shadow)">
    <rect x="720" y="640" width="420" height="130" rx="14" fill="url(#brevoGrad)" stroke="#00838f" stroke-width="2"/>
  </g>
  <rect x="720" y="640" width="200" height="28" rx="7" fill="#00838f"/>
  <text x="820" y="659" text-anchor="middle" fill="white" font-size="11" font-weight="bold">Service Email Brevo</text>
  <text x="940" y="659" text-anchor="start" fill="#006064" font-size="9" font-style="italic">  [Service externe]</text>
  <!-- Email icon -->
  <rect x="740" y="690" width="44" height="32" rx="4" fill="#00838f" opacity="0.5"/>
  <path d="M740 690 L762 710 L784 690" stroke="white" stroke-width="2" fill="none"/>
  <text x="920" y="698" text-anchor="middle" fill="#004d40" font-size="10">• Email de confirmation</text>
  <text x="920" y="715" text-anchor="middle" fill="#004d40" font-size="10">• Lien vers l'espace patient</text>
  <text x="920" y="732" text-anchor="middle" fill="#004d40" font-size="10">• Notifications rendez-vous</text>
  <text x="920" y="749" text-anchor="middle" fill="#546e7a" font-size="9">Envoi de confirmation email</text>

  <!-- ═══════════════════════════════════════════════
       ARROWS
  ═══════════════════════════════════════════════ -->

  <!-- Patient → Interface Web (Demande RDV) -->
  <line x1="134" y1="172" x2="134" y2="210" stroke="#0288d1" stroke-width="2" marker-end="url(#arrowBlue)"/>
  <rect x="35" y="185" width="140" height="16" rx="4" fill="white" fill-opacity="0.85"/>
  <text x="104" y="197" text-anchor="middle" fill="#0277bd" font-size="9" font-weight="bold">Demande de rendez-vous</text>

  <!-- Médecin → Interface Web -->
  <line x1="600" y1="172" x2="600" y2="210" stroke="#0288d1" stroke-width="2" marker-end="url(#arrowBlue)"/>
  <rect x="510" y="185" width="160" height="16" rx="4" fill="white" fill-opacity="0.85"/>
  <text x="590" y="197" text-anchor="middle" fill="#0277bd" font-size="9" font-weight="bold">Gestion du planning / Urgences</text>

  <!-- Admin → Interface Web -->
  <line x1="1066" y1="172" x2="1066" y2="210" stroke="#0288d1" stroke-width="2" marker-end="url(#arrowBlue)"/>
  <rect x="990" y="185" width="110" height="16" rx="4" fill="white" fill-opacity="0.85"/>
  <text x="1045" y="197" text-anchor="middle" fill="#0277bd" font-size="9" font-weight="bold">Administration</text>

  <!-- Interface Web → API Flask (REST) -->
  <line x1="510" y1="375" x2="510" y2="450" stroke="#1565c0" stroke-width="2.5" marker-end="url(#arrowBlue)"/>
  <rect x="420" y="392" width="145" height="16" rx="4" fill="white" fill-opacity="0.9"/>
  <text x="493" y="404" text-anchor="middle" fill="#0d47a1" font-size="9" font-weight="bold">API REST sécurisée</text>

  <!-- Interface Web ↔ Socket.IO (temps réel) -->
  <line x1="720" y1="375" x2="790" y2="450" stroke="#00838f" stroke-width="2" marker-end="url(#arrowGreen)"/>
  <rect x="685" y="398" width="150" height="16" rx="4" fill="white" fill-opacity="0.9"/>
  <text x="760" y="410" text-anchor="middle" fill="#00695c" font-size="9" font-weight="bold">Notifications temps réel</text>

  <!-- API Flask → OR-Tools -->
  <line x1="390" y1="510" x2="330" y2="510" stroke="#3949ab" stroke-width="2" marker-end="url(#arrowIndigo)"/>
  <rect x="316" y="497" width="130" height="16" rx="4" fill="white" fill-opacity="0.9"/>
  <text x="381" y="509" text-anchor="middle" fill="#1a237e" font-size="9" font-weight="bold">Optimisation des créneaux</text>

  <!-- OR-Tools → API Flask (return) -->
  <line x1="330" y1="525" x2="390" y2="525" stroke="#3949ab" stroke-width="2" stroke-dasharray="6,3" marker-end="url(#arrowIndigo)"/>
  <rect x="316" y="527" width="130" height="16" rx="4" fill="white" fill-opacity="0.9"/>
  <text x="381" y="539" text-anchor="middle" fill="#1a237e" font-size="9">Résultats d'optimisation</text>

  <!-- API Flask → MySQL -->
  <line x1="460" y1="570" x2="340" y2="640" stroke="#546e7a" stroke-width="2" marker-end="url(#arrowGray)"/>
  <rect x="330" y="596" width="155" height="16" rx="4" fill="white" fill-opacity="0.9"/>
  <text x="408" y="608" text-anchor="middle" fill="#37474f" font-size="9" font-weight="bold">Lecture / écriture des données</text>

  <!-- API Flask → Brevo -->
  <line x1="600" y1="570" x2="850" y2="640" stroke="#00838f" stroke-width="2" marker-end="url(#arrowGreen)"/>
  <rect x="660" y="592" width="125" height="16" rx="4" fill="white" fill-opacity="0.9"/>
  <text x="723" y="604" text-anchor="middle" fill="#00695c" font-size="9" font-weight="bold">Confirmation email</text>

  <!-- ═══════════════════════════════════════════════
       LEGEND
  ═══════════════════════════════════════════════ -->
  <rect x="950" y="645" width="190" height="118" rx="10" fill="white" fill-opacity="0.9" stroke="#b0bec5" stroke-width="1"/>
  <text x="1045" y="663" text-anchor="middle" fill="#37474f" font-size="10" font-weight="bold">Légende</text>
  <line x1="962" y1="675" x2="1000" y2="675" stroke="#0288d1" stroke-width="2" marker-end="url(#arrowBlue)"/>
  <text x="1005" y="679" fill="#546e7a" font-size="9">Interaction utilisateur</text>
  <line x1="962" y1="693" x2="1000" y2="693" stroke="#1565c0" stroke-width="2.5" marker-end="url(#arrowBlue)"/>
  <text x="1005" y="697" fill="#546e7a" font-size="9">API REST sécurisée</text>
  <line x1="962" y1="711" x2="1000" y2="711" stroke="#00838f" stroke-width="2" marker-end="url(#arrowGreen)"/>
  <text x="1005" y="715" fill="#546e7a" font-size="9">Service externe</text>
  <line x1="962" y1="729" x2="1000" y2="729" stroke="#3949ab" stroke-width="2" stroke-dasharray="6,3" marker-end="url(#arrowIndigo)"/>
  <text x="1005" y="733" fill="#546e7a" font-size="9">Retour optimisation</text>
  <line x1="962" y1="747" x2="1000" y2="747" stroke="#546e7a" stroke-width="2" marker-end="url(#arrowGray)"/>
  <text x="1005" y="751" fill="#546e7a" font-size="9">Accès base de données</text>

  <!-- Footer -->
  <rect x="0" y="800" width="1200" height="20" fill="#0d47a1" fill-opacity="0.07"/>
  <text x="600" y="814" text-anchor="middle" fill="#546e7a" font-size="9">
    OptiClinic — Architecture conceptuelle — Diagramme C4 Conteneurs — Projet PFE 2025-2026
  </text>

</svg>'''

output_path = "opticlinic-architecture-conceptuelle.svg"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(SVG)

print(f"SVG generated: {output_path}")

# Try to convert to PNG using cairosvg or Pillow
try:
    import cairosvg
    cairosvg.svg2png(url=output_path, write_to="opticlinic-architecture-conceptuelle.png", output_width=1200, output_height=820)
    print("PNG also generated via cairosvg.")
except ImportError:
    print("cairosvg not available. SVG only. Convert manually with Inkscape or browser.")
