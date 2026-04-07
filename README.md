# JESFOD - Site Web de Gestion de l'Association JESFOD

[![Django](https://img.shields.io/badge/Django-4.x-blue)](https://www.djangoproject.com/)

## 📖 Aperçu du Projet
**JESFOD** est une application web Django pour digitaliser l'association JESFOD, rendant accessible les activités, actualités et gestion des membres pour le développement de notre village. 

**Objectifs (du Cahier des Charges)**:
- Authentification: Inscription/connexion/gestion profil.
- Actualités: Publication par bureau via dashboard.
- Administration: Suivi complet des activités.
- Design: Responsive, bleu (#007BFF)/blanc/gris.

## 📁 Structure du Projet
```
JESFOD/
├── DOC/CAHIER DE CHARGE JESFOD.docx     # Spécifications principales
├── JESFOD_PROJECT/                      # Projet Django principal
│   ├── admin_JESFOD/                    # Admin: Members, News, Gallery, Dashboard
│   │   ├── models.py
│   │   ├── views.py
│   │   └── templates/admin_JESFOD/
│   ├── menber_JESFOD/                   # Membres: Auth, Profiles, News, Events
│   │   ├── models.py                    # Member, News, Event, Profile
│   │   ├── views.py
│   │   ├── forms.py
│   │   └── templates/menber_JESFOD/     # home.html, profile.html, news_list.html
│   ├── JESFOD_PROJECT/                  # Settings, URLs
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── templates/                   # base.html (SEO metas), home.html
│   ├── media/                           # Uploads: profiles/, news/, gallery/
│   ├── static/                          # CSS (style.css), JS (main.js), images/
│   ├── db.sqlite3                       # Base de données locale
│   └── manage.py
├── TODO_SEO.md, TODO_*.md               # Suivi des tâches en cours
├── robots.txt, sitemap.xml              # SEO
└── README.md                            # Ce fichier
```

## 🚀 Fonctionnalités
| Module | Description |
|--------|-------------|
| **Auth** | Inscription (`/menber/register/`), Login (`/menber/login/`), Profile (`/menber/profile/`) |
| **Membres** | CRUD via admin, photos profil, niveau scolaire, activités, certifications |
| **Actualités** | Liste/détail (`/menber/news/`), upload images, publication par bureau |
| **Galerie** | Gestion photos événements |
| **Admin Dashboard** | `/admin/` - Members/News/Gallery/Certifications en attente |
| **Événements** | Modèle Event |
| **SEO** | Metas OG/JSON-LD, robots.txt, sitemap.xml ✅ |

## 🛠 Installation & Lancement (Local)
1. **Environnement**:
   ```
   cd JESFOD_PROJECT
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install django pillow  # + autres si requirements.txt
   ```

2. **Migrations & Superuser**:
   ```
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

3. **Static & Serveur**:
   ```
   python manage.py collectstatic --noinput
   python manage.py runserver
   ```
   Ouvrir: http://127.0.0.1:8000/

## 📋 Tâches en Cours (TODOs Principales)
- [ ] `TODO_HERO_SLIDESHOW.md`: Slider images hero.
- [ ] `TODO_NEWS_DETAIL.md`: Vue détail news.
- [ ] `TODO_FIX_MEMBER_CREATE.md`: Fix création membre.
- [ ] `TODO_BUREAU.md`: Rôles bureau.
- Voir tous les [TODO_*.md](JESFOD_PROJECT/) pour détails.

**Auth Plan (redme.md)**: Majoritairement ✅ (register/login/dashboard).

## 📄 Documentation Complète
- **Cahier des Charges**: [DOC/CAHIER DE CHARGE JESFOD.docx](DOC/CAHIER DE CHARGE JESFOD.docx)
- **Auth Dev**: [menber_JESFOD/redme.md](JESFOD_PROJECT/menber_JESFOD/redme.md)
- **SEO**: [TODO_SEO.md](TODO_SEO.md) ✅
- **Autres**: Galerie TODO_PROFILE_PHOTOS.md, etc.

## 🔮 Déploiement
- Heroku/PythonAnywhere/Vercel (ajouter PostgreSQL).
- `DEBUG=False`, `ALLOWED_HOSTS`, `requirements.txt`.

## 🤝 Contributeurs
Développement en cours. Contactez pour + d'infos.

**Site Live**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/) (local)  
**Dernière MAJ**: Documentation centralisée ✅
