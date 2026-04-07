# TODO: Move Login to Dedicated Page

## Plan Steps:
- [x] Step 1: Edit JESFOD_PROJECT/JESFOD_PROJECT/templates/home.html - Remove {% include 'login_form_partial.html' %} and replace with login button linking to /menber/login/
- [x] Step 2: Edit JESFOD_PROJECT/menber_JESFOD/templates/menber_JESFOD/home.html - Same replacement
- [ ] Step 3: Test login flow: python JESFOD_PROJECT/manage.py runserver, visit /, click login → /menber/login/, submit form
- [ ] Step 4: Optional cleanup: delete unused login_form_partial.html and registration/login.html
- [ ] Done: Mark complete and attempt_completion

Current progress: Steps 1-2 complete. Step 3: Testing recommended. Navbar already links to login page correctly.
