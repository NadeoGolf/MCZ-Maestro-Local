# Historique des modifications

## 0.21.2 — 1er novembre 2026

### Correctif

- Les ventilateurs déclarent les fonctions `TURN_ON` / `TURN_OFF` exigées par Home Assistant : `fan.turn_on`, `fan.turn_off` et le bouton marche/arrêt de l'interface étaient refusés (« service non pris en charge »).

### Nettoyage et optimisation (sans changement de comportement)

- Entité de base commune (`entity.py`) : identifiant unique, appareil, envoi de commande suivi d'un rafraîchissement.
- Le coordinateur est stocké dans `entry.runtime_data` au lieu de `hass.data`.
- Activation par défaut des entités via le champ standard `entity_registry_enabled_default`.
- Constantes de préréglages et attributs reprises de Home Assistant ; lecture des options numériques factorisée.
- Climat : `turn_on` / `turn_off` délèguent à `set_hvac_mode`, application de la consigne factorisée.
- Protocole : table de correspondance des commandes, champs positionnels en dictionnaire, branche de décodage morte supprimée, trame décodée une seule fois.
- Tests supplémentaires sur le protocole.

## 0.21.1 — 25 octobre 2026

### Correctif

- Évite de renvoyer la commande MCZ `Power=OFF` (`C|WriteParametri|34|40`) lorsque le dernier état physique connu du poêle vaut `0` (éteint), `40` (extinction) ou `41` (refroidissement).
- Conserve la possibilité d'envoyer OFF dans les autres états, y compris `45` et `46`, et lorsque l'état physique est inconnu, pour ne pas bloquer un arrêt nécessaire.
- Ajoute une trace `debug` quand une commande OFF redondante est ignorée.
- Harmonise la version des diagnostics et du manifeste sur `0.21.1`.
- Ajoute des tests de non-régression ciblés sur l'envoi des commandes d'alimentation.

### Correctifs complémentaires

- Le formulaire d'options n'efface plus les tolérances, la température d'absence ni la durée minimale de cycle réglées via les entités `number`.
- Modifier un réglage du thermostat ne recharge plus toute l'intégration (plus de reconnexion ni d'entités indisponibles, l'anti-cycle court est conservé).
- Un poêle qui ne répond pas à la demande d'état est désormais signalé comme indisponible au lieu de conserver d'anciennes valeurs.
- Les échecs de commande sont remontés comme erreurs Home Assistant lisibles ; un échec de la régulation automatique est journalisé.
- Les diagnostics masquent l'adresse IP du poêle dans le titre, l'identifiant unique et les messages d'erreur.
- Version minimale de Home Assistant portée à **2024.11.0** (requise par le formulaire d'options).
- Suppression de la plateforme `binary_sensor` vide et inutilisée.
- Ajout du workflow `.github/workflows/validate.yml` et d'un `.gitignore`, absents de l'envoi précédent.

### Documentation et préparation GitHub/HACS

- README GitHub enrichi : installation HACS, prérequis réseau et fonctionnalités réellement implémentées.
- Complète le manifeste (`issue_tracker`, `codeowners`, `integration_type`) et retire l'ancienne option HACS non documentée `render_readme`.
- Ajoute `strings.json` et la traduction anglaise pour les formulaires de configuration.
- Ajoute les validations GitHub Actions (tests Python, HACS et hassfest), les templates de contributions et le guide de publication.
- Ajoute le texte de la licence GPLv3 et les attributions au projet maestrogateway.

> Correctif vérifié par tests simulés : **pas encore validé sur un poêle physique**. La décision d'ignorer OFF repose sur le dernier état reçu par Home Assistant ; en cas de doute ou d'information obsolète, vérifier l'état réel du poêle.

## 0.21.0

- Version de référence de l'archive d'origine fournie pour cette mise à jour.
