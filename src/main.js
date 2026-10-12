(function () {
  var rustig = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Header iets donkerder zodra je scrolt
  var kop = document.querySelector('.kop');
  if (kop) {
    var zet = function () { kop.classList.toggle('gescrold', window.scrollY > 8); };
    zet(); window.addEventListener('scroll', zet, { passive: true });
  }

  // Zachte onthulling bij scrollen. Alleen voor wat bij het laden nog onder de vouw staat,
  // zodat de pagina zonder JavaScript of animatie altijd compleet zichtbaar is.
  if (!rustig && 'IntersectionObserver' in window) {
    var doelen = document.querySelectorAll('.sectie-kop, .tegel, .over-tekst, .over img, .case-beeld, .case-tekst, .diensten li, .faq, .recensie, .logos div, .contact-links, form, .doc h2, .app-kaart');
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

  // Werkmethode-tijdlijn: afspeelkop start als de tijdlijn in beeld komt
  var tl = document.querySelector('.tijdlijn');
  if (tl && !rustig && 'IntersectionObserver' in window) {
    document.documentElement.classList.add('js-tijdlijn');
    var tio = new IntersectionObserver(function (items) {
      if (items[0].isIntersecting) { tl.classList.add('speelt'); tio.disconnect(); }
    }, { threshold: 0.35 });
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
  document.querySelectorAll('[data-yt]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var id = btn.getAttribute('data-yt');
      var box = btn.parentElement;
      var f = document.createElement('iframe');
      f.src = 'https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0';
      f.title = btn.getAttribute('aria-label') || 'Video';
      f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
      f.allowFullscreen = true;
      box.innerHTML = '';
      box.appendChild(f);
    });
  });

  // Mailadres kopiëren
  document.querySelectorAll('[data-kopieer]').forEach(function (b) {
    b.addEventListener('click', function () {
      var t = b.getAttribute('data-kopieer');
      var klaar = function () { b.textContent = 'Gekopieerd'; setTimeout(function () { b.textContent = 'Kopieer'; }, 2000); };
      if (navigator.clipboard) {
        navigator.clipboard.writeText(t).then(klaar, function () { selecteer(t); });
      } else { selecteer(t); }
    });
  });
  function selecteer(t) {
    var el = document.querySelector('[data-mail-tekst]');
    if (!el) return;
    var r = document.createRange(); r.selectNodeContents(el);
    var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
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
        melding('Bedankt! Je bericht is binnen. Ik neem zo snel mogelijk contact met je op.', 'goed');
      } else { throw new Error(res.message); }
    }).catch(function () {
      melding('Versturen lukte niet. Mail je vraag dan direct naar info@8mmfilmproductions.nl, dan kom ik er zo snel mogelijk op terug.', 'fout');
    }).finally(function () {
      knop.disabled = false; knop.textContent = oud;
    });
  });
})();
