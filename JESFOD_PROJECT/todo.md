# Fix Template Error & Reduce Profile Image Size
## Status: In Progress

### 1. [ ] Fix base.html
- Remove duplicate {% block title %} tags
- Fix UTF-8 encoding (replace smart quotes « » with ", non-breaking spaces)
- Ensure single {% block title %}JESFOD...{% endblock %}

### 2. [ ] Reduce profile images in home.html
- Welcome member card: 120px -> 80px width/height
- Bureau member cards: 100px -> 70px width/height
- Adjust padding/margins for better text visibility

### 3. [ ] Update CSS (if needed)
- Add .bureau-member-img class fallback

### 4. [ ] Test & Verify
- Restart server: python manage.py runserver
- Visit http://127.0.0.1:8000/ - no 500 error
- Check bureau cards show name/role/email/phone/activities fully
- collectstatic if CSS changes

### 5. [ ] Complete
