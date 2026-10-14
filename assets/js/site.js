/* Moulin de la Gardette — en-tête, menu, âge légal, apparitions, vitrine des cuvées, sommaire des vins,
   chiffres, formulaires (mode maquette) et commande. */
(() => {
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const calme = matchMedia('(prefers-reduced-motion: reduce)').matches;
  /* Langue de la page : tout texte affiché ou annoncé par ce script existe en français et en anglais */
  const EN = document.documentElement.lang === 'en';
  const T = EN ? {
    menuOuvrir: 'Open menu', menuFermer: 'Close menu',
    bouteilles: (n) => `${n.toLocaleString('en-GB')} bottle${n === 1 ? '' : 's'}`,
    cartons: (c, reste) => ` · ${c} case${c > 1 ? 's' : ''}${reste ? ` plus ${reste}` : ''}`,
    auMoinsUne: 'Please choose at least one bottle.',
    aCompleter: 'Please fill in the highlighted fields.',
    merci: 'Thank you', commandeOk: 'Order received', demandeOk: 'Message received',
    reponse: 'The estate will get back to you shortly to confirm.',
    maquette: 'This is a mock-up: on the live site, this form will go straight to the estate’s inbox.',
    nombre: (v, dec) => v.toLocaleString('en-GB', { minimumFractionDigits: dec, maximumFractionDigits: dec }),
  } : {
    menuOuvrir: 'Ouvrir le menu', menuFermer: 'Fermer le menu',
    bouteilles: (n) => `${n} bouteille${n > 1 ? 's' : ''}`,
    cartons: (c, reste) => ` · ${c} carton${c > 1 ? 's' : ''}${reste ? ` et ${reste}` : ''}`,
    auMoinsUne: 'Indiquez au moins une bouteille.',
    aCompleter: 'Merci de compléter les champs indiqués.',
    merci: 'Merci', commandeOk: 'Commande bien reçue', demandeOk: 'Demande bien reçue',
    reponse: 'Le domaine vous répond rapidement pour confirmer.',
    maquette: 'Ceci est une maquette&nbsp;: sur le site en ligne, ce formulaire arrivera directement dans la boîte du domaine.',
    nombre: (v, dec) => v.toFixed(dec).replace('.', ','),
  };
  const memo = {
    lire(k) { try { return localStorage.getItem(k); } catch { return null; } },
    ecrire(k, v) { try { localStorage.setItem(k, v); } catch { /* navigation privée */ } },
  };

  /* En-tête : transparent sur la photo d'ouverture, plein ensuite */
  const top = $('#top');
  if (top) {
    const maj = () => top.classList.toggle('is-plein', scrollY > 40);
    maj();
    addEventListener('scroll', maj, { passive: true });
  }

  /* Menu mobile */
  const burger = $('.burger');
  const menu = $('#menu');
  if (burger && menu) {
    const ouvrir = (o) => {
      menu.hidden = !o;
      burger.setAttribute('aria-expanded', String(o));
      burger.setAttribute('aria-label', o ? T.menuFermer : T.menuOuvrir);
      document.body.classList.toggle('menu-ouvert', o);
    };
    burger.addEventListener('click', () => ouvrir(menu.hidden));
    $$('a', menu).forEach((a) => a.addEventListener('click', () => ouvrir(false)));
    addEventListener('keydown', (e) => { if (e.key === 'Escape' && !menu.hidden) { ouvrir(false); burger.focus(); } });
    matchMedia('(min-width: 981px)').addEventListener('change', (e) => { if (e.matches) ouvrir(false); });
  }

  /* Âge légal (Loi Évin) : demandé une fois, gardé dans le navigateur (même clé pour les deux langues) */
  const age = $('#age');
  if (age && memo.lire('gardette-age') !== 'oui') {
    age.hidden = false;
    document.body.style.overflow = 'hidden';
    document.body.classList.add('age-ouvert');
    const oui = $('[data-age="oui"]', age);
    oui.focus({ preventScroll: true });
    oui.addEventListener('click', () => {
      memo.ecrire('gardette-age', 'oui');
      age.hidden = true;
      document.body.style.overflow = '';
      document.body.classList.remove('age-ouvert');
    });
    $('[data-age="non"]', age).addEventListener('click', () => {
      $('.age-choix', age).hidden = true;
      $('.age-non', age).hidden = false;
    });
  }

  /* Photos de secours (voir secours() dans le gabarit) : si la photo a échoué avant que sa légende existe */
  $$('img[data-echec]').forEach((img) => { const l = img.dataset.legende && document.getElementById(img.dataset.legende); if (l) l.hidden = true; });

  /* Apparitions au défilement (et tracé de la crête des Dentelles) */
  const blocs = $$('.rv, .devoile, .trace');
  if ('IntersectionObserver' in window && !calme) {
    const io = new IntersectionObserver((entrees) => entrees.forEach((e) => {
      if (e.isIntersecting) { e.target.classList.add('vu'); io.unobserve(e.target); }
    }), { rootMargin: '0px 0px -10% 0px', threshold: 0.06 });
    blocs.forEach((b) => io.observe(b));
  } else {
    blocs.forEach((b) => b.classList.add('vu'));
  }

  /* Chiffres : comptent jusqu'à leur valeur quand ils apparaissent */
  const chiffres = $$('[data-compte]');
  if (chiffres.length && 'IntersectionObserver' in window && !calme) {
    const io = new IntersectionObserver((entrees) => entrees.forEach((e) => {
      if (!e.isIntersecting) return;
      io.unobserve(e.target);
      const el = e.target;
      const fin = parseFloat(el.dataset.compte.replace(',', '.'));
      const dec = (el.dataset.compte.split(',')[1] || '').length;
      const t0 = performance.now();
      const pas = (t) => {
        const p = Math.min(1, (t - t0) / 1600);
        const v = fin * (1 - Math.pow(1 - p, 3));
        el.textContent = T.nombre(v, dec);
        if (p < 1) requestAnimationFrame(pas);
      };
      el.textContent = T.nombre(0, dec);
      requestAnimationFrame(pas);
    }), { threshold: 0.6 });
    chiffres.forEach((c) => io.observe(c));
  }

  /* Vitrine des cuvées : la photo suit la cuvée survolée */
  const vitrine = $('.vitrine');
  if (vitrine) {
    const liens = $$('.vitrine-liste a', vitrine);
    const visus = $$('.vitrine-visu figure', vitrine);
    const montrer = (i) => {
      liens.forEach((l, k) => l.classList.toggle('actif', k === i));
      visus.forEach((v, k) => v.classList.toggle('actif', k === i));
    };
    liens.forEach((l, i) => {
      l.addEventListener('pointerenter', () => montrer(i));
      l.addEventListener('focus', () => montrer(i));
    });
    montrer(0);
  }

  /* Sommaire collant (vins, domaine, caveau) : la partie lue est soulignée */
  const sommaire = $('.sommaire');
  if (sommaire && 'IntersectionObserver' in window) {
    const liens = $$('a', sommaire);
    const cibles = liens.map((l) => document.getElementById(l.hash.slice(1))).filter(Boolean);
    const io = new IntersectionObserver((entrees) => entrees.forEach((e) => {
      if (!e.isIntersecting) return;
      liens.forEach((l) => {
        const ici = l.getAttribute('href') === '#' + e.target.id;
        l.classList.toggle('actif', ici);
        if (ici) l.parentElement.parentElement.scrollTo({ left: l.parentElement.offsetLeft - 20, behavior: calme ? 'auto' : 'smooth' });
      });
    }), { rootMargin: '-45% 0px -50% 0px' });
    cibles.forEach((c) => io.observe(c));
  }

  /* Commande : quantités, total, livraison, cuvée choisie depuis la page des vins */
  const commande = $('#form-commande');
  if (commande) {
    const champs = $$('.quantite input', commande);
    const total = $('[data-total]', commande);
    const recompter = () => {
      const n = champs.reduce((s, i) => s + (Math.max(0, parseInt(i.value, 10)) || 0), 0);
      const cartons = Math.floor(n / 6);
      total.textContent = T.bouteilles(n) + (cartons ? T.cartons(cartons, n % 6) : '');
      total.classList.remove('bouge');
      void total.offsetWidth;
      total.classList.add('bouge');
    };
    $$('.quantite', commande).forEach((q) => {
      const champ = $('input', q);
      const regler = (d) => { champ.value = Math.max(0, Math.min(120, (parseInt(champ.value, 10) || 0) + d)); recompter(); };
      $('[data-plus]', q).addEventListener('click', () => regler(1));
      $('[data-moins]', q).addEventListener('click', () => regler(-1));
      champ.addEventListener('input', recompter);
    });
    const qs = new URLSearchParams(location.search);
    const voulue = qs.get('cuvee') || qs.get('wine');
    const ligne = voulue && $(`.ligne[data-cuvee="${CSS.escape(voulue)}"]`, commande);
    if (ligne) { $('input', ligne).value = 6; ligne.classList.add('choisie'); }
    recompter();
    const adresse = $('[data-livraison]', commande);
    $$('input[name="mode"]', commande).forEach((r) => r.addEventListener('change', () => {
      const livrer = $('input[name="mode"]:checked', commande).value === 'livraison';
      adresse.hidden = !livrer;
      $('textarea', adresse).required = livrer;
    }));
  }

  /* Formulaires : vérification, puis message (c'est une maquette, rien n'est envoyé) */
  $$('form[data-demo]').forEach((form) => {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const etat = $('.form-etat', form);
      let premier = null;
      $$('[required]', form).forEach((c) => {
        const ok = c.type === 'email' ? /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(c.value.trim()) : c.value.trim() !== '';
        c.closest('.champ')?.classList.toggle('a-erreur', !ok);
        if (!ok && !premier) premier = c;
      });
      if (form.id === 'form-commande' && !$$('.quantite input', form).some((i) => parseInt(i.value, 10) > 0)) {
        etat.textContent = T.auMoinsUne;
        return;
      }
      if (premier) {
        etat.textContent = T.aCompleter;
        premier.focus();
        return;
      }
      const titre = form.id === 'form-commande' ? T.commandeOk : T.demandeOk;
      form.innerHTML = `<div class="form-ok"><p class="k">${T.merci}</p><h3>${titre}</h3><p>${T.reponse}</p><p class="mention">${T.maquette}</p></div>`;
    });
  });

  $$('[data-annee]').forEach((el) => { el.textContent = new Date().getFullYear(); });
})();
