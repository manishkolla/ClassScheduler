// theme.js

const themeToggle = document.getElementById('theme-toggle');
const body = document.body;

// Check if the theme preference is saved in localStorage
const currentTheme = localStorage.getItem('theme');

// If a theme preference exists in localStorage, apply it
if (currentTheme) {
    body.classList.add(currentTheme);
}

// Add event listener to the theme toggle button
themeToggle.addEventListener('click', () => {
    // Toggle between 'light' and 'dark' themes
    body.classList.toggle('dark');

    // Save the theme preference in localStorage
    const theme = body.classList.contains('dark') ? 'dark' : '';
    localStorage.setItem('theme', theme);
});
