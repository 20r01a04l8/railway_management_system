# Login/Register Page Access Issue - Troubleshooting Guide

## Quick Solutions

### Option 1: Use the Debug Version (Recommended)
1. Open `frontend/debug.html` in your browser
2. This simplified version should show login/register pages correctly
3. Test the functionality there first

### Option 2: Fix the Original Frontend
1. Open `frontend/index.html` in your browser
2. Press F12 to open Developer Tools
3. Go to the Console tab
4. Type: `showPage('login')` and press Enter
5. If that doesn't work, try: `forceShowPage('login')`

### Option 3: Start Everything with the Batch File
1. Double-click `start-debug.bat` in the project root
2. This will start the backend and open the debug frontend automatically

## Common Issues and Solutions

### Issue 1: Pages Not Switching
**Symptoms:** Clicking Login/Register buttons does nothing
**Solution:** 
- Open browser console (F12)
- Look for JavaScript errors
- Try typing `testPageNavigation()` in console
- Use `forceShowPage('login')` to force show the page

### Issue 2: Backend Not Running
**Symptoms:** Login/Register forms don't submit, network errors
**Solution:**
- Make sure backend is running on http://localhost:8000
- Run: `cd backend && python main.py`
- Check if you see "Uvicorn running on http://0.0.0.0:8000"

### Issue 3: CSS/Display Issues
**Symptoms:** Pages exist but are not visible
**Solution:**
- Check if pages have `display: none` in CSS
- Try adding `!important` to the active page CSS
- Use browser inspector to check element styles

## Manual Testing Steps

1. **Test Page Elements Exist:**
   ```javascript
   console.log('Login page:', document.getElementById('login'));
   console.log('Register page:', document.getElementById('register'));
   ```

2. **Test Page Switching:**
   ```javascript
   showPage('login');
   // Wait 2 seconds
   showPage('register');
   ```

3. **Test Backend Connection:**
   ```javascript
   fetch('http://localhost:8000/health')
     .then(r => r.json())
     .then(d => console.log('Backend:', d))
     .catch(e => console.error('Backend error:', e));
   ```

## Files Created for Debugging

1. **debug.html** - Simplified version with working login/register
2. **page-fix.js** - JavaScript fixes for the original frontend
3. **start-debug.bat** - Automated startup script
4. **troubleshooting.md** - This guide

## Next Steps

1. Try the debug.html version first
2. If that works, the issue is in the original index.html
3. If debug.html doesn't work, check if backend is running
4. Use browser developer tools to identify specific errors

## Backend Requirements

Make sure these are installed in your backend:
```bash
cd backend
pip install fastapi uvicorn sqlalchemy pymysql python-jose[cryptography] passlib[bcrypt] python-multipart
```

## Database Requirements

Make sure MySQL is running and the database exists:
```sql
CREATE DATABASE railway_db;
```

Run the schema and sample data:
```bash
mysql -u root -p railway_db < database/schema.sql
mysql -u root -p railway_db < database/sample_data.sql
```