// JESFOD Enhanced Animations - Green Theme
// Hero Slideshow Control
function initHeroSlideshow() {
  const slideshow = document.querySelector('.hero-slideshow');
  if (!slideshow) return;

  const slides = slideshow.querySelectorAll('.hero-slide');
  let currentSlide = 0;
  let interval;

  function showSlide(index) {
    slides.forEach((slide, i) => {
      slide.classList.toggle('active', i === index);
    });
  }

  function nextSlide() {
    currentSlide = (currentSlide + 1) % slides.length;
    showSlide(currentSlide);
  }

  function startSlideshow() {
    interval = setInterval(nextSlide, 5000); // 5s per slide
  }

  function pauseSlideshow() {
    clearInterval(interval);
  }

  // Auto start
  startSlideshow();

  // Pause on hover
  slideshow.addEventListener('mouseenter', pauseSlideshow);
  slideshow.addEventListener('mouseleave', startSlideshow);

  // Optional: Navigation dots (add if needed)
  /*
  const dotsContainer = document.createElement('div');
  dotsContainer.className = 'hero-dots position-absolute bottom-0 start-50 translate-middle-x mb-3 d-flex gap-2';
  slideshow.appendChild(dotsContainer);
  slides.forEach((_, i) => {
    const dot = document.createElement('button');
    dot.className = 'btn btn-sm rounded-circle bg-white bg-opacity-50 hover-bg-opacity-75';
    dot.style.width = '12px'; dot.style.height = '12px';
    dot.addEventListener('click', () => {
      clearInterval(interval);
      showSlide(i);
      currentSlide = i;
      startSlideshow();
    });
    dotsContainer.appendChild(dot);
  });
  */
}

document.addEventListener('DOMContentLoaded', function() {
  initHeroSlideshow();
  
  // Smooth scrolling
  document.querySelectorAll('a[href^=\"#\"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });

  // Navbar scroll effect
  window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
      navbar.style.background = 'rgba(40,167,69,0.95)';
      navbar.style.backdropFilter = 'blur(10px)';
    } else {
      navbar.style.background = 'linear-gradient(135deg, #28a745, #20c997)';
    }
  });

  // Animate stats counters
  function animateCounters() {
    const counters = document.querySelectorAll('.stat-number');
    counters.forEach(counter => {
      const target = parseInt(counter.getAttribute('data-target'));
      const increment = target / 100;
      let current = 0;
      const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
          counter.textContent = target;
          clearInterval(timer);
        } else {
          counter.textContent = Math.floor(current);
        }
      }, 20);
    });
  }

  // Intersection Observer for animations
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate__animated', 'animate__fadeInUp');
        if (entry.target.querySelector('.stat-number')) {
          animateCounters();
        }
      }
    });
  }, observerOptions);

  // Observe sections
  document.querySelectorAll('section').forEach(section => {
    observer.observe(section);
  });

// Enhanced image lightbox + download
  document.querySelectorAll('.card-img-top, .profile-photo, img.news-image').forEach(img => {
    img.style.cursor = 'pointer';
    img.addEventListener('click', function(e) {
      e.preventDefault();
      const src = this.src;
      const modal = document.createElement('div');
      modal.id = 'lightbox';
      modal.style.cssText = `
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; 
        background: rgba(0,0,0,0.95); z-index: 9999; display: flex; align-items: center; justify-content: center;
        backdrop-filter: blur(5px);
      `;
      modal.innerHTML = `
        <div style="position: relative; max-width: 90%; max-height: 90%;">
          <img src="${src}" style="max-width: 100%; max-height: 90vh; border-radius: 10px; box-shadow: 0 20px 60px rgba(0,0,0,0.5);">
          <button onclick="downloadImage('${src}')" style="position: absolute; bottom: 20px; right: 20px; background: #007bff; color: white; border: none; border-radius: 50%; width: 50px; height: 50px; cursor: pointer; font-size: 1.2rem;"><i class="bi bi-download"></i></button>
          <button onclick="closeLightbox()" style="position: absolute; top: 20px; right: 20px; background: transparent; color: white; border: none; font-size: 2rem; cursor: pointer;">×</button>
        </div>
      `;
      document.body.appendChild(modal);
      document.body.style.overflow = 'hidden';
    });
  });

  window.downloadImage = function(src) {
    const a = document.createElement('a');
    a.href = src;
    a.download = src.split('/').pop();
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  window.closeLightbox = function() {
    const lightbox = document.getElementById('lightbox');
    if (lightbox) {
      lightbox.remove();
      document.body.style.overflow = 'auto';
    }
  };

  // Form submit simulation
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      const btn = this.querySelector('button[type=\"submit\"]');
      const original = btn.textContent;
      btn.textContent = 'Envoyé !';
      btn.disabled = true;
      setTimeout(() => {
        btn.textContent = original;
        btn.disabled = false;
        this.reset();
        alert('Message envoyé avec succès ! (Simulation)');
      }, 2000);
    });
  });
});
