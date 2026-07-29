/**
 * LUMA — Main Application Client Script
 * Theme Management, Micro-interactions, Accessibility
 */

(function () {
    'use strict';

    function getStoredTheme() {
        return localStorage.getItem('luma-theme');
    }

    function setStoredTheme(theme) {
        localStorage.setItem('luma-theme', theme);
    }

    function getPreferredTheme() {
        const storedTheme = getStoredTheme();
        if (storedTheme) {
            return storedTheme;
        }
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    function applyTheme(theme) {
        const root = document.documentElement;
        if (theme === 'dark') {
            root.classList.add('dark');
        } else {
            root.classList.remove('dark');
        }
        updateThemeControls(theme);
    }

    function updateThemeControls(theme) {
        // 1. Header/Sidebar theme toggle icons
        const toggleBtns = document.querySelectorAll('.luma-theme-toggle');
        toggleBtns.forEach(btn => {
            const sunIcon = btn.querySelector('.theme-icon-sun');
            const moonIcon = btn.querySelector('.theme-icon-moon');
            if (sunIcon && moonIcon) {
                if (theme === 'dark') {
                    sunIcon.classList.remove('hidden');
                    moonIcon.classList.add('hidden');
                    btn.setAttribute('aria-label', 'Switch to Light Theme');
                    btn.setAttribute('title', 'Switch to Light Theme');
                } else {
                    sunIcon.classList.add('hidden');
                    moonIcon.classList.remove('hidden');
                    btn.setAttribute('aria-label', 'Switch to Dark Theme');
                    btn.setAttribute('title', 'Switch to Dark Theme');
                }
            }
        });

        // 2. Settings page theme radio options sync
        const themeRadios = document.querySelectorAll('input[name="theme"]');
        themeRadios.forEach(radio => {
            if (radio.value === theme) {
                radio.checked = true;
            }
        });
    }

    window.setTheme = function (theme) {
        setStoredTheme(theme);
        applyTheme(theme);
    };

    window.toggleTheme = function () {
        const currentTheme = document.documentElement.classList.contains('dark') ? 'dark' : 'light';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        window.setTheme(newTheme);
    };

    // Apply theme immediately on script execute to prevent flash of unstyled content
    const initialTheme = getPreferredTheme();
    applyTheme(initialTheme);

    // Listen for OS theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        if (!getStoredTheme()) {
            applyTheme(e.matches ? 'dark' : 'light');
        }
    });

    // Re-sync controls when DOM is ready
    document.addEventListener('DOMContentLoaded', () => {
        const activeTheme = document.documentElement.classList.contains('dark') ? 'dark' : 'light';
        updateThemeControls(activeTheme);

        if (window.lucide) {
            lucide.createIcons();
        }
    });
})();
