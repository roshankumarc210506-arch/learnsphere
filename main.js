// main.js - simple handlers for index.html
document.addEventListener('DOMContentLoaded', () => {
  const toLoginButtons = document.querySelectorAll('#to-login');
  const aboutStartLearningButton = document.getElementById('about-start-learning');
  const aboutContactButton = document.getElementById('about-contact');
  const toggleButtons = document.querySelectorAll('#toggle-theme');
  const backToTopButton = document.getElementById('back-to-top');

  const viewFeaturesButton = document.getElementById('view-features');
  const featuresSection = document.getElementById('features-detailed'); // Renamed from aboutSection

  // --- PERSISTENT THEME LOGIC ---
  function updateTheme(isDark) {
    document.body.classList.toggle('dark', isDark);
    localStorage.setItem('learnsphere_theme', isDark ? 'dark' : 'light');
    toggleButtons.forEach(btn => {
      btn.innerText = isDark ? 'Light' : 'Dark';
    });
  }
  const savedTheme = localStorage.getItem('learnsphere_theme');
  const initialIsDark = savedTheme === 'dark';
  updateTheme(initialIsDark);
  toggleButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const newIsDark = !document.body.classList.contains('dark');
      updateTheme(newIsDark);
    });
  });
  // ------------------------------

  // --- NAVIGATION & ACTIONS ---
  toLoginButtons.forEach(btn => {
    btn.addEventListener('click', () => location.href = 'login.html');
  });

  if (viewFeaturesButton && featuresSection) {
    viewFeaturesButton.addEventListener('click', () => {
      featuresSection.classList.remove('hidden');
      featuresSection.scrollIntoView({ behavior: 'smooth' });
    });
  }

  if (aboutStartLearningButton) {
    aboutStartLearningButton.addEventListener('click', () => location.href = 'login.html');
  }

  if (aboutContactButton) {
    aboutContactButton.addEventListener('click', () => alert('Contact feature coming soon!'));
  }

  // --- BACK TO TOP BUTTON LOGIC ---
  window.addEventListener('scroll', () => {
    if (window.scrollY > 300) {
      backToTopButton.classList.remove('hidden');
    } else {
      backToTopButton.classList.add('hidden');
    }
  });

  backToTopButton.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });

  // --- ANIMATE ON SCROLL LOGIC ---
  const animatedElements = document.querySelectorAll('.animate-on-scroll');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.1
  });

  animatedElements.forEach(el => {
    observer.observe(el);
  });
});