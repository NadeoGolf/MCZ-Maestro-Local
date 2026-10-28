<p align="center">
  <img src="custom_components/mcz_maestro/brand/logo.png" alt="Logo MCZ" width="140">
</p>

# MCZ Maestro Local pour Home Assistant

[![Validate integration](https://github.com/NadeoGolf/MCZ-Maestro-Local/actions/workflows/validate.yml/badge.svg)](https://github.com/NadeoGolf/MCZ-Maestro-Local/actions/workflows/validate.yml)

**Pilotez et surveillez votre poêle à granulés MCZ Maestro directement depuis Home Assistant, en local, sans passer par le cloud MCZ.**

[![Ajouter le dépôt à HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=NadeoGolf&repository=MCZ-Maestro-Local&category=integration)

> [!IMPORTANT]
> Cette intégration communautaire et non officielle utilise le **protocole WebSocket local des poêles MCZ Maestro classiques**. Elle nécessite que Home Assistant puisse accéder au réseau Wi-Fi du poêle. Elle n'est **pas conçue pour Maestro+**, dont le fonctionnement réseau diffère. La compatibilité n'est pas garantie pour tous les modèles et firmwares.

## Présentation

MCZ Maestro Local est une **intégration personnalisée Home Assistant** qui communique directement avec le poêle via WebSocket (par défaut `ws://192.168.120.1:81`). Elle permet de commander le chauffage, de consulter les mesures et de configurer certains paramètres depuis l'interface Home Assistant.

**Aucun compte MCZ, service cloud, broker MQTT ou processus `maestrogateway` n'est nécessaire à l'exécution de cette intégration.** Le travail de rétro-ingénierie du projet [maestrogateway](https://github.com/Chibald/maestrogateway) a toutefois servi de référence pour le protocole.

### Fonctionnalités principales

- Thermostat Home Assistant avec **deux modes de régulation** : thermostat local avec hystérésis ou consigne de température native MCZ.
- Allumage et extinction du poêle depuis une entité `climate` ou un interrupteur dédié.
- Réglage de la puissance de chauffe **de 1 à 5**, selon les fonctions du poêle.
- Modes **Eco**, **Silent**, **Active**, sons des touches et mode été/hiver.
- Sélection du profil de fonctionnement MCZ.
- Pilotage du ventilateur principal et d'un ventilateur canalisé (si présents/compatibles), avec niveaux manuels et mode Auto.
- Mesures de température, état de fonctionnement, vitesse du ventilateur de fumées et informations d'entretien.
- Diagnostics de communication et réglages accessibles depuis Home Assistant.

## Compatibilité et prérequis

| Élément | Exigence ou information |
| --- | --- |
| Home Assistant | Intégration personnalisée via `custom_components` ; `hacs.json` annonce une version minimale de **2024.11.0**. |
| Poêle | MCZ équipé du **Maestro classique**, avec point d'accès Wi-Fi et serveur WebSocket local compatible. |
| Modèle de référence | Configuration prévue initialement pour **MCZ EGO Air Maestro** ; autres modèles à vérifier. |
| Réseau | Accès IP **depuis Home Assistant** au poêle, généralement `192.168.120.1` sur le port TCP `81`. |
| HACS | Facultatif : facilite l'installation et les mises à jour. |
| Cloud / MQTT | **Non requis**. |

**Maestro et Maestro+ ne sont pas interchangeables.** La présence de « Maestro » dans le nom commercial ne suffit pas à confirmer la compatibilité. Vérifiez que le poêle expose bien le réseau Wi-Fi et le service WebSocket attendus.

### Accès au réseau Wi-Fi du poêle

Les poêles Maestro concernés diffusent leur **propre réseau Wi-Fi**. L'adresse `192.168.120.1` est généralement accessible depuis ce réseau, **pas directement depuis votre réseau domestique**.

Deux approches sont possibles :

1. **Home Assistant possède un accès direct** au Wi-Fi du poêle et conserve, si nécessaire, une autre connexion au réseau domestique.
2. **Une passerelle à deux interfaces** (par exemple un Raspberry Pi relié en Ethernet au réseau local et en Wi-Fi au poêle) fournit un chemin réseau vers le poêle.

```text
  Réseau domestique                 Réseau Wi-Fi MCZ

  Home Assistant ── LAN ── Passerelle ── Wi-Fi ── Poêle MCZ
                                                  │
                                           192.168.120.1:81
```

> [!WARNING]
> Relier une machine à ces deux réseaux ne suffit pas toujours : **le routage, les routes IP et, selon l'architecture, le NAT doivent être configurés séparément**. Cette intégration ne configure pas la passerelle réseau. Évitez tout conflit entre le sous-réseau du poêle (habituellement `192.168.120.0/24`) et votre réseau local.

Le test important consiste à vérifier que **l'environnement qui exécute Home Assistant**, et non uniquement un téléphone ou un PC, peut joindre l'adresse et le port WebSocket du poêle.

## Installation

### Méthode recommandée : HACS

1. Ouvrez **HACS** dans Home Assistant.
2. Dans le menu `⋮`, choisissez **Dépôts personnalisés** (*Custom repositories*).
3. Renseignez l'adresse du dépôt :

   ```text
   https://github.com/NadeoGolf/MCZ-Maestro-Local
   ```

4. Choisissez le type **Intégration**, puis ajoutez le dépôt.
5. Recherchez **MCZ Maestro Local** dans HACS et téléchargez l'intégration.
6. **Redémarrez Home Assistant**.
7. Allez dans **Paramètres → Appareils et services → Ajouter une intégration**, puis recherchez **MCZ Maestro Local**.

Vous pouvez également utiliser le bouton HACS présent en haut de ce README.

### Installation manuelle

1. Téléchargez le contenu de ce dépôt GitHub.
2. Copiez **tout le dossier** `custom_components/mcz_maestro` dans le répertoire de configuration Home Assistant :

   ```text
   <config_home_assistant>/custom_components/mcz_maestro/
   ```

3. Vérifiez que `manifest.json` et `__init__.py` se trouvent directement dans ce dossier (sans dossier intermédiaire supplémentaire).
4. Redémarrez Home Assistant.
5. Ajoutez l'intégration dans **Paramètres → Appareils et services**.

Pour mettre à jour une installation manuelle, remplacez les fichiers de ce dossier, puis redémarrez Home Assistant. Effectuez une sauvegarde avant toute mise à jour.

## Première configuration

L'assistant d'ajout demande **uniquement** les informations de connexion :

| Paramètre | Valeur par défaut | Description |
| --- | --- | --- |
| Adresse IP (`host`) | `192.168.120.1` | Adresse du poêle vue par Home Assistant. |
| Port WebSocket (`port`) | `81` | Port TCP du serveur WebSocket MCZ. |

L'intégration tente une connexion au poêle lors de l'ajout. Une fois ajoutée, ouvrez **Paramètres → Appareils et services → MCZ Maestro Local → Configurer** pour accéder aux options générales.

| Option | Valeur par défaut | Description |
| --- | --- | --- |
| Nom affiché | `MCZ EGO Air` | Nom de l'appareil dans Home Assistant. |
| Modèle | `EGO Air Maestro` | Modèle affiché dans la fiche appareil. |
| Type de poêle | `Air` | Choix `Air` ou `Hydro` (information de configuration ; ne crée pas automatiquement d'entités Hydro spécifiques). |
| Mode de contrôle | `home_assistant_thermostat` | Régulation locale Home Assistant ou consigne native MCZ. |
| Intervalle de lecture | **15 secondes** | Lecture périodique des données ; plage configurable de **5 à 300 secondes**. |

## Entités disponibles

Les noms et identifiants complets des entités dépendent du nom de votre appareil et du registre d'entités Home Assistant.

| Plateforme | Entités / fonctionnalités |
| --- | --- |
| `climate` | Thermostat chauffage / arrêt, réglage de consigne, preset **Absence**. |
| `switch` | **Alimentation**, **Mode Eco**, **Mode Silent**, **Mode Active**, **Sons touches**, **Mode hiver/été**. |
| `select` | **Puissance** (1 à 5), **Profil** MCZ. |
| `fan` | **Ventilateur poêle**, **Ventilateur couloir** (premier ventilateur canalisé) ; niveaux 0 à 5 et **Auto** (valeur MCZ 6). |
| `number` | Réglages du thermostat : tolérances froide et chaude, température d'absence, durée minimale de cycle ; **Consigne native MCZ** (désactivée par défaut). |
| `sensor` | État du poêle, température ambiante, consigne native, température des fumées, vitesse du ventilateur des fumées et diagnostics complémentaires. |

### Capteurs complémentaires

Plusieurs capteurs sont **désactivés par défaut** pour ne pas encombrer Home Assistant. Vous pouvez les activer dans **Appareil → Entités** :

- Heures totales de fonctionnement et heures restantes avant entretien.
- Nombre d'allumages et minutes avant extinction.
- Température de la carte mère et température Active.
- Vitesse de la vis sans fin (mesure et consigne), pompe PWM.
- Version du firmware, identifiant de base de données, état du brasier et informations Active.

La disponibilité de ces informations dépend des données réellement transmises par le firmware du poêle. **Les entités qui ne correspondent pas à votre équipement peuvent rester inconnues ou indisponibles.**

## Thermostat : choisir le mode de contrôle

### 1. Thermostat Home Assistant (`home_assistant_thermostat`)

Dans ce mode, Home Assistant lit la **température ambiante remontée par le poêle** et décide d'envoyer des commandes d'allumage ou d'extinction en fonction de la consigne et de deux tolérances (hystérésis).

**Exemple :**

- Consigne : **20 °C**.
- Tolérance froide : **1,5 °C** → commande d'allumage à **18,5 °C ou moins**.
- Tolérance chaude : **0,5 °C** → commande d'extinction à **20,5 °C ou plus**.

La régulation automatique n'agit que lorsque l'entité `climate` est en mode **Chauffage (`heat`)**. Le mode **Arrêt (`off`)** commande l'extinction ; un allumage via l'interrupteur `Alimentation` ne met pas automatiquement le thermostat en mode Chauffage.

Pour limiter les commandes répétées, une **durée minimale entre deux commandes automatiques** est appliquée (10 minutes par défaut). Les actions manuelles d'allumage et d'extinction depuis le thermostat contournent cette temporisation.

Depuis la **version 0.21.1**, les commandes d'extinction sont ignorées lorsque l'état physique connu du poêle indique **Éteint (`0`)**, **Extinction (`40`)** ou **Refroidissement (`41`)**. Cela évite d'envoyer un nouvel ordre `Power=OFF` susceptible de relancer la ventilation. Si l'état physique n'est pas disponible ou n'est pas reconnu, la commande reste transmise par précaution. Cette protection n'empêche pas le cycle normal de ventilation déclenché par une véritable extinction.

> [!NOTE]
> Le contrôle ON/OFF ne reproduit pas à lui seul les protections, temporisations mécaniques ou séquences internes du poêle. Le poêle reste responsable de son propre cycle d'allumage et d'extinction.

### 2. Consigne native MCZ (`mcz_native_setpoint`)

Dans ce mode, Home Assistant transmet la consigne de température au poêle avec la commande **`Temperature_Setpoint`**. C'est le **poêle** qui gère sa régulation interne.

- Plage de consigne du thermostat Home Assistant : **10 à 32 °C**, par pas de **0,5 °C**.
- Passer le thermostat en mode Chauffage envoie la consigne et une commande d'allumage.
- Passer en mode Arrêt envoie une commande d'extinction.
- Le preset **Absence** envoie la température d'absence configurée.

Les tolérances froide/chaude et la durée minimale de cycle **ne sont pas utilisées pour piloter l'ON/OFF automatique** dans ce mode.

### Réglages du thermostat depuis la fiche appareil

Dans **MCZ Maestro Local → Appareil → Entités de configuration**, les entités `number` exposent les paramètres suivants :

| Réglage | Valeur par défaut | Utilité |
| --- | --- | --- |
| Tolérance froide | `1,5 °C` | Seuil de déclenchement de l'allumage en mode thermostat local. |
| Tolérance chaude | `0,5 °C` | Seuil de déclenchement de l'extinction en mode thermostat local. |
| Température d'absence | `18 °C` | Consigne du preset **Absence / Away**. |
| Durée minimale de cycle | `600 s` | Intervalle minimal entre deux commandes **automatiques** ON/OFF. |

La consigne initiale du thermostat local est de **18 °C** ; Home Assistant tente de restaurer le dernier état enregistré après un redémarrage.

## Diagnostic et dépannage

| Symptôme | Vérifications conseillées |
| --- | --- |
| L'intégration n'apparaît pas | Vérifiez le dossier `custom_components/mcz_maestro`, la présence du `manifest.json`, puis redémarrez Home Assistant. |
| « Impossible de se connecter » | Vérifiez le Wi-Fi du poêle, l'adresse IP, le port `81` et surtout la **route réseau depuis Home Assistant**. |
| Les capteurs affichent `unknown` ou `unavailable` | Vérifiez la communication, le modèle/firmware et les champs réellement envoyés par le poêle. |
| Le thermostat ne lance pas le chauffage | Vérifiez le mode `heat`, la température ambiante reçue, la consigne, les tolérances et la durée minimale de cycle. |
| La puissance affichée n'est pas renseignée ou semble ancienne | La puissance configurée n'est **pas déduite des trames positionnelles** : sa lecture dépend notamment des retours JSON, des commandes envoyées et de la restauration d'état. |
| Une commande de ventilateur n'a pas d'effet | Tous les poêles n'ont pas de ventilateur canalisé ou ne prennent pas en charge tous les modes. |

Pour tester la connectivité TCP, depuis une machine ayant **le même accès réseau que Home Assistant** et disposant de `nc` :

```bash
nc -vz 192.168.120.1 81
```

Un port accessible ne prouve toutefois pas, à lui seul, la compatibilité du protocole WebSocket.

### Activer temporairement les journaux détaillés

Ajoutez dans `configuration.yaml` (en fusionnant avec votre éventuelle configuration `logger`) :

```yaml
logger:
  default: warning
  logs:
    custom_components.mcz_maestro: debug
```

Redémarrez Home Assistant, reproduisez le problème, puis consultez les journaux. **Désactivez ensuite le niveau `debug`** : il peut enregistrer les trames échangées avec le poêle.

Un export des **diagnostics de l'intégration** est aussi disponible dans Home Assistant. Il contient des informations de configuration, des données d'état, des statistiques de communication et potentiellement des trames brutes. L'adresse IP est masquée dans une partie des diagnostics, mais **vérifiez toujours le contenu avant de publier ou de transmettre un fichier de diagnostic**.

## Limitations connues

- Projet **non officiel** basé sur un protocole non publiquement documenté par MCZ ; compatibilité variable selon modèles, firmwares et options.
- **Maestro+ n'est pas pris en charge** par cette implémentation du protocole Maestro classique.
- Le type `Air`/`Hydro` est un réglage d'identification : les entités ne sont pas actuellement générées automatiquement en fonction des capacités matérielles.
- Le second ventilateur canalisé (`DuctedFan2`) est présent dans le protocole, mais **aucune entité `fan` dédiée n'est actuellement créée**.
- La valeur `Puissance` peut rester inconnue ou reposer sur une valeur restaurée : elle n'est pas calculée à partir de l'état de combustion.
- Le statut d'alimentation est interprété à partir des états MCZ : il peut notamment rester considéré comme actif pendant certaines phases d'extinction ou de refroidissement.
- La temporisation anti-cycles du thermostat est conservée **en mémoire** et repart après un rechargement/redémarrage de l'intégration.
- Les tests automatisés fournis portent sur le **protocole** et sur la prévention des commandes OFF redondantes ; ils ne remplacent pas une validation sur poêle réel et ne couvrent pas tous les scénarios Home Assistant.

## Sécurité et avertissement

> [!CAUTION]
> **Cette intégration commande un appareil de chauffage.** Son utilisation est sous votre responsabilité. Conservez toutes les protections et procédures de sécurité prévues par le fabricant. Vérifiez physiquement le comportement du poêle lors de la mise en service, des mises à jour et des modifications d'automatisations. Ne laissez pas une automatisation non validée piloter seule le poêle.

La communication utilise **`ws://` (non chiffré)** sur le réseau local. N'exposez **jamais le port WebSocket du poêle directement sur Internet**. Préférez un réseau local maîtrisé et, si nécessaire, une passerelle sécurisée.

Cette intégration n'est **ni développée ni approuvée par MCZ**.

## Développement et contribution

Le projet a été créé pour un besoin personnel, avec l'aide de **l'intelligence artificielle** pour la génération, l'adaptation et la correction du code, puis avec des essais dans l'environnement de son auteur. Il peut encore comporter des erreurs ou des hypothèses propres au modèle utilisé.

Les rapports de bogues, retours de compatibilité et *pull requests* sont les bienvenus. Consultez aussi [CONTRIBUTING.md](CONTRIBUTING.md) et [SECURITY.md](SECURITY.md) :

- [Ouvrir un problème sur GitHub](https://github.com/NadeoGolf/MCZ-Maestro-Local/issues).
- Préciser le **modèle exact**, la **version du firmware**, le **mode de contrôle** et les étapes permettant de reproduire le problème.
- Joindre, si nécessaire, des journaux ou diagnostics **après vérification et suppression des données sensibles**.

Pour exécuter les tests unitaires du protocole depuis la racine du dépôt, avec Python et `pytest` installés :

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q tests/
```

## Remerciements

- [Chibald/maestrogateway](https://github.com/Chibald/maestrogateway), pour le travail de compréhension et de documentation du protocole MCZ Maestro.
- La [communauté Home Assistant](https://www.home-assistant.io/) pour sa documentation et ses outils d'intégration.

## Licence et publication

Le code de ce dépôt est distribué sous la **GNU General Public License v3.0** ([LICENSE](LICENSE)). La documentation du protocole utilisée comme référence provient notamment de [Chibald/maestrogateway](https://github.com/Chibald/maestrogateway), également sous GPL-3.0. Consultez [NOTICE.md](NOTICE.md) pour les attributions et les réserves concernant les marques et logos tiers.

Pour publier une mise à jour sur GitHub et préparer une release compatible HACS, suivez le [guide de publication](docs/PUBLICATION_GITHUB.md). Les tests GitHub Actions vérifient le dépôt, mais ils ne remplacent pas un essai sur un poêle réel.
