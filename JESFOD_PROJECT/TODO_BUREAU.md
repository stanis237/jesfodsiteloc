# Bureau Gallery Implementation - Bureau Membres Galerie et Activités

Status: Started

## Detailed Steps from Approved Plan:

1. [x] Create/update this TODO_BUREAU.md with task list

3. [x] Run migrations: `cd c:/Users/Lenovo/OneDrive/Desktop/djangoproject/JESFOD/JESFOD_PROJECT && python manage.py makemigrations menber_JESFOD && python manage.py migrate` ✅
4. [ ] Edit `JESFOD_PROJECT/admin_JESFOD/views.py`: Update MemberCreateView.fields and MemberUpdateView.fields to `['name', 'email', 'phone', 'address', 'profile_photo', 'school_level', 'role', 'activities', 'is_certified']`
5. [ ] Edit `JESFOD_PROJECT/admin_JESFOD/templates/admin_JESFOD/member_form.html`: Add photo preview logic
6. [ ] Read/edit `JESFOD_PROJECT/menber_JESFOD/views.py`: Ensure home view passes `bureau_members = Member.objects.filter(role='bureau')` to main home context
7. [ ] Edit `JESFOD_PROJECT/JESFOD_PROJECT/templates/home.html`: In bureau section, use `member.profile_photo.url` if exists (with thumbnail), display `member.activities`
8. [ ] Edit `JESFOD_PROJECT/admin_JESFOD/admin.py`: Register menber_JESFOD.Member with list_filter/display fields for photo/role
9. [ ] Test: Login as bureau admin, add member with role='bureau', photo, activities; verify on home page
10. [x] Update this TODO on completion, remove checked items

Next step progress will update this file.

