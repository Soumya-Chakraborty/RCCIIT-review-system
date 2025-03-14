// Common JavaScript for the application

// Flash message auto-close
document.addEventListener("DOMContentLoaded", function () {
  // Auto-dismiss alerts after 5 seconds
  setTimeout(function () {
    const alerts = document.querySelectorAll(".alert:not(.alert-permanent)");
    alerts.forEach(function (alert) {
      const closeBtn = alert.querySelector(".close");
      if (closeBtn) {
        closeBtn.click();
      }
    });
  }, 5000);

  // Set active navigation based on URL
  const currentPath = window.location.pathname;
  const navLinks = document.querySelectorAll(".navbar-nav .nav-link");

  navLinks.forEach(function (link) {
    if (link.getAttribute("href") === currentPath) {
      link.classList.add("active");
    }
  });
});

// Star rating system for reviews
function initializeStarRatings() {
  const ratingContainers = document.querySelectorAll(".star-rating");

  ratingContainers.forEach(function (container) {
    const stars = container.querySelectorAll("i");
    const input = container.previousElementSibling;

    // Set initial state
    if (input && input.value) {
      updateStars(parseInt(input.value), stars);
    }

    // Add click handlers
    stars.forEach(function (star, index) {
      star.addEventListener("click", function () {
        const value = index + 1;
        input.value = value;
        updateStars(value, stars);
      });

      // Add hover effect
      star.addEventListener("mouseenter", function () {
        const value = index + 1;
        previewStars(value, stars);
      });

      container.addEventListener("mouseleave", function () {
        const value = input.value || 0;
        updateStars(parseInt(value), stars);
      });
    });
  });
}

// Update star display based on rating value
function updateStars(value, stars) {
  stars.forEach(function (star, index) {
    if (index < value) {
      star.classList.remove("far");
      star.classList.add("fas");
    } else {
      star.classList.remove("fas");
      star.classList.add("far");
    }
  });
}

// Preview stars on hover
function previewStars(value, stars) {
  stars.forEach(function (star, index) {
    if (index < value) {
      star.classList.remove("far");
      star.classList.add("fas");
    } else {
      star.classList.remove("fas");
      star.classList.add("far");
    }
  });
}

// Call this when page loads
document.addEventListener("DOMContentLoaded", function () {
  initializeStarRatings();
});

// Theme Management
const themeToggle = document.createElement('div');
themeToggle.className = 'theme-toggle';
themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
document.body.appendChild(themeToggle);

// Check for saved theme preference
const savedTheme = localStorage.getItem('theme') || 'light';
document.documentElement.setAttribute('data-theme', savedTheme);
updateThemeIcon(savedTheme);

// Theme toggle functionality
themeToggle.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
});

function updateThemeIcon(theme) {
    themeToggle.innerHTML = theme === 'light' 
        ? '<i class="fas fa-moon"></i>' 
        : '<i class="fas fa-sun"></i>';
}

// Loading Screen
const loadingScreen = document.createElement('div');
loadingScreen.className = 'loading-screen';
loadingScreen.innerHTML = '<div class="loading-spinner"></div>';
document.body.appendChild(loadingScreen);

window.addEventListener('load', () => {
    // Hide loading screen with fade effect
    loadingScreen.style.opacity = '0';
    setTimeout(() => {
        loadingScreen.style.display = 'none';
    }, 500);
    
    // Animate elements
    animateElements();
});

// Animation Functions
function animateElements() {
    // Animate cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.animation = 'fadeIn 0.5s ease-out forwards';
        }, index * 100);
    });

    // Animate navbar
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        navbar.style.animation = 'slideIn 0.5s ease-out';
    }

    // Animate form elements
    const formElements = document.querySelectorAll('.form-control, .btn');
    formElements.forEach((element, index) => {
        element.style.opacity = '0';
        setTimeout(() => {
            element.style.opacity = '1';
            element.style.animation = 'fadeIn 0.3s ease-out forwards';
        }, index * 50);
    });
}

// Star Rating Animation
document.addEventListener('DOMContentLoaded', () => {
    const stars = document.querySelectorAll('.star-rating i');
    stars.forEach(star => {
        star.addEventListener('mouseover', () => {
            const value = star.getAttribute('data-value');
            const starContainer = star.closest('.star-rating');
            const allStars = starContainer.querySelectorAll('i');
            
            allStars.forEach(s => {
                if (parseInt(s.getAttribute('data-value')) <= parseInt(value)) {
                    s.classList.add('fas');
                    s.classList.remove('far');
                } else {
                    s.classList.add('far');
                    s.classList.remove('fas');
                }
            });
        });
    });
});

// Flash Messages Animation
function showFlashMessage(message, type = 'info') {
    const flash = document.createElement('div');
    flash.className = `alert alert-${type} fade show`;
    flash.setAttribute('role', 'alert');
    flash.innerHTML = message;
    
    const container = document.querySelector('.container');
    container.insertBefore(flash, container.firstChild);
    
    setTimeout(() => {
        flash.style.animation = 'fadeIn 0.5s reverse';
        setTimeout(() => flash.remove(), 500);
    }, 3000);
}

// Form Submission Loading State
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', () => {
        const submitBtn = form.querySelector('[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
        }
    });
});

// Smooth Scrolling
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});
