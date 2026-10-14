"""Assemble les pages du site : _src/layout.html + _src/pages/*.html → *.html à la racine,
   et la version anglaise _src/pages/en/*.html → en.html (accueil, servi sur /en) et en/<slug>.html.
   Lancer : python3 _src/build.py"""
import hashlib
import json
import os
import re
import urllib.parse

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
GABARIT = open(os.path.join(ICI, 'layout.html'), encoding='utf-8').read()
CRETE = open(os.path.join(ICI, 'crete.txt'), encoding='utf-8').read().strip()

empreinte = hashlib.sha1()
for f in ('assets/css/site.css', 'assets/js/site.js', 'assets/js/proposition.js'):
    empreinte.update(open(os.path.join(RACINE, f), 'rb').read())
VERSION = empreinte.hexdigest()[:8]

SITE = 'https://moulindelagardette.fr'
MAQUETTE = 'https://v2x-client-moulin-de-la-gardette.vercel.app'   # URL absolues des balises hreflang
JOURS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
JSONLD = {
    '@context': 'https://schema.org', '@type': 'Winery', 'name': 'Moulin de la Gardette',
    'description': 'Domaine familial de 10 hectares à Gigondas, au pied des Dentelles de Montmirail, conduit par '
                   'Jean-Baptiste Meunier : agriculture biologique, vendanges à la main, vinification sans levures ajoutées.',
    'founder': {'@type': 'Person', 'name': 'Jean-Baptiste Meunier'},
    'address': {'@type': 'PostalAddress', 'streetAddress': '11 place Gabriel-Andéol', 'postalCode': '84190',
                'addressLocality': 'Gigondas', 'addressRegion': 'Vaucluse', 'addressCountry': 'FR'},
    'geo': {'@type': 'GeoCoordinates', 'latitude': 44.1644, 'longitude': 5.0056},
    'telephone': '+33490658151', 'email': 'info@moulindelagardette.com', 'url': SITE + '/',
    'image': SITE + '/assets/img/partage.jpg',
    'openingHoursSpecification': [
        {'@type': 'OpeningHoursSpecification', 'dayOfWeek': JOURS, 'opens': '10:00', 'closes': '13:00'},
        {'@type': 'OpeningHoursSpecification', 'dayOfWeek': JOURS, 'opens': '14:30', 'closes': '18:30'},
    ],
}
JSONLD_EN = {**JSONLD, 'url': SITE + '/en',
             'description': 'A 10-hectare family estate in Gigondas, below the Dentelles de Montmirail, run by '
                            'Jean-Baptiste Meunier: certified organic, picked by hand, fermented with native yeasts.'}

