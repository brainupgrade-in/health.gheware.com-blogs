/**
 * Template Loader for Health Gheware Blog (GitHub Pages)
 * Loads HTML templates (header, footer) dynamically to avoid duplication
 */

(function() {
    'use strict';

    // Detect base URL from script location or use window.SITE_BASE_URL if defined
    function getBaseUrl() {
        if (window.SITE_BASE_URL) {
            return window.SITE_BASE_URL;
        }
        // Try to detect from current script
        const scripts = document.getElementsByTagName('script');
        for (let script of scripts) {
            const src = script.src;
            if (src.includes('template-loader.js')) {
                // Extract base URL by removing /js/template-loader.js
                return src.replace(/js\/template-loader\.js.*$/, '');
            }
        }
        // Fallback: use relative path from root
        return '';
    }

    const SITE_BASE = getBaseUrl();

    /**
     * Load a template from the templates directory
     * @param {string} templateName - Name of the template file (without .html extension)
     * @param {string} targetSelector - CSS selector for the container element
     * @param {object} options - Optional configuration
     * @returns {Promise<void>}
     */
    async function loadTemplate(templateName, targetSelector, options = {}) {
        const {
            position = 'afterbegin', // 'beforebegin', 'afterbegin', 'beforeend', 'afterend'
            baseUrl = SITE_BASE + 'templates/',
            onLoad = null
        } = options;

        try {
            const response = await fetch(`${baseUrl}${templateName}.html`);

            if (!response.ok) {
                throw new Error(`Failed to load template: ${templateName}`);
            }

            const html = await response.text();
            const targetElement = document.querySelector(targetSelector);

            if (!targetElement) {
                console.error(`Target element not found: ${targetSelector}`);
                return;
            }

            // Create a temporary container to parse the HTML
            const tempContainer = document.createElement('div');
            tempContainer.innerHTML = html;

            // Extract and store scripts before inserting HTML
            const scripts = tempContainer.querySelectorAll('script');
            const scriptContents = [];
            scripts.forEach(script => {
                scriptContents.push(script.textContent);
                script.remove();
            });

            // Insert the HTML (without scripts)
            targetElement.insertAdjacentHTML(position, tempContainer.innerHTML);

            // Execute the scripts after HTML is inserted
            scriptContents.forEach(scriptContent => {
                if (scriptContent.trim()) {
                    const newScript = document.createElement('script');
                    newScript.textContent = scriptContent;
                    document.body.appendChild(newScript);
                }
            });

            // Execute callback if provided
            if (typeof onLoad === 'function') {
                onLoad();
            }

            console.log(`✓ Template loaded: ${templateName}`);
        } catch (error) {
            console.error(`Error loading template ${templateName}:`, error);
        }
    }

    /**
     * Load header template
     */
    async function loadHeader() {
        await loadTemplate('header', 'body', {
            position: 'afterbegin',
            onLoad: () => {
                // Update tagline based on page
                const taglineElement = document.getElementById('header-tagline');
                if (taglineElement) {
                    const path = window.location.pathname;
                    if (path.includes('/blog')) {
                        taglineElement.textContent = 'Blog';
                    } else {
                        taglineElement.textContent = 'Data Analytics';
                    }
                }

                // Add scroll effect to header
                const header = document.querySelector('.header-premium');
                if (header) {
                    window.addEventListener('scroll', () => {
                        if (window.pageYOffset > 100) {
                            header.classList.add('scrolled');
                        } else {
                            header.classList.remove('scrolled');
                        }
                    });
                }
            }
        });
    }

    /**
     * Load footer template
     */
    async function loadFooter() {
        await loadTemplate('footer', 'body', {
            position: 'beforeend',
            onLoad: () => {
                // Hide Trade Gheware newsletter on Health Gheware blog posts
                const path = window.location.pathname;
                const tradeNewsletter = document.querySelector('.footer-newsletter-trade');

                if (tradeNewsletter) {
                    // Check if this is a health blog post or health-related page
                    const isHealthBlog = path.includes('/blog/posts/') &&
                                        (path.includes('health-gheware') ||
                                         path.includes('time-in-range') ||
                                         path.includes('diabetes') ||
                                         path.includes('sleep-affects-blood-sugar'));

                    if (isHealthBlog) {
                        // Hide trade newsletter on health blog posts
                        tradeNewsletter.style.display = 'none';
                    }
                }
            }
        });
    }

    /**
     * Load author bio template (for blog posts)
     */
    async function loadAuthorBio() {
        // Only load if there's an author-bio-placeholder
        const placeholder = document.getElementById('author-bio-placeholder');
        if (placeholder) {
            await loadTemplate('author-bio', '#author-bio-placeholder', {
                position: 'afterbegin',
                onLoad: () => {
                    // Fix image paths to use correct base URL
                    const authorImg = placeholder.querySelector('.author-img');
                    if (authorImg) {
                        authorImg.src = SITE_BASE + 'assets/images/rajesh-gheware.jpg';
                        authorImg.onerror = function() {
                            this.src = SITE_BASE + 'images/rajesh-gheware.jpg';
                        };
                    }
                }
            });
        }
    }

    /**
     * Load disclaimer template (for blog posts)
     */
    async function loadDisclaimer() {
        // Only load if there's a disclaimer-placeholder
        const placeholder = document.getElementById('disclaimer-placeholder');
        if (placeholder) {
            await loadTemplate('disclaimer', '#disclaimer-placeholder', {
                position: 'afterbegin'
            });
        }
    }

    /**
     * Initialize templates
     * Call this function when DOM is ready
     */
    async function initTemplates() {
        console.log('🔄 Loading templates...');

        // Load header and footer in parallel (always)
        // Load author bio and disclaimer if placeholders exist (blog posts only)
        await Promise.all([
            loadHeader(),
            loadFooter(),
            loadAuthorBio(),
            loadDisclaimer()
        ]);

        console.log('✅ All templates loaded');

        // Dispatch custom event to notify that templates are ready
        document.dispatchEvent(new CustomEvent('templatesLoaded'));
    }

    // Auto-initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTemplates);
    } else {
        // DOM already loaded
        initTemplates();
    }

    // Export for manual usage if needed
    window.GhewareTemplates = {
        loadTemplate,
        loadHeader,
        loadFooter,
        loadAuthorBio,
        loadDisclaimer,
        init: initTemplates
    };
})();
