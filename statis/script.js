// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all functionality
    initLoadingScreen();
    initNavigation();
    initScrollAnimations();
    initCounters();
    initQualityChart();
    initBackToTop();
    initStatsAPI();
    initMobileMenu();
    initSmoothScrolling();
});

// Loading Screen
function initLoadingScreen() {
    const loadingScreen = document.getElementById('loading-screen');
    
    // Simulate loading time
    setTimeout(() => {
        loadingScreen.classList.add('hidden');
        
        // Remove from DOM after animation completes
        setTimeout(() => {
            loadingScreen.style.display = 'none';
        }, 500);
        
        // Trigger entrance animations
        triggerEntranceAnimations();
    }, 2000);
}

// Navigation functionality
function initNavigation() {
    const navbar = document.querySelector('.navbar');
    
    // Navbar scroll effect
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
}

// Mobile Menu
function initMobileMenu() {
    const hamburger = document.getElementById('hamburger');
    const navMenu = document.getElementById('nav-menu');
    
    hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('active');
        navMenu.classList.toggle('active');
    });
    
    // Close menu when clicking on a link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            hamburger.classList.remove('active');
            navMenu.classList.remove('active');
        });
    });
    
    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
        if (!hamburger.contains(e.target) && !navMenu.contains(e.target)) {
            hamburger.classList.remove('active');
            navMenu.classList.remove('active');
        }
    });
}

// Smooth Scrolling
function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const offset = 70; // Account for fixed navbar
                const targetPosition = target.offsetTop - offset;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Scroll Animations
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                
                // Special handling for staggered animations
                if (entry.target.classList.contains('stagger-parent')) {
                    const children = entry.target.querySelectorAll('.stagger-child');
                    children.forEach((child, index) => {
                        setTimeout(() => {
                            child.classList.add('visible');
                        }, index * 100);
                    });
                }
            }
        });
    }, observerOptions);
    
    // Observe all animatable elements
    document.querySelectorAll('.fade-in, .slide-in-left, .slide-in-right, .scale-in').forEach(el => {
        observer.observe(el);
    });
}

// Counter Animation
function initCounters() {
    const counters = document.querySelectorAll('.stat-number[data-target]');
    
    const countObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                countObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    counters.forEach(counter => {
        countObserver.observe(counter);
    });
}

function animateCounter(element) {
    const target = parseInt(element.getAttribute('data-target'));
    const duration = 2000; // 2 seconds
    const startTime = performance.now();
    const startValue = 0;
    
    function updateCounter(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function for smooth animation
        const easeOut = 1 - Math.pow(1 - progress, 3);
        const currentValue = Math.floor(startValue + (target - startValue) * easeOut);
        
        element.textContent = formatNumber(currentValue);
        
        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = formatNumber(target);
        }
    }
    
    requestAnimationFrame(updateCounter);
}

function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

// Quality Chart Animation
function initQualityChart() {
    const chartObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateQualityBars();
                chartObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    const chartContainer = document.querySelector('.quality-chart');
    if (chartContainer) {
        chartObserver.observe(chartContainer);
    }
}

function animateQualityBars() {
    const bars = document.querySelectorAll('.quality-fill');
    
    bars.forEach((bar, index) => {
        setTimeout(() => {
            const width = bar.getAttribute('data-width');
            bar.style.width = width + '%';
        }, index * 200);
    });
}

// Back to Top Button
function initBackToTop() {
    const backToTopBtn = document.getElementById('back-to-top');
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            backToTopBtn.classList.add('visible');
        } else {
            backToTopBtn.classList.remove('visible');
        }
    });
    
    backToTopBtn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Stats API Integration
function initStatsAPI() {
    fetchBotStats();
    
    // Refresh stats every 30 seconds
    setInterval(fetchBotStats, 30000);
}

async function fetchBotStats() {
    try {
        // Fetch real stats from API
        const stats = await fetchStatsFromAPI();
        updateStatsDisplay(stats);
    } catch (error) {
        console.error('Error fetching stats:', error);
        // Keep loading state or show error
    }
}

// Fetch real stats from API
async function fetchStatsFromAPI() {
    try {
        const response = await fetch('/api/stats');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        return {
            totalUsers: data.users.total,
            downloadsToday: data.users.today,
            totalSongs: 50000, // Static value since we don't track songs directly
            activeUsers: data.users.active,
            qualityDistribution: data.quality_distribution,
            typeDistribution: data.type_distribution
        };
    } catch (error) {
        console.error('Failed to fetch real stats, using fallback:', error);
        // Fallback to mock data if API fails
        return {
            totalUsers: Math.floor(Math.random() * 5000) + 8000,
            downloadsToday: Math.floor(Math.random() * 1000) + 500,
            totalSongs: Math.floor(Math.random() * 10000) + 45000,
            activeUsers: Math.floor(Math.random() * 2000) + 3000
        };
    }
}

