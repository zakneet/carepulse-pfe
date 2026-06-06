# Architecture Diagram — OptiClinic

## Fichier principal

| Fichier | Format | Taille | Usage |
|---------|--------|--------|-------|
| `opticlinic-architecture-conceptuelle.svg` | SVG vectoriel | scalable | Insertion dans Word / LibreOffice |
| `opticlinic-architecture-conceptuelle.png` | PNG raster | 1200×820px | Impression / PDF / LaTeX |

---

## Titre de la figure

> **Figure 4.1 — Architecture conceptuelle du système OptiClinic**

---

## Légende / Caption

> Figure 4.1 — Architecture conceptuelle du système OptiClinic. Le diagramme présente les principaux acteurs, l'interface Angular, le backend Flask, la base de données MySQL, le module d'optimisation OR-Tools, le canal temps réel Socket.IO et le service d'envoi d'emails Brevo.

---

## Paragraphe d'introduction (section 4.1 du rapport)

> L'architecture conceptuelle d'OptiClinic repose sur une séparation claire entre la couche de présentation, la logique métier, la gestion des données et les services externes. Les patients interagissent avec l'interface web pour la réservation et l'accès à leur espace patient, tandis que le personnel médical exploite le tableau de bord pour la gestion du planning, des urgences et du suivi des patients. Le backend Flask centralise les traitements métier, communique avec la base MySQL, déclenche les notifications temps réel via Socket.IO et s'appuie sur OR-Tools pour l'optimisation du planning. Le service Brevo assure l'envoi des emails de confirmation et des liens d'accès à l'espace patient.

---

## Éléments représentés

### Acteurs externes
- **Patient** — accède à la réservation en ligne et à l'espace patient
- **Médecin / Personnel de santé** — utilise le tableau de bord médical
- **Administrateur** — administre l'application

### Conteneurs système
| Conteneur | Type | Rôle |
|-----------|------|------|
| Interface Web Angular | SPA | Couche présentation |
| API Backend Flask | API REST | Logique métier, authentification JWT |
| Canal temps réel Socket.IO | WebSocket | Notifications, alertes urgences |
| Module d'optimisation OR-Tools | Optimisation | Planification des créneaux |
| Base de données MySQL | BDD relationnelle | Stockage patients, rendez-vous, plannings |
| Service Email Brevo | Service externe | Envoi confirmations email |

### Flux représentés
- Demande de rendez-vous (Patient → Interface Web)
- Gestion du planning / Urgences (Médecin → Interface Web)
- Administration (Administrateur → Interface Web)
- API REST sécurisée (Interface Web → Backend Flask)
- Notifications temps réel (Interface Web ↔ Socket.IO)
- Optimisation des créneaux (Backend Flask → OR-Tools)
- Résultats d'optimisation (OR-Tools → Backend Flask)
- Lecture / écriture des données (Backend Flask → MySQL)
- Confirmation email (Backend Flask → Brevo)

---

## Comment insérer dans le rapport

### Word / LibreOffice Writer
1. Aller à la section **4.1 Architecture conceptuelle du système**
2. Supprimer le placeholder `Figure à ajouter de l'architecture ici`
3. Insérer → Image → `opticlinic-architecture-conceptuelle.png`
4. Ajuster la largeur à la largeur de la zone de texte (≈ 16 cm)
5. Ajouter la légende sous l'image : *Figure 4.1 — Architecture conceptuelle du système OptiClinic*

### LaTeX
```latex
\begin{figure}[H]
    \centering
    \includegraphics[width=\textwidth]{figures/opticlinic-architecture-conceptuelle.png}
    \caption{Architecture conceptuelle du système OptiClinic.}
    \label{fig:architecture-conceptuelle}
\end{figure}
```

---

## Régénération du diagramme

Le fichier SVG source est dans ce même répertoire : `opticlinic-architecture-conceptuelle.svg`

Pour modifier le diagramme :
- Ouvrir le fichier SVG avec **Inkscape** (gratuit) ou **Boxy SVG**
- Modifier les textes, couleurs ou flèches selon les besoins
- Exporter en PNG (File → Export PNG Image) à 150 dpi minimum pour l'impression

---

*Généré automatiquement pour le rapport PFE OptiClinic — 2025-2026*
