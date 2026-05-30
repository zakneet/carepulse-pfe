# Prompt Lovable AI - OptiClinic (Plateforme Médicale)

Copiez-collez l'intégralité de ce texte dans Lovable (ou tout autre IA de génération de code comme Cursor, V0, etc.) pour générer votre interface frontend.

---

**Contexte du Projet :** 
Tu agis en tant qu'ingénieur UI/UX et Développeur Frontend Senior (niveau Google/Alphabet). Ta mission est de générer le frontend complet pour "OptiClinic", une plateforme web clinique haut de gamme dédiée à la gestion des rendez-vous médicaux et des dossiers patients. L'interface doit refléter les standards professionnels les plus stricts : inspiration Google Material Design 3, ergonomie clinique "Zero-Click", accessibilité maximale et une esthétique moderne et premium.

**Stack Technique attendue :**
- Frontend : Angular (version 13+)
- Styling : Tailwind CSS (ou SCSS natif si préféré, mais Tailwind est recommandé pour la rapidité)
- Composants : Angular Material ou Tailwind UI
- Icônes : Material Icons ou Lucide
- Animations : Angular Animations standard (@angular/animations)

**Directives Design System & UI/UX (Standard Pro) :**
- **Palette de Couleurs :** Design principalement "Light Mode" très clean. Utilise un Bleu médical profond et rassurant comme couleur primaire, des fonds très clairs (blanc/gris perle) pour contraster avec le texte foncé. Ajoute des touches sémantiques : Vert (Succès/Confirmé), Rouge pastel (Urgences), Orange (En attente).
- **Typographie :** Utilise "Inter" ou "Outfit". Une hiérarchie visuelle stricte (H1 massifs, texte de corps lisible).
- **Composants "Premium" :** Utilise de l'effet "Glassmorphism" subtil sur les modales, des ombres douces (soft shadows) sur les cartes pour créer de la profondeur, et des transitions hover élégantes.
- L'interface doit être 100% responsive (Mobile-first pour les patients, Desktop-first pour les médecins).

**Architecture et Vues à générer :**

Crée une application complète avec le routage suivant :

### 1. Module d'Authentification (`/login`)
- Un layout scindé (Split Screen) : Une belle image médicale abstraite/générative à gauche, le formulaire à droite.
- Le formulaire utilise des "Tabs" (Onglets) pour séparer la connexion : "Espace Patient" et "Personnel Médical".
- **Règle stricte :** L'onglet "Personnel Médical" doit obligatoirement inclure un champ supplémentaire "Code d'accès sécurisé" avec une icône de cadenas.

### 2. Portail Patient (`/patient/dashboard`)
- **Header :** Salutation personnalisée ("Bonjour, Jean Dupont").
- **Dashboard :** Une interface en grille (Grid). Une carte "Hero" montrant le prochain rendez-vous avec un compte à rebours ou une mise en évidence.
- **Réservation (Wizard) :** Un bouton primaire "Nouveau Rendez-vous" qui ouvre une belle modale en plusieurs étapes (Stepper) : 1. Choix Spécialité -> 2. Sélection du Médecin (avec photo/avatar) -> 3. Calendrier interactif des disponibilités -> 4. Confirmation.
- **Historique :** Une liste sous forme de cartes minimalistes affichant les rendez-vous passés avec leur statut.

### 3. Portail Personnel Médical (`/medical-staff/dashboard`)
- **Layout :** Un vrai "Cockpit" clinique. Une Sidebar rétractable (Planning, Dossiers, Urgences, Paramètres) + une Topbar (Recherche globale, Notifications, Statut du médecin).
- **Le Planning (Calendrier) :** C'est la pièce maîtresse. Implémente une vue calendrier (Semaine/Jour). Les créneaux de RDV doivent être des "blocks" cliquables avec des codes couleurs selon le type de visite.
- **Dossiers Patients :** Une Data Table (Tableau de données) riche. Recherche en temps réel par CIN (Numéro d'identité), filtres, pagination. 
- **Vue Détail Patient :** En cliquant sur une ligne du tableau, faire glisser un panneau latéral (Slide-over) très complet : Info patient en haut, historique des consultations, champ de saisie rapide pour ajouter des notes médicales.

### 4. Mode Urgence
- Intègre un Toggle ou Bouton "Urgence" rouge dans le header du médecin. Quand il est activé, l'interface doit subtilement changer de thème (ex: bordures rouges) et mettre en avant les protocoles d'action rapide ou la liste des patients critiques.

**Intégration et Qualité du Code :**
- Le code doit être structuré par "Features" (modules).
- Prépare l'architecture pour qu'elle puisse consommer facilement une API REST (Backend Flask existant). Utilise des services factices (mock data) en attendant la vraie connexion.
- Utilise TypeScript de manière stricte pour typer les interfaces (User, Patient, Appointment).

Surprends-moi avec un design digne d'une startup HealthTech de la Silicon Valley !
