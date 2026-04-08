# Fix 403 on POST /menber/register/

**Progress:** Step 0 done

## Steps:
- [x] 0. Create this TODO.md
- [x] 1. Fix CustomRegisterForm Meta.fields in menber_JESFOD/forms.py (remove non-User fields from fields tuple)\n- [x] 2. Update JESFOD_PROJECT/settings.py: ALLOWED_HOSTS = ['*']\n- [x] 3. Remove fake form handler from static/js/main.js (preventDefault causing no POST)\n- [x] 3. Add debug logging to menber_JESFOD/views.py register
- [ ] 3. Add debug logging to menber_JESFOD/views.py register view (print form.is_valid(), errors)
- [ ] 4. Run python manage.py shell to list existing Users.usernames/emails
- [ ] 5. Restart server: cd JESFOD_PROJECT && python manage.py runserver --verbosity=2
- [x] 6. Fixed forms.py Meta indentation + reverted urls.py to original views (now syntax safe)
- [ ] 7. Test POST /menber/register/ with NEW unique username/email
- [ ] 7. Check logs for errors, confirm success
- [ ] 8. Remove debug prints, mark complete

**Notes:**
- Template has CSRF token ✓
- Form handles FILES ✓
- No permission decorator ✓

