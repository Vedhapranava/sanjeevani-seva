
// mobile nav
const toggle = document.querySelector('.nav-toggle');
const nav = document.querySelector('.nav');
if (toggle && nav) { toggle.addEventListener('click', () => nav.classList.toggle('open')); }

// reveal on scroll
const revealEls = document.querySelectorAll('[data-reveal]');
const onReveal = (entries, obs) => { for (const e of entries) if (e.isIntersecting){ e.target.classList.add('reveal-visible'); obs.unobserve(e.target);} };
const ro = new IntersectionObserver(onReveal, { rootMargin: '0px 0px -10% 0px'});
revealEls.forEach(el => ro.observe(el));

// contact form -> /api/leads
const form = document.getElementById('contactForm');
if (form) {
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(form).entries());
    try{
      const r = await fetch('/api/leads', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(data) });
      if (!r.ok) throw new Error('Network');
      alert(`Thanks ${data.name || ''}! We will call you at ${data.phone || ''} for ${data.need || 'your request'}.`);
      form.reset();
    }catch(err){
      alert('Could not send. Please call the helpline.');
    }
  });
}

// Fetch content for services (home + services page)
async function renderServices(selector){
  const el = document.querySelector(selector);
  if (!el) return;
  const res = await fetch('/api/services');
  const rows = await res.json();
  if (!Array.isArray(rows)) return;
  el.innerHTML = rows.map(r => `
    <a class="card lift">
      <div class="icon">🩺</div>
      <h3>${r.title}</h3>
      <p>${r.category}</p>
      ${(JSON.parse(r.bullets||'[]')||[]).length ? `<ul class="bullets">${(JSON.parse(r.bullets||'[]')).map(b=>`<li>${b}</li>`).join('')}</ul>`:''}
    </a>
  `).join('');
}

renderServices('#servicesGrid');
renderServices('#servicesGridPage');

// Fetch network
(async function(){
  const grid = document.getElementById('networkGrid');
  if (grid){
    const res = await fetch('/api/network'); const rows = await res.json();
    grid.innerHTML = rows.map(r=>`<div class="network-card"><h4>${r.name}</h4><p>${r.city} · ${r.meta||''}</p></div>`).join('');
  }
  const chips = document.getElementById('citiesChips');
  if (chips){
    const res = await fetch('/api/network'); const rows = await res.json();
    const uniq = [...new Set(rows.map(r=>r.city))];
    chips.innerHTML = uniq.map(c=>`<span class="chip">${c}</span>`).join('');
  }
})();

// Testimonials slider
(async function(){
  const wrap = document.getElementById('testimonialsWrap');
  if (!wrap) return;
  const res = await fetch('/api/testimonials');
  const rows = await res.json();
  const slides = rows.map((r,i)=>`
    <div class="slide ${i===0?'active':''}">
      <blockquote>${r.quote}</blockquote>
      <div class="author">${r.author}</div>
    </div>
  `).join('');
  wrap.insertAdjacentHTML('afterbegin', slides);
  const dotsEl = wrap.querySelector('.dots');
  const slideEls = Array.from(wrap.querySelectorAll('.slide'));
  slideEls.forEach((_, i) => {
    const btn = document.createElement('button');
    btn.addEventListener('click', () => show(i));
    dotsEl.appendChild(btn);
  });
  function show(i){
    slideEls.forEach((s, idx)=> s.classList.toggle('active', idx===i));
    dotsEl.querySelectorAll('button').forEach((b, idx)=> b.classList.toggle('active', idx===i));
  }
  show(0);
})();