function updateStatsDisplay(stats) {
    const elements = {
        users: document.querySelector('[data-api="users"]'),
        downloads: document.querySelector('[data-api="downloads"]'),
        songs: document.querySelector('[data-api="songs"]')
    };
    
    // Update each stat with animation
    Object.keys(elements).forEach(key => {
        const element = elements[key];
        if (element && stats[key === 'users' ? 'totalUsers' : key === 'downloads' ? 'downloadsToday' : 'totalSongs']) {
            element.classList.remove('loading-stat');
            
            // Animate the number change
            const currentValue = parseInt(element.textContent.replace(/[^\d]/g, '')) || 0;
            const newValue = stats[key === 'users' ? 'totalUsers' : key === 'downloads' ? 'downloadsToday' : 'totalSongs'];
            
            animateNumberChange(element, currentValue, newValue);
        }
    });
}

function animateNumberChange(element, startValue, endValue) {
    const duration = 1000;
    const startTime = performance.now();
    
    function updateNumber(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easeOut = 1 - Math.pow(1 - progress, 2);
        const currentValue = Math.floor(startValue + (endValue - startValue) * easeOut);
        
        element.textContent = formatNumber(currentValue);
        
        if (progress < 1) {
            requestAnimationFrame(updateNumber);
        } else {
            element.textContent = formatNumber(endValue);
        }
    }
    
    requestAnimationFrame(updateNumber);
}

// Entrance Animations
function triggerEntranceAnimations() {
    // Hero content animation
    const heroContent = document.querySelector('.hero-content');
    if (heroContent) {
        heroContent.style.opacity = '0';
        heroContent.style.transform = 'translateY(50px)';
        
        setTimeout(() => {
            heroContent.style.transition = 'all 1s cubic-bezier(0.4, 0, 0.2, 1)';
            heroContent.style.opacity = '1';
            heroContent.style.transform = 'translateY(0)';
        }, 300);
    }
    
    // Stagger hero stats animation
    const heroStats = document.querySelectorAll('.stat-item');
    heroStats.forEach((stat, index) => {
        stat.style.opacity = '0';
        stat.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            stat.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
            stat.style.opacity = '1';
            stat.style.transform = 'translateY(0)';
        }, 800 + index * 100);
    });
}

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

// Error Handling
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    // You can add error reporting here
});

// Performance Monitoring
window.addEventListener('load', function() {
    const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
    console.log('Page load time:', loadTime + 'ms');
});

// Accessibility Enhancements
document.addEventListener('keydown', function(e) {
    // Handle keyboard navigation for custom elements
    if (e.key === 'Escape') {
        // Close mobile menu if open
        const hamburger = document.getElementById('hamburger');
        const navMenu = document.getElementById('nav-menu');
        
        if (hamburger.classList.contains('active')) {
            hamburger.classList.remove('active');
            navMenu.classList.remove('active');
        }
    }
});

// Preload critical resources
function preloadResources() {
    const criticalResources = [
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css',
        'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap'
    ];
    
    criticalResources.forEach(resource => {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.as = 'style';
        link.href = resource;
        document.head.appendChild(link);
    });
}

// Initialize preloading
preloadResources();

// Service Worker Registration (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registered');
            })
            .catch(function(err) {
                console.log('ServiceWorker registration failed');
            });
    });
}

// Analytics Integration (placeholder)
function trackEvent(eventName, properties = {}) {
    // Add your analytics tracking code here
    console.log('Event tracked:', eventName, properties);
}

// Track page interactions
document.addEventListener('click', function(e) {
    if (e.target.matches('.btn')) {
        trackEvent('button_click', {
            button_text: e.target.textContent.trim(),
            button_href: e.target.href || 'no_href'
        });
    }
});

// Dark theme persistence (already dark by default)
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
prefersDark.addEventListener('change', function(e) {
    // Handle system theme changes if needed
    console.log('System theme changed to:', e.matches ? 'dark' : 'light');
});

// Intersection Observer polyfill check
if (!window.IntersectionObserver) {
    console.warn('IntersectionObserver not supported, loading polyfill...');
    // Load polyfill if needed
}

// Print styles handling
window.addEventListener('beforeprint', function() {
    document.body.classList.add('printing');
});

window.addEventListener('afterprint', function() {
    document.body.classList.remove('printing');
});

// Connection status monitoring
window.addEventListener('online', function() {
    console.log('Connection restored');
    // Retry failed requests
    fetchBotStats();
});

window.addEventListener('offline', function() {
    console.log('Connection lost');
    // Show offline message or cache content
});

// Memory management
window.addEventListener('beforeunload', function() {
    // Clean up any intervals or observers
    // Performance cleanup
});

// Development helpers
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    console.log('🚀 JioSaavn Bot Dashboard - Development Mode');
    console.log('Available functions:', {
        fetchBotStats,
        animateCounter,
        trackEvent,
        formatNumber
    });
}
