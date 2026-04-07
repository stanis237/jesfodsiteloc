# Django Admin Restriction TODO

**Status:** Complete

**Changes:**
1. ✅ menber_JESFOD/forms.py: CustomRegisterForm.save() now explicitly sets `user.is_staff = False`, `user.is_superuser = False`.
2. ✅ Confirmed no other code grants staff permissions (search 0 results).

**Result:**
- Only `python manage.py createsuperuser` users access /admin/.
- Registered members (bureau/reunion) cannot access Django admin panel.

**Verification:** Try login with registered user → /admin/ denied; superuser → access granted.
