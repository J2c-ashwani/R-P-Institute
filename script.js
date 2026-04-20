// ===== R & P Institute - Campaign Script =====

document.addEventListener('DOMContentLoaded', () => {
    initNavbar();
    initParticles();
    initCounters();
    initAOS();
    initFloatingButton();
    initMobileMenu();
    initGeoCurrency();
});

// ===== NAVBAR =====
function initNavbar() {
    const navbar = document.getElementById('navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 80) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
}

// ===== MOBILE MENU =====
function initMobileMenu() {
    const hamburger = document.getElementById('hamburger');
    const mobileMenu = document.getElementById('mobile-menu');

    hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('active');
        mobileMenu.classList.toggle('active');
    });

    mobileMenu.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            hamburger.classList.remove('active');
            mobileMenu.classList.remove('active');
        });
    });
}

// ===== GEO CURRENCY DETECTION =====
function initGeoCurrency() {
    // Detect timezone to determine USA/Canada vs India
    const tz = Intl.DateTimeFormat().resolvedOptions().timeZone || '';
    const lang = (navigator.language || navigator.userLanguage || '').toLowerCase();

    const isNorthAmerica = tz.startsWith('America/') || 
                           lang.startsWith('en-us') || 
                           lang.startsWith('en-ca');

    if (isNorthAmerica) {
        switchToUSD();
    }
}

function switchToUSD() {
    // Currency mapping: INR → USD (approximate for donation context)
    const conversions = {
        '₹500': '$500',
        '₹2,000': '$1,200',
        '₹10,000': '$5,000',
        '₹50,000+': '$10,000+',
        '₹70 Lakh': '$85,000',
        '₹40 Lakh': '$48,000',
        '₹30 Lakh': '$36,000',
        '₹20 Lakh': '$24,000',
        '₹2 Crore': '$240,000',
        '₹2,00,00,000': '$240,000',
        '₹0': '$0',
    };

    // Update tier amounts
    document.querySelectorAll('.tier-amount').forEach(el => {
        const txt = el.textContent.trim();
        if (conversions[txt]) el.textContent = conversions[txt];
    });

    // Update fund breakdown amounts
    document.querySelectorAll('.fund-amount').forEach(el => {
        const txt = el.textContent.trim();
        if (conversions[txt]) el.textContent = conversions[txt];
    });

    // Update goal target label
    const goalTarget = document.querySelector('.goal-target');
    if (goalTarget) goalTarget.textContent = 'Goal: $240,000';

    // Update hero badge
    const heroBadge = document.querySelector('.hero-badge');
    if (heroBadge) {
        heroBadge.innerHTML = heroBadge.innerHTML.replace('₹2 Crore', '$240,000');
    }

    // Update tier titles and descriptions for high-ticket USD
    const tierContent = {
        '$500': { title: 'Teacher Sponsor', desc: 'Covers tuition and training for one B.Ed student for a full year.' },
        '$1,200': { title: 'Degree Sponsor', desc: 'Sponsors a student\'s complete 2-year B.Ed journey until certified.' },
        '$5,000': { title: 'Founding Member 🌟', desc: 'Funds the construction of one classroom. Plaque on the door.' },
        '$10,000+': { title: 'Institute Pillar', desc: 'Funds a modern science/computer lab. Major recognition on the donor wall.' },
    };

    document.querySelectorAll('.tier-card').forEach(card => {
        const amountEl = card.querySelector('.tier-amount');
        if (!amountEl) return;
        const amount = amountEl.textContent.trim();
        if (tierContent[amount]) {
            const h3 = card.querySelector('h3');
            const p = card.querySelector('p');
            if (h3) h3.textContent = tierContent[amount].title;
            if (p) p.textContent = tierContent[amount].desc;
        }
    });

    // Update tier button text
    document.querySelectorAll('.tier-btn').forEach(el => {
        const text = el.textContent.trim();
        for (const [inr, usd] of Object.entries(conversions)) {
            if (text.includes(inr.replace('₹', ''))) {
                el.textContent = 'Donate ' + conversions[inr];
            }
        }
    });

    // Add currency indicator
    const currencyNote = document.createElement('p');
    currencyNote.className = 'currency-note';
    currencyNote.innerHTML = '🌎 Showing amounts in <strong>USD</strong> for international donors. <a href="http://impactguru.com/s/eW5Mk1" target="_blank">ImpactGuru accepts international payments</a>.';
    const heroContent = document.querySelector('.hero-content');
    if (heroContent) heroContent.appendChild(currencyNote);

    // Update hero stat suffix
    const statSuffixes = document.querySelectorAll('.hero-stat-suffix');
    if (statSuffixes[0]) statSuffixes[0].textContent = '40K';
    const statNumbers = document.querySelectorAll('.hero-stat-number');
    if (statNumbers[0]) {
        statNumbers[0].setAttribute('data-target', '240');
        statNumbers[0].textContent = '$';
    }

    // Update CTA subtitle
    const ctaSub = document.querySelector('.cta-subtitle');
    if (ctaSub) {
        ctaSub.innerHTML = ctaSub.innerHTML
            .replace('₹2 Crore', '$240,000')
            .replace('Every rupee', 'Every dollar');
    }

    // Add ImpactGuru USD selector link to donation buttons  
    document.querySelectorAll('a[href*="impactguru.com/s/eW5Mk1"]').forEach(a => {
        // ImpactGuru supports USD — the platform auto-handles currency
    });
}

// ===== PARTICLES =====
function initParticles() {
    const container = document.getElementById('hero-particles');
    if (!container) return;

    for (let i = 0; i < 30; i++) {
        const particle = document.createElement('div');
        particle.className = 'hero-particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';
        particle.style.width = (Math.random() * 4 + 2) + 'px';
        particle.style.height = particle.style.width;
        particle.style.animationDelay = (Math.random() * 6) + 's';
        particle.style.animationDuration = (Math.random() * 4 + 4) + 's';
        particle.style.opacity = Math.random() * 0.5 + 0.1;
        container.appendChild(particle);
    }
}

// ===== COUNTER ANIMATION =====
function initCounters() {
    const counters = document.querySelectorAll('.hero-stat-number');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    counters.forEach(counter => observer.observe(counter));
}

function animateCounter(el) {
    const target = parseInt(el.getAttribute('data-target'));
    const duration = 2000;
    const start = performance.now();

    function update(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = Math.floor(eased * target);
        el.textContent = current;

        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            el.textContent = target;
        }
    }

    requestAnimationFrame(update);
}

// ===== SCROLL ANIMATIONS (AOS) =====
function initAOS() {
    const elements = document.querySelectorAll('[data-aos]');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const siblings = Array.from(entry.target.parentElement.children).filter(c => c.hasAttribute('data-aos'));
                const index = siblings.indexOf(entry.target);
                entry.target.style.transitionDelay = (index * 0.1) + 's';
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.15 });

    elements.forEach(el => observer.observe(el));
}

// ===== FLOATING DONATE BUTTON =====
function initFloatingButton() {
    const btn = document.getElementById('floating-donate');
    const hero = document.getElementById('hero');

    window.addEventListener('scroll', () => {
        if (window.scrollY > hero.offsetHeight * 0.7) {
            btn.classList.add('visible');
        } else {
            btn.classList.remove('visible');
        }
    });
}

// ===== TRACK SHARE CLICKS =====
document.querySelectorAll('.share-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const platform = btn.classList[1];
        console.log(`Share clicked: ${platform}`);
    });
});