# ---------- Deux langues ----------
# Chemins publics des pages, par langue (les pages anglaises sont dans _src/pages/en/)
CHEMINS = {
    'fr': {'accueil': '/', 'domaine': '/domaine', 'vins': '/vins', 'caveau': '/caveau', 'mentions': '/mentions-legales'},
    'en': {'accueil': '/en', 'domaine': '/en/estate', 'vins': '/en/wines', 'caveau': '/en/cellar-door',
           'mentions': '/en/legal-notice'},
}
# Ancres utilisées par le gabarit (les ancres des cuvées sont les mêmes dans les deux langues)
ANCRES = {
    'fr': {'colline': 'colline', 'vignoble': 'vignoble', 'vendanges': 'vendanges', 'cave': 'cave', 'annee': 'annee',
           'releve': 'releve', 'infos': 'infos', 'ecrire': 'ecrire', 'commande': 'commande', 'lieux': 'lieux',
           'photos': 'photos'},
    'en': {'colline': 'hill', 'vignoble': 'vineyard', 'vendanges': 'harvest', 'cave': 'winery', 'annee': 'year',
           'releve': 'next-generation', 'infos': 'visit', 'ecrire': 'contact', 'commande': 'order',
           'lieux': 'where-to-buy', 'photos': 'photos'},
}
# Textes du gabarit : {{t_cle}} dans layout.html
EVIN_FR = 'L’abus d’alcool est dangereux pour la santé, à consommer avec modération.'
TEXTES = {
    'fr': {
        'saut': 'Aller au contenu',
        'age_t': 'Avez-vous l’âge légal pour consommer de l’alcool&nbsp;?',
        'age_oui': 'Oui, j’ai plus de 18 ans', 'age_non': 'Non',
        'age_refus': 'Ce site présente des vins&nbsp;: il est réservé aux personnes majeures. À bientôt.',
        'age_loi': EVIN_FR,
        'nav': 'Navigation principale', 'nav_d': 'Navigation secondaire', 'menu': 'Menu', 'pied': 'Pied de page',
        'logo': 'Moulin de la Gardette, accueil',
        'accueil': 'Accueil', 'domaine': 'Le domaine', 'vins': 'Les vins', 'caveau': 'Le caveau',
        'colline': 'La colline de la Gardette', 'colline_court': 'La colline', 'vignoble': 'Le vignoble',
        'vendanges': 'Les vendanges', 'cave': 'La cave', 'annee': 'L’année au domaine', 'releve': 'La relève',
        'ans': 'ans d’âge', 'grappes': 'grappes entières', 'petite': 'La Petite Gardette', 'rose': 'Le rosé',
        'rose_court': 'Rosé', 'toutes': 'Toutes les cuvées',
        'infos': 'Horaires et accès', 'ecrire': 'Écrire au domaine', 'ecrire_court': 'Écrire',
        'commander_vin': 'Commander du vin', 'lieux': 'Où trouver nos vins',
        'cta': 'Commander', 'commander': 'Commander', 'menu_ouvrir': 'Ouvrir le menu',
        'tel': '04 90 65 81 51', 'adresse_courte': '11 place Gabriel-Andéol, Gigondas',
        'pied_sous': 'AOC Gigondas · Agriculture biologique<br>Famille Meunier, au pied des Dentelles de Montmirail',
        'pied_adresse': '11 place Gabriel-Andéol<br>84190 Gigondas',
        'pied_horaires': 'Du lundi au samedi<br>10&nbsp;h – 13&nbsp;h, puis 14&nbsp;h 30 – 18&nbsp;h 30 (14&nbsp;h – 18&nbsp;h l’hiver)',
        'mentions': 'Mentions légales',
        'evin': EVIN_FR + ' La vente d’alcool est interdite aux mineurs.',
        'credits': 'Paysages de Gigondas&nbsp;: Wikimedia Commons, <a href="/mentions-legales#photos">crédits</a> · '
                   'Site réalisé par <a href="https://v2x-studio.fr" rel="noopener">V2X Studio</a>',
        'suite': 'Continuer la visite', 'fil_accueil': 'Accueil',
    },
    'en': {
        'saut': 'Skip to content',
        'age_t': 'Are you of legal drinking age?',
        'age_oui': 'Yes, I am over 18', 'age_non': 'No',
        'age_refus': 'This website is about wine and is for adults only. Goodbye for now.',
        'age_loi': f'<span lang="fr">{EVIN_FR}</span><br>Alcohol abuse is dangerous for your health. Please drink in moderation.',
        'nav': 'Main navigation', 'nav_d': 'Secondary navigation', 'menu': 'Menu', 'pied': 'Footer',
        'logo': 'Moulin de la Gardette, home',
        'accueil': 'Home', 'domaine': 'The estate', 'vins': 'The wines', 'caveau': 'Cellar door',
        'colline': 'The Gardette hill', 'colline_court': 'The hill', 'vignoble': 'The vineyard',
        'vendanges': 'The harvest', 'cave': 'The winery', 'annee': 'A year at the estate', 'releve': 'The next generation',
        'ans': 'year-old vines', 'grappes': 'whole bunches', 'petite': 'La Petite Gardette', 'rose': 'The rosé',
        'rose_court': 'Rosé', 'toutes': 'All the wines',
        'infos': 'Opening hours and directions', 'ecrire': 'Contact the estate', 'ecrire_court': 'Contact',
        'commander_vin': 'Order wine', 'lieux': 'Where to find our wines',
        'cta': 'Order', 'commander': 'Order wine', 'menu_ouvrir': 'Open menu',
        'tel': '+33 4 90 65 81 51', 'adresse_courte': '11 place Gabriel-Andéol, Gigondas',
        'pied_sous': 'AOC Gigondas · Organic farming<br>The Meunier family, at the foot of the Dentelles de Montmirail',
        'pied_adresse': '11 place Gabriel-Andéol<br>84190 Gigondas, France',
        'pied_horaires': 'Monday to Saturday<br>10am–&#8288;1pm and 2.30pm–&#8288;6.30pm (2pm–&#8288;6pm in winter)',
        'mentions': 'Legal notice',
        'evin': f'<span lang="fr">{EVIN_FR} La vente d’alcool est interdite aux mineurs.</span><br>'
                'Alcohol abuse is dangerous for your health. Please drink in moderation. '
                'The sale of alcohol to minors is prohibited.',
        'credits': 'Gigondas landscapes: Wikimedia Commons, <a href="/en/legal-notice#photos">credits</a> · '
                   'Website by <a href="https://v2x-studio.fr" rel="noopener">V2X Studio</a>',
        'suite': 'Continue your visit', 'fil_accueil': 'Home',
    },
}
# Petits drapeaux du sélecteur de langue : un seul SVG par drapeau, posé en <symbol> dans le gabarit
# (page française : drapeau britannique à côté de « EN » ; page anglaise : drapeau français à côté de « FR »)
DRAPEAUX = {
    'en': '<symbol id="drapeau-en" viewBox="0 0 60 30" preserveAspectRatio="xMidYMid slice">'
          '<clipPath id="drapeau-en-x"><path d="M30 15h30v15zv15H0zH0V0zV0h30z"/></clipPath>'
          '<path d="M0 0h60v30H0z" fill="#012169"/><path d="M0 0l60 30M60 0L0 30" stroke="#fff" stroke-width="6"/>'
          '<path d="M0 0l60 30M60 0L0 30" clip-path="url(#drapeau-en-x)" stroke="#c8102e" stroke-width="4"/>'
          '<path d="M30 0v30M0 15h60" stroke="#fff" stroke-width="10"/><path d="M30 0v30M0 15h60" stroke="#c8102e" stroke-width="6"/>'
          '</symbol>',
    'fr': '<symbol id="drapeau-fr" viewBox="0 0 3 2" preserveAspectRatio="xMidYMid slice">'
          '<path d="M0 0h1v2H0z" fill="#002395"/><path d="M1 0h1v2H1z" fill="#fff"/><path d="M2 0h1v2H2z" fill="#ed2939"/>'
          '</symbol>',
}
VERSION_DE = {'en': 'English version', 'fr': 'Version française'}


