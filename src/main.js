(function () {
  var rustig = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Achtergrond: de lichtvlekken schuiven langzamer mee dan de pagina (begint op ca. 18% van de scrollsnelheid
  // en loopt zacht af naar maximaal 40vh). Uit bij verminderde beweging en op smalle schermen.
  var vlekken = document.querySelectorAll('.vlek');
  if (vlekken.length && !rustig && window.matchMedia && window.matchMedia('(min-width: 640px)').matches) {
    var wacht = false;
    var beweeg = function () {
      wacht = false;
      var max = window.innerHeight * 0.4, x = window.scrollY * 0.18, af = max * x / (max + x);
      vlekken[0].style.transform = 'translate3d(0,' + (-af).toFixed(1) + 'px,0)';
      if (vlekken[1]) vlekken[1].style.transform = 'translate3d(0,' + (-af * 0.7).toFixed(1) + 'px,0)';
      if (vlekken[2]) { // de derde vlek komt pas onderaan de pagina in beeld
        var rest = Math.max(1, document.documentElement.scrollHeight - window.innerHeight), vz = Math.min(1, window.scrollY / rest);
        vlekken[2].style.transform = 'translate3d(0,' + (-(af * 0.7 + vz * vz * window.innerHeight * 0.5)).toFixed(1) + 'px,0)';
      }
    };
    window.addEventListener('scroll', function () { if (!wacht) { wacht = true; requestAnimationFrame(beweeg); } }, { passive: true });
    beweeg();
  }

  // Header iets donkerder zodra je scrolt
  var kop = document.querySelector('.kop');
  if (kop) {
    var zet = function () { kop.classList.toggle('gescrold', window.scrollY > 8); };
    zet(); window.addEventListener('scroll', zet, { passive: true });
  }

  // Zachte onthulling bij scrollen. Alleen voor wat bij het laden nog onder de vouw staat,
  // zodat de pagina zonder JavaScript of animatie altijd compleet zichtbaar is.
  if (!rustig && 'IntersectionObserver' in window) {
    var doelen = document.querySelectorAll('.sectie-kop, .tegel, .over-kop, .case-tabs, .diensten li, .faq, .recensie, .logos div, .contact-links, form, .doc h2, .app-kaart');
    var io = new IntersectionObserver(function (items) {
      items.forEach(function (it) {
        if (!it.isIntersecting) return;
        it.target.classList.add('verschijn');
        it.target.classList.remove('wacht');
        io.unobserve(it.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    var hoogte = window.innerHeight;
    doelen.forEach(function (el) {
      if (el.getBoundingClientRect().top < hoogte * 0.92) return;
      // kleine trapsgewijze vertraging binnen een rij (videogrid, stappen, logo's)
      var broers = el.parentElement ? Array.prototype.indexOf.call(el.parentElement.children, el) : 0;
      if (el.matches('.tegel, .stappen li, .logos div, .recensie')) el.style.setProperty('--vertraging', (broers % 4) * 0.08 + 's');
      el.classList.add('wacht');
      io.observe(el);
    });
  }

  // Werkmethode-tijdlijn: de afspeelkop loopt eenmalig over liniaal en clips zodra de tijdlijn in beeld komt
  var tl = document.querySelector('.tijdlijn');
  if (tl && !rustig && 'IntersectionObserver' in window) {
    document.documentElement.classList.add('js-tijdlijn');
    var tio = new IntersectionObserver(function (items) {
      if (items[0].isIntersecting) { tl.classList.add('speelt'); tio.disconnect(); }
    }, { threshold: 0.3 });
    tio.observe(tl);
  }

  // Filter op soort video (videopagina). Werkt ook via een link als videos#bedrijfsfilm.
  var knoppen = document.querySelectorAll('.filter');
  var grid = document.querySelector('.grid.ruim');
  if (knoppen.length && grid) {
    var tegels = grid.querySelectorAll('.tegel');
    var filter = function (cat, scroll) {
      var geldig = false;
      knoppen.forEach(function (k) { var aan = k.getAttribute('data-filter') === cat; k.setAttribute('aria-pressed', aan ? 'true' : 'false'); if (aan) geldig = true; });
      if (!geldig) { cat = ''; knoppen[0].setAttribute('aria-pressed', 'true'); }
      tegels.forEach(function (t) { t.hidden = !!cat && t.getAttribute('data-cat') !== cat; t.classList.remove('wacht'); });
      grid.classList.toggle('gefilterd', !!cat);
      if (scroll) document.querySelector('.filters').scrollIntoView({ behavior: rustig ? 'auto' : 'smooth', block: 'start' });
    };
    knoppen.forEach(function (k) {
      k.addEventListener('click', function () {
        var cat = k.getAttribute('data-filter');
        filter(cat, false);
        try { history.replaceState(null, '', cat ? '#' + cat : location.pathname); } catch (e) {}
      });
    });
    var start = (location.hash || '').slice(1);
    if (start && !document.getElementById(start)) filter(start, true);
    window.addEventListener('hashchange', function () {
      var h = location.hash.slice(1);
      if (!document.getElementById(h)) filter(h, true);
    });
  }

  // Video's: pas laden na klik (sneller en privacyvriendelijk, geen YouTube-cookies vooraf)
  // Zodra iemand een video aanwijst of aanraakt, bouwen we alvast de verbinding met YouTube op (sneller starten).
  var verbonden = false;
  function opwarmen() {
    if (verbonden) return;
    verbonden = true;
    var l = document.createElement('link');
    l.rel = 'preconnect'; l.href = 'https://www.youtube-nocookie.com';
    document.head.appendChild(l);
  }
  function koppelVideo(btn) {
    ['pointerenter', 'touchstart', 'focus'].forEach(function (ev) { btn.addEventListener(ev, opwarmen, { once: true, passive: true }); });
    btn.addEventListener('click', function () {
      var id = btn.getAttribute('data-yt');
      var box = btn.parentElement;
      opwarmen();
      btn.disabled = true;
      box.classList.add('laadt'); // de still blijft staan met een draaiend bolletje tot de speler er is
      var f = document.createElement('iframe');
      f.src = 'https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0&playsinline=1';
      f.title = btn.getAttribute('aria-label') || 'Video';
      f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
      f.allowFullscreen = true;
      f.addEventListener('load', function () {
        f.classList.add('klaar');
        box.classList.remove('laadt');
        Array.prototype.forEach.call(box.querySelectorAll('button, .tijdcode'), function (x) { x.remove(); });
      });
      box.appendChild(f);
    });
  }
  document.querySelectorAll('[data-yt]').forEach(koppelVideo);

  // YouTube heeft niet van elke video een maxresdefault-still: val dan terug op hqdefault
  function stillFallback(img) {
    var terug = img.getAttribute('data-fallback');
    if (!terug) return;
    var wissel = function () { img.removeAttribute('data-fallback'); img.src = terug; };
    img.addEventListener('error', wissel);
    img.addEventListener('load', function () { if (img.naturalWidth && img.naturalWidth <= 120) wissel(); });
    if (img.complete && (!img.naturalWidth || img.naturalWidth <= 120)) wissel();
  }
  document.querySelectorAll('img[data-fallback]').forEach(stillFallback);

  // Uitgelichte projecten: tabs. Zonder JavaScript staan alle projecten gewoon onder elkaar.
  var cases = document.querySelector('.cases');
  if (cases) {
    var tabs = Array.prototype.slice.call(cases.querySelectorAll('[role=tab]'));
    var lijst = cases.querySelector('[role=tablist]');
    var panelen = tabs.map(function (t) { return document.getElementById(t.getAttribute('aria-controls')); });
    if (tabs.length && lijst) {
      cases.classList.add('js-cases');
      lijst.hidden = false;
      panelen.forEach(function (p) {
        p.setAttribute('role', 'tabpanel');
        var b = p.querySelector('.beeld');
        p._beeld = b ? b.innerHTML : '';
      });
      // een video die nog speelt als je van tab wisselt, zetten we terug naar de still
      var stopVideo = function (p) {
        var b = p.querySelector('.beeld');
        if (!b || !b.querySelector('iframe')) return;
        b.innerHTML = p._beeld;
        var k = b.querySelector('[data-yt]'); if (k) koppelVideo(k);
        var im = b.querySelector('img[data-fallback]'); if (im) stillFallback(im);
      };
      var kies = function (i, focus) {
        tabs.forEach(function (t, j) { t.setAttribute('aria-selected', j === i ? 'true' : 'false'); t.tabIndex = j === i ? 0 : -1; });
        panelen.forEach(function (p, j) {
          if (j === i) {
            if (!p.hidden) return;
            p.hidden = false; p.classList.remove('wissel');
            if (!rustig) { void p.offsetWidth; p.classList.add('wissel'); }
          } else if (!p.hidden) { stopVideo(p); p.hidden = true; }
        });
        if (focus) { tabs[i].focus(); tabs[i].scrollIntoView({ block: 'nearest', inline: 'nearest', behavior: rustig ? 'auto' : 'smooth' }); }
      };
      tabs.forEach(function (t, i) {
        t.addEventListener('click', function () { kies(i, false); });
        t.addEventListener('keydown', function (ev) {
          var n = tabs.length, nieuw = null;
          if (ev.key === 'ArrowRight') nieuw = (i + 1) % n;
          else if (ev.key === 'ArrowLeft') nieuw = (i - 1 + n) % n;
          else if (ev.key === 'Home') nieuw = 0;
          else if (ev.key === 'End') nieuw = n - 1;
          if (nieuw === null) return;
          ev.preventDefault(); kies(nieuw, true);
        });
      });
      kies(0, false);
    }
  }

  // Contactformulier via Web3Forms. Zonder JavaScript post het formulier gewoon naar Web3Forms.
  var form = document.getElementById('contactformulier');
  if (!form) return;
  var status = document.getElementById('formstatus');
  var knop = form.querySelector('button[type=submit]');
  var preview = form.hasAttribute('data-preview');

  function melding(tekst, soort) {
    status.hidden = false;
    status.className = 'status ' + soort;
    status.textContent = tekst;
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (form.botcheck && form.botcheck.checked) return; // honeypot: bots vinken dit aan
    if (!form.checkValidity()) { form.reportValidity(); return; }
    if (preview) {
      melding('Dit is het voorbeeld: hier wordt nog niets verstuurd. Op de echte site gaat je bericht naar info@8mmfilmproductions.nl.', 'goed');
      return;
    }
    knop.disabled = true;
    var oud = knop.textContent;
    knop.textContent = 'Versturen...';
    var data = {};
    new FormData(form).forEach(function (v, k) { data[k] = v; });
    data.subject = 'Nieuwe aanvraag via de website: ' + (data.naam || '');
    data.from_name = '8MM website';
    fetch(form.action, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(data)
    }).then(function (r) { return r.json(); }).then(function (res) {
      if (res.success) {
        form.reset();
        melding('Bedankt! Je bericht is binnen. Je hoort binnen twee werkdagen van ons.', 'goed');
      } else { throw new Error(res.message); }
    }).catch(function () {
      melding('Versturen lukte niet. Mail je vraag dan direct naar info@8mmfilmproductions.nl, dan komen we er zo snel mogelijk op terug.', 'fout');
    }).finally(function () {
      knop.disabled = false; knop.textContent = oud;
    });
  });
})();
