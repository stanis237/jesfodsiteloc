# Navbar Consistency TODO

**Completed: 4/4 - Done**

## Steps:
1. ✅ Updated menber_JESFOD/views.py: Added `is_member_page = True` contexts.
2. ✅ Updated admin_JESFOD/views.py: Added `is_admin_page = True` contexts.
3. ✅ Updated base.html: Conditional navbar based on is_member_page/is_admin_page.
4. ✅ Navbar now adapts: Landing shows #accueil/#apropos, member pages show Dashboard/News/Membres.

Test: `python manage.py runserver`
- Landing (/) : Accueil/A Propos scroll.
- /menber/news/ : Dashboard, Actualités links.
- /adminjesfod/ : Admin Dashboard, Membres.