def lien_langue(autre, cible, classe=''):
    """Lien « EN » / « FR » vers la page équivalente dans l'autre langue, avec son petit drapeau."""
    return (f'<a class="langue{classe}" href="{cible}" hreflang="{autre}" lang="{autre}" aria-label="{VERSION_DE[autre]}">'
            f'<span class="drapeau" aria-hidden="true"><svg viewBox="0 0 16 11" focusable="false"><use href="#drapeau-{autre}" width="16" height="11"/></svg></span>'
            f'{autre.upper()}</a>')


# Photos de Gigondas et des Dentelles sur Wikimedia Commons, affichées depuis Commons (pas encore copiées sur le site).
# Si l'une ne s'affiche pas, la photo de secours (hébergée ici) prend sa place et sa légende disparaît (voir layout.html).
SECOURS = {
    'gres': ('/assets/img/gres-2000.webp', '/assets/img/gres-1200.webp 1200w, /assets/img/gres-2000.webp 2000w',
             {'fr': 'Rangs de vigne en été devant un mas et une pinède',
              'en': 'Rows of vines in summer in front of a farmhouse and pine trees'}),
    'rangs': ('/assets/img/vignes-rangs-2000.webp', '/assets/img/vignes-rangs-1200.webp 1200w, /assets/img/vignes-rangs-2000.webp 2000w',
              {'fr': 'Rangs de vieilles vignes taillées en gobelet, au printemps',
               'en': 'Rows of old bush-trained vines in spring'}),
}
# clé : (fichier sur Commons, largeurs demandées, photo de secours)
PHOTOS = {
    'vignoble-dentelles': ('Vignoble de Gigondas dans les dentelles de Montmirail.jpg', (1280, 1920), 'gres'),
    'vignes-dentelles': ('Gigondas Dentelles de Montmirail et vignes.jpg', (960,), 'rangs'),
    'place-village': ('La place des vignerons, au coeur du centre historique de Gigondas.jpg', (1280, 1920), 'rangs'),
    'panorama': ("Panorama sur le vignoble à l'intérieur des Dentelles de Montmirail.jpg", (1280,), 'rangs'),
    'dentelles': ('Dentelles de montmirail.jpg', (1280,), 'gres'),
    'rocher-du-midi': ('Gigondas 84- Rocher du Midi 470m- STCH.jpg', (1280,), 'rangs'),
    'sarrasines': ('Dentelles Sarrasines.jpg', (1280,), 'gres'),
}


