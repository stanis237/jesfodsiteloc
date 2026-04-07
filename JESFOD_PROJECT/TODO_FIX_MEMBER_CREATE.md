# Fix MemberCreateView IntegrityError (user_id NOT NULL)

## Steps:
- [x] 1. Create this TODO.md
- [ ] 2. Edit admin_JESFOD/views.py: Override form_valid() in MemberCreateView to set instance.user = request.user
- [ ] 3. Test: Login as bureau user, POST to /adminjesfod/members/create/, submit form (no error)
- [ ] 4. Verify: Check new Member in list/dashboard has correct user_id
- [x] 5. Mark complete

**Current progress: Step 1 done**
