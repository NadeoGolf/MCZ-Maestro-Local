# MCZ Maestro Local pour Home Assistant

Intégration locale Home Assistant pour piloter un poêle MCZ Maestro via WebSocket, basée sur le protocole utilisé par `maestrogateway`. github.com/Chibald/maestrogateway

## À propos du projet

Ce projet a été réalisé avec l’aide de l’intelligence artificielle.

Je ne suis pas développeur de métier. Cette intégration a été construite progressivement pour répondre à un besoin personnel : piloter localement un poêle MCZ Maestro depuis Home Assistant, sans dépendre du cloud MCZ.

Le code, la structure Home Assistant, les entités et les corrections ont été générés, adaptés et améliorés avec l’aide de l’IA, puis testés dans mon environnement.

Le projet peut donc contenir des imperfections, des choix techniques discutables ou des limitations. Les retours, corrections et contributions sont les bienvenus.

## Remerciements

Merci aux projets et travaux existants ayant servi de base à la compréhension du protocole MCZ, notamment :

- `maestrogateway`, qui a servi de référence pour comprendre les commandes et le protocole WebSocket MCZ.
- La communauté Home Assistant pour la documentation, les exemples d’intégrations personnalisées et les bonnes pratiques.

## Configuration matérielle requise

Le poêle à granulés MCZ possède son propre réseau Wi-Fi (SSID). La solution la plus simple pour établir cette connexion consiste à utiliser un Raspberry Pi connecté à votre réseau local par câble Ethernet, et à configurer son Wi-Fi intégré pour se connecter au SSID du poêle à granulés. Cependant, tout appareil doté de deux interfaces réseau, dont au moins une interface Wi-Fi pour la connexion au poêle, conviendra.

## Fonctions principales

- Connexion locale WebSocket au poêle, par défaut `ws://192.168.120.1:81`. il faut être connecté au direct au Wifi du poêle.
- Thermostat Home Assistant avec deux modes de contrôle :
  - `home_assistant_thermostat` : Home Assistant régule ON/OFF avec hystérésis.
  - `mcz_native_setpoint` : la consigne de température est envoyée au poêle avec `Temperature_Setpoint`.
- Commande ON/OFF explicite :
  - `switch.alimentation`
- Puissance sous forme de liste déroulante `select` de 1 à 5.
- Commandes MCZ sûres ajoutées : Eco, Silent, Active, sons touches, profil, consigne native.
- Capteurs de diagnostic : firmware, database ID, heures de fonctionnement, heures avant entretien, nombre d’allumages, température carte mère, RPM vis sans fin, etc.
- Plusieurs capteurs de diagnostic sont désactivés par défaut pour garder l’interface Home Assistant lisible.
- Options de configuration : nom affiché, modèle, type Air/Hydro, mode de contrôle, intervalle de polling.

## Installation manuelle

Pour une installation manuelle, copie le dossier :

```text
custom_components/mcz_maestro
```

dans :

```text
/config/custom_components/mcz_maestro
```

Redémarre Home Assistant, puis ajoute l’intégration depuis :

```text
Paramètres → Appareils et services → Ajouter une intégration → MCZ Maestro Local
```

## Installation HACS

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=NadeoGolf&repository=MCZ-Maestro-Local&category=integration)

1. Installer HACS
2. Aller dans la section « Intégrations » de HACS
3. Cliquer sur les 3 points en haut à droite
4. Cliquer sur « Dépôts personnalisés »
5. Ajouter le dépôt [https://github.com/NadeoGolf/MCZ-Maestro-Local](https://github.com/NadeoGolf/MCZ-Maestro-Local) avec la catégorie Integration
6. Rechercher « Maestro MCZ » et l’ajouter
7. Dans l’interface Home Assistant (HA), aller dans « Configuration »
8. Cliquer sur « Intégrations »
9. Cliquer sur « + Ajouter une intégration »
10. Rechercher « Maestro MCZ »

## Configuration

Lors de l’ajout de l’intégration, renseigner les informations du poêle :

```text
Adresse IP
Port WebSocket
Nom affiché
Modèle
Type Air / Hydro
```

Exemple courant :

```text
Host : 192.168.120.1
Port : 81
```

L’écran `Configurer` de l’intégration conserve uniquement les réglages globaux :

- nom affiché
- modèle
- type de poêle
- mode de contrôle thermostat
- intervalle de lecture

Les paramètres fins du thermostat sont exposés directement comme entités de configuration dans la fiche appareil Home Assistant.

## Configuration thermostat depuis l’appareil

Les réglages du thermostat local Home Assistant sont exposés comme entités `number` dans la catégorie `Configuration` de l’appareil Home Assistant :

- `Tolérance froide thermostat` : allumage si la température ambiante est inférieure ou égale à la consigne moins cette valeur.
- `Tolérance chaude thermostat` : extinction si la température ambiante est supérieure ou égale à la consigne plus cette valeur.
- `Température absence thermostat` : température utilisée par le preset Away / absence.
- `Durée minimale cycle thermostat` : délai minimal entre deux commandes automatiques ON/OFF.

Exemple avec une consigne à 20 °C, une tolérance froide à 1,5 °C et une tolérance chaude à 0,5 °C :

```text
Allumage si température <= 18,5 °C
Extinction si température >= 20,5 °C
```

Ces paramètres concernent principalement le mode :

```text
home_assistant_thermostat
```

En mode :

```text
mcz_native_setpoint
```

la consigne est envoyée directement au poêle.

## Compatibilité

Projet développé pour un usage local avec un poêle MCZ Maestro compatible WebSocket.

Le protocole MCZ n’étant pas officiellement documenté, certaines valeurs peuvent varier selon :

- modèle du poêle
- version firmware
- type Air / Hydro
- options matérielles installées
- présence ou non de ventilateurs canalisés

## Limites connues

- Le protocole MCZ est basé sur rétro-ingénierie.
- Tous les modèles MCZ Maestro ne sont pas forcément compatibles.
- Certaines entités peuvent ne pas être pertinentes selon le modèle.

## Avertissement

Cette intégration pilote un appareil de chauffage.

Utilisation à vos risques et périls.

Vérifiez toujours le comportement du poêle après installation, mise à jour ou modification d’automatisations.

Ne laissez pas une automatisation non testée piloter l’allumage ou l’extinction du poêle sans surveillance initiale.
