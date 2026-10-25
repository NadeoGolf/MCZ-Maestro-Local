# Publication GitHub et installation HACS

Ce document décrit ce qui reste à faire **sur GitHub** après avoir envoyé les
fichiers du dépôt. Les paramètres du dépôt et une release ne sont pas créés
automatiquement par le ZIP.

## 1. Envoyer les fichiers

Ouvrir le dépôt `https://github.com/NadeoGolf/MCZ-Maestro-Local` puis copier
à sa racine **le contenu du dossier `MCZ-Maestro-Local`**, avec les fichiers
cachés (notamment `.github/` et `.gitignore`). Il ne faut pas créer de
sous-dossier `MCZ-Maestro-Local` supplémentaire dans le dépôt.

Via Git, depuis une copie locale du dépôt :

```bash
git add -A
git commit -m "Prepare GitHub and HACS metadata for v0.21.1"
git push origin main
```

## 2. Paramètres GitHub à régler manuellement

Dans la section **About** du dépôt, ajouter :

- Description : `Intégration locale Home Assistant pour poêles MCZ Maestro via WebSocket, sans cloud ni MQTT.`
- Topics : `home-assistant`, `hacs`, `mcz`, `maestro`, `pellet-stove`, `websocket`, `custom-integration`.
- Site web (optionnel) : `https://github.com/NadeoGolf/MCZ-Maestro-Local`.

Activer **Issues** et **Actions** dans les paramètres du dépôt si nécessaire.
Vérifier que les fichiers `LICENSE` et `.github/workflows/validate.yml`
apparaissent après le push.

## 3. Vérifier les contrôles GitHub Actions

Dans l'onglet **Actions**, lancer ou consulter `Validate integration`. Trois
vérifications sont prévues :

- `tests` : syntaxe Python et tests unitaires ;
- `hacs` : validation du dépôt par HACS ;
- `hassfest` : contrôle du manifeste et de l'intégration par Home Assistant.

Si un contrôle échoue, consulter son journal et corriger la cause **avant** de
publier la release. La réussite de ces actions ne prouve pas le fonctionnement
réel du poêle : le correctif d'extinction doit encore être validé sur l'appareil.

## 4. Créer une véritable release GitHub

Dans **Releases → Draft a new release**, créer le tag `v0.21.1`, choisir
`main`, puis rédiger les notes à partir de `CHANGELOG.md`.

**Important :** si `v0.21.1` existe déjà, ne réécrivez pas son tag ; une nouvelle
version doit alors être préparée avec une nouvelle numérotation cohérente dans
`manifest.json`, `const.py` et `CHANGELOG.md`.

HACS privilégie les releases GitHub publiées pour ses versions ; un simple tag
ne remplace pas une release. Le dépôt peut également être ajouté comme
**dépôt personnalisé** dans HACS, indépendamment de son éventuelle inscription
au catalogue HACS par défaut.

## 5. Installation par HACS

Depuis HACS, ajouter le dépôt GitHub comme **dépôt personnalisé** de type
**Intégration**, installer la version souhaitée, puis redémarrer Home Assistant.
Un accès réseau au WebSocket du poêle est nécessaire.

L'inscription au **catalogue HACS par défaut** requiert en plus une démarche
spécifique auprès du projet HACS ; la publication du ZIP ne la réalise pas.

## 6. Licence et attribution

Le protocole s'appuie sur les travaux du projet `Chibald/maestrogateway`, sous
licence GPL-3.0. Vérifier les conditions de redistribution et d'utilisation des
logos/marques tiers avant la publication. Le texte de la GPLv3 est dans
`LICENSE` ; les attributions et marques sont dans `NOTICE.md`.