def commons(fichier, largeur):
    nom = fichier.replace(' ', '_')
    h = hashlib.md5(nom.encode('utf-8')).hexdigest()
    q = urllib.parse.quote(nom, safe="(),'!_-.~")
    return f'https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[:2]}/{q}/{largeur}px-{q}'


def page_commons(fichier):
    return 'https://commons.wikimedia.org/wiki/File:' + urllib.parse.quote(fichier.replace(' ', '_'), safe="(),'!_-.~")


def photo(cle, legende='', langue='fr'):
    """Attributs d'une photo Commons : src, srcset, photo de secours (et légende à masquer si le secours sert)."""
    fichier, largeurs, sec = PHOTOS[cle]
    s_src, s_srcset, s_alt = SECOURS[sec]
    srcset = ', '.join(f'{commons(fichier, w)} {w}w' for w in largeurs)
    attrs = (f'src="{commons(fichier, largeurs[-1])}" srcset="{srcset}" data-secours="{s_src}" '
             f'data-secours-srcset="{s_srcset}" data-secours-alt="{s_alt[langue]}"')
    if legende:
        attrs += f' data-legende="{legende}"'
    return attrs + ' referrerpolicy="no-referrer" onerror="secours(this)"'


def crete(classe='crete--ligne'):
    sym = 'crete-plein' if 'plein' in classe else 'crete-ligne'
    return f'<svg class="crete {classe}" viewBox="0 0 1600 200" aria-hidden="true" focusable="false"><use href="#{sym}"/></svg>'


# « Continuer la visite » : en bas des pages intérieures, les deux autres rubriques
TEXTES_RUBRIQUES = {
    'fr': {'domaine': ('Le domaine', 'La colline de la Gardette, 25 parcelles, les vendanges à la main.'),
           'vins': ('Les vins', 'Trois Gigondas rouges et un rosé, de la Petite Gardette à Ventabren.'),
           'caveau': ('Le caveau', 'Sur la place du village, du lundi au samedi.')},
    'en': {'domaine': ('The estate', 'The Gardette hill, 25 plots, picked by hand.'),
           'vins': ('The wines', 'Three red Gigondas and a rosé, from La Petite Gardette to Ventabren.'),
           'caveau': ('Cellar door', 'On the village square, Monday to Saturday.')},
}


def rubriques(langue):
    visuels = {
        'domaine': f'<img {photo("vignes-dentelles", langue=langue)} alt="" width="960" height="1449" loading="lazy" decoding="async">',
        'vins': f'<span class="cc suite-cc" style="--c:var(--tradition)">{crete("crete--plein")}</span>',
        'caveau': f'<img {photo("place-village", langue=langue)} alt="" width="1920" height="1440" loading="lazy" decoding="async">',
    }
    return {cle: (CHEMINS[langue][cle], *TEXTES_RUBRIQUES[langue][cle], visuels[cle]) for cle in visuels}


def suite(actif, langue):
    rub = rubriques(langue)
    if actif not in rub:
        return ''
    k = TEXTES[langue]['suite']
    cartes = ''.join(
        f'<a class="suite-carte rv" href="{href}">{visuel}'
        f'<span class="k k--seul">{k}</span><b>{titre}</b><p>{texte}</p></a>'
        for cle, (href, titre, texte, visuel) in rub.items() if cle != actif)
    return f'    <section class="sec sec--serre" aria-label="{k}">\n      <div class="cadre suite">{cartes}</div>\n    </section>'


def fil(actif, langue):
    if actif not in TEXTES_RUBRIQUES[langue]:
        return ''
    href, titre = CHEMINS[langue][actif], TEXTES_RUBRIQUES[langue][actif][0]
    d = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': TEXTES[langue]['fil_accueil'],
         'item': SITE + ('/' if langue == 'fr' else CHEMINS[langue]['accueil'])},
        {'@type': 'ListItem', 'position': 2, 'name': titre, 'item': SITE + href}]}
    return f'<script type="application/ld+json">{json.dumps(d, ensure_ascii=False)}</script>'


def developper(corps, langue):
    """{{photo:cle}} ou {{photo:cle:id-legende}}, {{commons:cle}} (page Commons de la photo), {{crete}} ou {{crete:plein}}."""
    corps = re.sub(r'\{\{photo:([\w-]+)(?::([\w-]+))?\}\}', lambda m: photo(m[1], m[2] or '', langue), corps)
    corps = re.sub(r'\{\{commons:([\w-]+)\}\}', lambda m: page_commons(PHOTOS[m[1]][0]), corps)
    corps = re.sub(r'\{\{crete(?::(\w+))?\}\}', lambda m: crete('crete--' + (m[1] or 'ligne')), corps)
    return corps


