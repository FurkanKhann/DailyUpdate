// static/js/main.js

// Form validation and enhancement
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateX(-20px)';
            setTimeout(() => {
                alert.style.display = 'none';
            }, 300);
        }, 5000);
    });

    // Email form validation
    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(input => {
        input.addEventListener('blur', function() {
            const email = this.value;
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            
            if (email && !emailRegex.test(email)) {
                this.style.borderColor = '#dc3545';
                this.style.backgroundColor = '#f8d7da';
            } else if (email) {
                this.style.borderColor = '#28a745';
                this.style.backgroundColor = '#d4edda';
            } else {
                this.style.borderColor = '#ced4da';
                this.style.backgroundColor = 'white';
            }
        });
    });

    // Form submission enhancement
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.textContent = 'Processing...';
                submitBtn.disabled = true;
                
                // Re-enable after 3 seconds (fallback)
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.textContent = submitBtn.getAttribute('data-original-text') || 'Submit';
                }, 3000);
            }
        });
    });

    // Store original button text
    const submitBtns = document.querySelectorAll('button[type="submit"]');
    submitBtns.forEach(btn => {
        btn.setAttribute('data-original-text', btn.textContent);
    });
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Add loading animation to feature cards
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe all feature cards
document.querySelectorAll('.feature-card').forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(card);
});
