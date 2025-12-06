const scrollLinks = document.querySelectorAll('[data-scroll], header nav a');
const topbar = document.getElementById('topbar');
const filters = document.querySelectorAll('.filter');
const amenities = document.querySelectorAll('.amenity');
const milestones = document.querySelectorAll('.milestone');
const form = document.querySelector('.contact__form');
const status = document.querySelector('.form__status');
const canvas = document.getElementById('wave-canvas');
const ctx = canvas.getContext('2d');

function resizeCanvas() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
}

function drawWaves(time) {
  if (!canvas) return;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const amplitude = 18;
  const baseY = canvas.height * 0.6;
  const speed = 0.0025;
  const colors = ['rgba(61,213,255,0.14)', 'rgba(123,157,255,0.14)', 'rgba(61,213,255,0.08)'];

  colors.forEach((color, i) => {
    ctx.beginPath();
    ctx.moveTo(0, baseY);
    for (let x = 0; x <= canvas.width; x += 12) {
      const y = baseY + Math.sin((x + time * (i + 1) * 40) * speed) * amplitude * (1 + i * 0.3);
      ctx.lineTo(x, y);
    }
    ctx.lineTo(canvas.width, canvas.height);
    ctx.lineTo(0, canvas.height);
    ctx.closePath();
    ctx.fillStyle = color;
    ctx.fill();
  });

  requestAnimationFrame(drawWaves);
}

function smoothScroll(target) {
  const el = document.querySelector(target);
  if (el) {
    el.scrollIntoView({ behavior: 'smooth' });
  }
}

scrollLinks.forEach(link => {
  link.addEventListener('click', event => {
    const target = link.dataset.scroll || link.getAttribute('href');
    if (target.startsWith('#')) {
      event.preventDefault();
      smoothScroll(target);
    }
  });
});

window.addEventListener('scroll', () => {
  const scrolled = window.scrollY > 40;
  topbar.style.boxShadow = scrolled ? '0 10px 30px rgba(0,0,0,0.35)' : 'none';
  topbar.style.background = scrolled ? 'rgba(4, 9, 21, 0.9)' : 'rgba(4, 9, 21, 0.75)';
});

filters.forEach(filter => {
  filter.addEventListener('click', () => {
    filters.forEach(f => f.classList.remove('active'));
    filter.classList.add('active');
    const category = filter.dataset.filter;
    amenities.forEach(item => {
      const matches = category === 'all' || item.dataset.category === category;
      item.style.display = matches ? 'block' : 'none';
      item.style.opacity = matches ? '1' : '0';
    });
  });
});

const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('active');
    }
  });
}, { threshold: 0.3 });

milestones.forEach(item => observer.observe(item));

if (form) {
  form.addEventListener('submit', event => {
    event.preventDefault();
    const valid = form.checkValidity();
    if (!valid) {
      status.textContent = 'Заполните обязательные поля';
      status.style.color = '#ffb3c7';
      return;
    }
    status.textContent = 'Спасибо! Мы свяжемся с вами в течение 15 минут';
    status.style.color = '#3dd5ff';
    form.reset();
  });
}

resizeCanvas();
requestAnimationFrame(drawWaves);
window.addEventListener('resize', resizeCanvas);
