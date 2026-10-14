"""Assemble les pages du site : _src/layout.html + _src/pages/*.html → *.html à la racine.
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

# Photos de Gigondas et des Dentelles sur Wikimedia Commons, affichées depuis Commons (pas encore copiées sur le site).
# Si l'une ne s'affiche pas, la photo de secours (hébergée ici) prend sa place et sa légende disparaît (voir layout.html).
SECOURS = {
    'gres': ('/assets/img/gres-2000.webp', '/assets/img/gres-1200.webp 1200w, /assets/img/gres-2000.webp 2000w',
             'Rangs de vigne en été devant un mas et une pinède'),
    'rangs': ('/assets/img/vignes-rangs-2000.webp', '/assets/img/vignes-rangs-1200.webp 1200w, /assets/img/vignes-rangs-2000.webp 2000w',
              'Rangs de vieilles vignes taillées en gobelet, au printemps'),
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


def photo(cle, legende=''):
    """Attributs d'une photo Commons : src, srcset, photo de secours (et légende à masquer si le secours sert)."""
    fichier, largeurs, sec = PHOTOS[cle]
    s_src, s_srcset, s_alt = SECOURS[sec]
    srcset = ', '.join(f'{commons(fichier, w)} {w}w' for w in largeurs)
    attrs = (f'src="{commons(fichier, largeurs[-1])}" srcset="{srcset}" data-secours="{s_src}" '
             f'data-secours-srcset="{s_srcset}" data-secours-alt="{s_alt}"')
    if legende:
        attrs += f' data-legende="{legende}"'
    return attrs + ' referrerpolicy="no-referrer" onerror="secours(this)"'


def crete(classe='crete--ligne'):
    sym = 'crete-plein' if 'plein' in classe else 'crete-ligne'
    return f'<svg class="crete {classe}" viewBox="0 0 1600 200" aria-hidden="true" focusable="false"><use href="#{sym}"/></svg>'


# « Continuer la visite » : en bas des pages intérieures, les deux autres rubriques
RUBRIQUES = {
    'domaine': ('/domaine', 'Le domaine', 'La colline de la Gardette, 25 parcelles, les vendanges à la main.',
                f'<img {photo("vignes-dentelles")} alt="" width="960" height="1449" loading="lazy" decoding="async">'),
    'vins': ('/vins', 'Les vins', 'Trois Gigondas rouges et un rosé, de la Petite Gardette à Ventabren.',
             f'<span class="cc suite-cc" style="--c:var(--tradition)">{crete("crete--plein")}</span>'),
    'caveau': ('/caveau', 'Le caveau', 'Sur la place du village, du lundi au samedi.',
               f'<img {photo("place-village")} alt="" width="1920" height="1440" loading="lazy" decoding="async">'),
}


def suite(actif):
    if actif not in RUBRIQUES:
        return ''
    cartes = ''.join(
        f'<a class="suite-carte rv" href="{href}">{visuel}'
        f'<span class="k k--seul">Continuer la visite</span><b>{titre}</b><p>{texte}</p></a>'
        for cle, (href, titre, texte, visuel) in RUBRIQUES.items() if cle != actif)
    return f'    <section class="sec sec--serre" aria-label="Continuer la visite">\n      <div class="cadre suite">{cartes}</div>\n    </section>'


def fil(actif):
    if actif not in RUBRIQUES:
        return ''
    href, titre = RUBRIQUES[actif][:2]
    d = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Accueil', 'item': SITE + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': titre, 'item': SITE + href}]}
    return f'<script type="application/ld+json">{json.dumps(d, ensure_ascii=False)}</script>'


def developper(corps):
    """{{photo:cle}} ou {{photo:cle:id-legende}}, {{commons:cle}} (page Commons de la photo), {{crete}} ou {{crete:plein}}."""
    corps = re.sub(r'\{\{photo:([\w-]+)(?::([\w-]+))?\}\}', lambda m: photo(m[1], m[2] or ''), corps)
    corps = re.sub(r'\{\{commons:([\w-]+)\}\}', lambda m: page_commons(PHOTOS[m[1]][0]), corps)
    corps = re.sub(r'\{\{crete(?::(\w+))?\}\}', lambda m: crete('crete--' + (m[1] or 'ligne')), corps)
    return corps


for nom in sorted(os.listdir(os.path.join(ICI, 'pages'))):
    source = open(os.path.join(ICI, 'pages', nom), encoding='utf-8').read()
    m = re.match(r'<!--(\{.*?\})-->\n', source, re.S)
    meta, corps = json.loads(m.group(1)), developper(source[m.end():])
    # Pré-chargement de la photo d'ouverture (la plus grande image visible au chargement)
    preload = ''
    img = re.search(r'<img class="(?:hero|entete)-img" src="([^"]+)" srcset="([^"]+)".*? sizes="([^"]+)"', corps)
    if img:
        preload = (f'<link rel="preload" as="image" href="{img[1]}" imagesrcset="{img[2]}" imagesizes="{img[3]}" '
                   f'fetchpriority="high" referrerpolicy="no-referrer">')
    valeurs = {
        'titre': meta['titre'], 'description': meta['description'], 'version': VERSION,
        'classe': 'page-' + nom.removesuffix('.html'), 'tete_classe': ' top--sur' if img else '',
        'preload': preload, 'contenu': corps.rstrip(),
        'jsonld': f'<script type="application/ld+json">{json.dumps(JSONLD, ensure_ascii=False)}</script>' if meta.get('jsonld') else fil(meta.get('actif')),
        'suite': suite(meta.get('actif')),
        'crete_d': CRETE, 'crete_ligne': crete('crete--ligne'),
    }
    for page in ('domaine', 'vins', 'caveau'):
        valeurs[f'actif_{page}'] = ' aria-current="page"' if meta.get('actif') == page else ''
    html = re.sub(r'\{\{(\w+)\}\}', lambda x: valeurs[x[1]], GABARIT)
    html = re.sub(r'\n\s*\n(\s*<link rel="stylesheet")', r'\n\1', html)
    open(os.path.join(RACINE, nom), 'w', encoding='utf-8').write(html)
    print(nom, len(html) // 1024, 'Ko')