def pages():
    """(langue, source, fichier produit, chemin public) : pages françaises, puis anglaises."""
    dossier = os.path.join(ICI, 'pages')
    for nom in sorted(os.listdir(dossier)):
        if nom.endswith('.html'):
            slug = nom.removesuffix('.html')
            yield 'fr', os.path.join(dossier, nom), nom, '/' if slug == 'index' else '/' + slug
    for nom in sorted(os.listdir(os.path.join(dossier, 'en'))):
        if nom.endswith('.html'):
            slug = nom.removesuffix('.html')
            sortie, chemin = ('en.html', '/en') if slug == 'index' else ('en/' + nom, '/en/' + slug)
            yield 'en', os.path.join(dossier, 'en', nom), sortie, chemin


os.makedirs(os.path.join(RACINE, 'en'), exist_ok=True)
for langue, source_f, sortie, chemin in pages():
    source = open(source_f, encoding='utf-8').read()
    m = re.match(r'<!--(\{.*?\})-->\n', source, re.S)
    meta, corps = json.loads(m.group(1)), developper(source[m.end():], langue)
    assert meta.get('langue', 'fr') == langue, f'{source_f} : "langue" ne correspond pas au dossier'
    autre = 'en' if langue == 'fr' else 'fr'
    chemin_autre = meta[autre]
    chemin_fr = chemin if langue == 'fr' else chemin_autre
    # Balises hreflang (pas sur la page 404, qui n'a pas d'équivalent)
    hreflang = ''
    if not sortie.startswith('404'):
        chemin_en = chemin if langue == 'en' else chemin_autre
        hreflang = (f'<link rel="alternate" hreflang="fr" href="{MAQUETTE}{chemin_fr}">\n'
                    f'  <link rel="alternate" hreflang="en" href="{MAQUETTE}{chemin_en}">\n'
                    f'  <link rel="alternate" hreflang="x-default" href="{MAQUETTE}{chemin_fr}">')
    # Pré-chargement de la photo d'ouverture (la plus grande image visible au chargement)
    preload = ''
    img = re.search(r'<img class="(?:hero|entete)-img" src="([^"]+)" srcset="([^"]+)".*? sizes="([^"]+)"', corps)
    if img:
        preload = (f'<link rel="preload" as="image" href="{img[1]}" imagesrcset="{img[2]}" imagesizes="{img[3]}" '
                   f'fetchpriority="high" referrerpolicy="no-referrer">')
    jsonld = JSONLD if langue == 'fr' else JSONLD_EN
    valeurs = {
        'langue': langue, 'og_locale': 'fr_FR' if langue == 'fr' else 'en_GB',
        'og_locale_autre': 'en_GB' if langue == 'fr' else 'fr_FR', 'hreflang': hreflang,
        'titre': meta['titre'], 'description': meta['description'], 'version': VERSION,
        'classe': 'page-' + (chemin_fr.strip('/') or 'index'), 'tete_classe': ' top--sur' if img else '',
        'preload': preload, 'contenu': corps.rstrip(),
        'jsonld': f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if meta.get('jsonld') else fil(meta.get('actif'), langue),
        'suite': suite(meta.get('actif'), langue),
        'crete_d': CRETE, 'crete_ligne': crete('crete--ligne'),
        'drapeau': DRAPEAUX[autre],
        'langue_nav': lien_langue(autre, chemin_autre), 'langue_tete': lien_langue(autre, chemin_autre, ' langue--tete'),
        'langue_menu': lien_langue(autre, chemin_autre, ' langue--menu'),
        **{'u_' + k: v for k, v in CHEMINS[langue].items()},
        **{'a_' + k: v for k, v in ANCRES[langue].items()},
        **{'t_' + k: v for k, v in TEXTES[langue].items()},
    }
    for page in ('domaine', 'vins', 'caveau'):
        valeurs[f'actif_{page}'] = ' aria-current="page"' if meta.get('actif') == page else ''
    html = re.sub(r'\{\{(\w+)\}\}', lambda x: valeurs[x[1]], GABARIT)
    html = re.sub(r'\n\s*\n(\s*<link rel="(?:stylesheet|preload)")', r'\n\1', html)
    open(os.path.join(RACINE, sortie), 'w', encoding='utf-8').write(html)
    print(sortie, len(html) // 1024, 'Ko')
