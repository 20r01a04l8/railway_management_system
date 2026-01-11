// Quick fix for login/register page navigation issues
// Add this script to the end of your index.html file

// Force show page function for debugging
window.forceShowPage = function(pageId) {
    console.log(`Force showing page: ${pageId}`);
    document.querySelectorAll('.page').forEach(p => {
        p.style.display = 'none';
        p.classList.remove('active');
    });
    const page = document.getElementById(pageId);
    if (page) {
        page.style.display = 'block';
        page.classList.add('active');
        console.log(`Page ${pageId} should now be visible`);
    } else {
        console.log(`Page ${pageId} not found!`);
    }
};

// Test page navigation
window.testPageNavigation = function() {
    console.log('Testing page navigation...');
    const pages = ['home', 'login', 'register'];
    pages.forEach(pageId => {
        const page = document.getElementById(pageId);
        console.log(`Page ${pageId}:`, page ? 'exists' : 'missing');
        if (page) {
            console.log(`  - Display: ${window.getComputedStyle(page).display}`);
            console.log(`  - Classes: ${page.className}`);
        }
    });
};

// Enhanced showPage function with better error handling
function showPageFixed(pageId) {
    try {
        console.log('Attempting to show page:', pageId);
        
        // Clear any existing errors when switching pages
        document.querySelectorAll('.alert').forEach(alert => alert.style.display = 'none');
        
        // Hide all pages first
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('active');
            page.style.display = 'none';
        });
        
        // Show the selected page
        const targetPage = document.getElementById(pageId);
        if (targetPage) {
            targetPage.classList.add('active');
            targetPage.style.display = 'block';
            console.log('Successfully showed page:', pageId);
        } else {
            console.error('Page not found:', pageId);
            alert('Page not found: ' + pageId);
        }
        
        // Reset forms when showing login/register pages
        if (pageId === 'login') {
            const loginForm = document.getElementById('loginForm');
            if (loginForm) loginForm.reset();
        }
        if (pageId === 'register') {
            const registerForm = document.getElementById('registerForm');
            if (registerForm) registerForm.reset();
        }
        
    } catch (error) {
        console.error('Error in showPage:', error);
        alert('Error showing page: ' + error.message);
    }
}

// Replace the original showPage function
if (typeof showPage !== 'undefined') {
    window.originalShowPage = showPage;
}
window.showPage = showPageFixed;

console.log('Page navigation fix loaded. Try using showPage("login") or showPage("register")');