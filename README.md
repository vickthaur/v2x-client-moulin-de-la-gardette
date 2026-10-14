# Moulin de la Gardette · maquette de refonte

Proposition de nouveau site pour le **Moulin de la Gardette** (Jean-Baptiste Meunier, Gigondas), préparée par V2X Studio.

- Maquette : https://v2x-client-moulin-de-la-gardette.vercel.app (non indexée : `noindex` + `robots.txt`)
- Site actuel : https://moulindelagardette.fr/ (page d'entrée « ENTER », frames, ancien Google Analytics)

## Ce qu'il y a dedans

Même niveau que la maquette du Domaine de Saje, avec l'identité de Gigondas : lie-de-vin et calcaire des Dentelles, rose grenache, une ligne de crête des Dentelles dessinée qui sert de signature (pied de page, âge légal, fiches des cuvées). Pas de 3D, pas d'effet gratuit.

- **Accueil** : photo d'ouverture (le vignoble de Gigondas sous les Dentelles), le domaine en une phrase et quatre chiffres (10 ha, 25 parcelles, 50 ans d'âge moyen, 100 ans pour Ventabren), vitrine des quatre cuvées (la fiche suit la cuvée survolée), bandeau terroir, le vigneron et Zoé, le caveau et ses horaires, « Où trouver nos vins » (Decanter, Berry Bros. & Rudd, The Wine Society, Vine Trail, K&L, La Grande Épicerie).
- **Le domaine** : repères (1670, 1958, 1988, 2003, 2012, Zoé), le vignoble (25 parcelles de 100 à 330 m, marnes du Trias, sables du Miocène, bio depuis 2012), les vendanges (tardives, à la main, grappes entières), la cave en quatre chiffres, l'année au domaine, la relève.
- **Les vins** : un chapitre par cuvée avec sommaire collant (fiche, cépages, âge des vignes, élevage), tableau comparatif, bouton « Commander » qui pré-remplit la commande.
- **Le caveau** : adresse, plan, horaires, formulaire de contact, commande (quantités, cartons, retrait ou livraison).
- Âge légal à la première visite, Loi Évin, mentions légales, page 404, données structurées `Winery`.
- Formulaires en mode maquette : ils vérifient la saisie et affichent une confirmation, sans rien envoyer.
- Pastille « Proposition de refonte » (`assets/js/proposition.js`) : chaque ouverture remonte dans le CRM (fiche `moulin-de-la-gardette`). Pour ne pas compter tes propres visites : ouvre une fois la maquette avec `?moi`.

## D'où viennent les textes

Rien d'inventé : tout vient de sources publiques, recoupées quand c'était possible.

- Site du domaine (pages en anglais et en français) : cépages et âges des vignes de la Petite Gardette, de la Tradition, de Ventabren et du rosé, élevages, adresse, téléphone, e-mail `info@moulindelagardette.com`, horaires.
- Fiche du domaine sur gigondas-vin.com (l'appellation) : 10 ha, reprise en 1988, Zoé, vignes de 50 ans en moyenne, bio depuis 2012, vendanges manuelles et tardives, levures indigènes.
- Vine Trail (importateur UK) : coteau réputé depuis 1670, nom apparu en 1958 (Geneviève Jurdic et Laurent Meunier), le moulin, sols, 25 parcelles, vendange 2019 à la mi-octobre, cave de 2003, Tradition non collée non filtrée.
- Decanter (Matt Walls) : passage chez Diamond Creek, vendange après la pluie, très peu de soufre, sélection « 10 of the most exciting southern Rhône estates ».
- K&L, Berry Bros. & Rudd, The Wine Society, La Grande Épicerie : où le vin est vendu, nom de Ventabren (« là où souffle le vent »).

**À confirmer avec Jean-Baptiste** : l'assemblage de la Tradition (le site du domaine dit 10 % mourvèdre et 10 % cinsault ; certains cavistes donnent de la syrah à la place), les horaires actuels du caveau, l'appellation exacte du rosé, la position exacte du caveau sur la carte (marqueur au centre du village).

## Photos

Les photos de Gigondas et des Dentelles sont affichées **directement depuis Wikimedia Commons** (elles n'ont pas pu être téléchargées pendant la préparation). Si une photo ne s'affiche pas, une photo de secours hébergée sur le site prend sa place et sa légende disparaît (fonction `secours()` dans `_src/layout.html`). Les photos de secours (rangs de vigne, vignoble et mas) et la vendangeuse viennent de la maquette Saje (Wikimedia Commons, crédits dans les mentions légales).

**À vérifier en ouvrant la maquette** : que chaque photo Commons s'affiche bien et montre ce qu'annonce sa légende. Sinon, changer le fichier dans `PHOTOS` (`_src/build.py`).

Les cuvées sont présentées par des fiches typographiques (âge des vignes, assemblage) à la place des bouteilles, en attendant des photos.

## Modifier

- Textes : `_src/pages/*.html` (une page par fichier), gabarit commun `_src/layout.html`, puis `python3 _src/build.py`.
- Photos Commons : `PHOTOS` dans `_src/build.py` ; dans les pages, `{{photo:cle}}` (ou `{{photo:cle:id-de-la-legende}}`).
- Ligne de crête : `_src/crete.py` régénère `_src/crete.txt` (graine fixe).
- Styles : `assets/css/site.css` (couleurs et polices en variables au début, couleurs des cuvées `--rose`, `--petite`, `--tradition`, `--ventabren`). Titres en Newsreader, texte en Geist (polices hébergées sur le site).

## Avant la mise en ligne réelle

1. Photos du domaine : Jean-Baptiste et Zoé, les vignes de la Gardette, la cave, le caveau, les quatre bouteilles. Copier sur le site les photos Commons gardées (au lieu de les afficher depuis Commons).
2. Version anglaise (vins vendus au Royaume-Uni et aux États-Unis).
3. Prix et millésimes disponibles → éventuellement boutique avec paiement (Stripe).
4. Formulaires : brancher l'envoi des e-mails vers info@moulindelagardette.com (Resend).
5. Mentions légales : SIRET.
6. Domaine `moulindelagardette.fr` dans Vercel, retirer `noindex` (vercel.json, layout, robots.txt) et `proposition.js`, ajouter les redirections des anciennes adresses.
