# MCZ Maestro Local pour Home Assistant

Intégration locale Home Assistant pour piloter un poêle MCZ Maestro via WebSocket, basée sur le protocole utilisé par `maestrogateway`.

## À propos du projet

Ce projet a été réalisé avec l’aide de l’intelligence artificielle.

Je ne suis pas développeur de métier. Cette intégration a été construite progressivement pour répondre à un besoin personnel : piloter localement un poêle MCZ Maestro depuis Home Assistant, sans dépendre du cloud MCZ.

Le code, la structure Home Assistant, les entités et les corrections ont été générés, adaptés et améliorés avec l’aide de l’IA, puis testés dans mon environnement.

Le projet peut donc contenir des imperfections, des choix techniques discutables ou des limitations. Les retours, corrections et contributions sont les bienvenus.

## Remerciements

Merci aux projets et travaux existants ayant servi de base à la compréhension du protocole MCZ, notamment :

- `maestrogateway`, qui a servi de référence pour comprendre les commandes et le protocole WebSocket MCZ.
- Les contributeurs ayant documenté ou expérimenté le protocole MCZ Maestro.
- La communauté Home Assistant pour la documentation, les exemples d’intégrations personnalisées et les bonnes pratiques.

Sans ces bases existantes, cette intégration n’aurait probablement pas pu être réalisée.

## Fonctions principales

- Connexion locale WebSocket au poêle, par défaut `ws://192.168.120.1:81`.
- Thermostat Home Assistant avec deux modes de contrôle :
  - `home_assistant_thermostat` : Home Assistant régule ON/OFF avec hystérésis.
  - `mcz_native_setpoint` : la consigne de température est envoyée au poêle avec `Temperature_Setpoint`.
- Commande ON/OFF explicite :
  - `switch.alimentation`
- Puissance sous forme de liste déroulante `select` de 1 à 5.
- Commandes MCZ sûres ajoutées : Eco, Silent, Active, sons touches, profil, consigne native.
- Capteurs de diagnostic : firmware, database ID, heures de fonctionnement, heures avant entretien, nombre d’allumages, température carte mère, RPM vis sans fin, etc.
- Plusieurs capteurs de diagnostic sont désactivés par défaut pour garder l’interface Home Assistant lisible.
- Diagnostics Home Assistant téléchargeables depuis l’intégration.
- Options de configuration : nom affiché, modèle, type Air/Hydro, mode de contrôle, intervalle de polling.

## Ce qui n’est pas ajouté volontairement

- Pas de `select` supplémentaire pour les ventilateurs.
- Pas d’entité ni de commande `Pellet_Sensor`, car le poêle cible n’en possède pas.
- Pas de commandes sensibles de maintenance comme `Reset_Alarm`, `Reset_Active`, `Diagnostics`, `Feeding_Screw` ou factory reset.

## Installation manuelle

Ce dépôt est structuré pour HACS et pour une installation manuelle.

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

La structure attendue par HACS est présente :

```text
custom_components/mcz_maestro
hacs.json
README.md
```

Il faut publier ce contenu dans un dépôt GitHub, puis l’ajouter comme dépôt personnalisé HACS de type :

```text
Integration
```

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

## Entités principales

### Thermostat

```text
climate.mcz_ego_air
```

Deux modes sont disponibles :

```text
home_assistant_thermostat
mcz_native_setpoint
```

### Alimentation

```text
switch.mcz_ego_air_alimentation
```

Permet d’allumer ou d’éteindre le poêle.

Commandes MCZ utilisées :

```text
Allumage  : C|WriteParametri|34|1
Extinction: C|WriteParametri|34|40
```

### Puissance

```text
select.mcz_ego_air_puissance
```

Options disponibles :

```text
1
2
3
4
5
```

Commande MCZ utilisée :

```text
C|WriteParametri|36|<puissance>
```

### Mode été

```text
switch.mcz_ego_air_mode_ete
```

Permet de basculer le poêle en mode été / hiver.

### Autres commandes MCZ exposées

Selon les capacités du poêle, l’intégration peut exposer :

```text
switch.mcz_ego_air_mode_eco
switch.mcz_ego_air_mode_silent
switch.mcz_ego_air_mode_active
switch.mcz_ego_air_sons_touches
select.mcz_ego_air_profil
```

## Automations utiles

### Régler la puissance

```yaml
service: select.select_option
target:
  entity_id: select.mcz_ego_air_puissance
data:
  option: "3"
```

### Allumer le poêle avec le switch

```yaml
service: switch.turn_on
target:
  entity_id: switch.mcz_ego_air_alimentation
```

### Éteindre le poêle avec le switch

```yaml
service: switch.turn_off
target:
  entity_id: switch.mcz_ego_air_alimentation
```

### Régler la température en mode consigne native MCZ

Activer le mode de consigne native MCZ dans les options, puis régler la température du `climate` :

```yaml
service: climate.set_temperature
target:
  entity_id: climate.mcz_ego_air
data:
  temperature: 20.5
```

Dans ce mode, Home Assistant envoie :

```text
C|WriteParametri|42|41
```

Ce qui correspond à une consigne de 20,5 °C.

## Attention aux automatisations au retour Wi-Fi

Les poêles MCZ Maestro peuvent perdre temporairement leur connexion Wi-Fi.

Lors du retour réseau, Home Assistant relit l’état du poêle avec :

```text
C|RecuperoInfo
```

Si une automation est déclenchée sur un changement d’état trop large, elle peut se lancer au retour de disponibilité du poêle.

Il faut éviter les déclencheurs qui réagissent à tous les changements d’état, par exemple :

```yaml
trigger:
  - platform: state
    entity_id: switch.mcz_ego_air_mode_ete
```

car ils peuvent se déclencher lors de transitions comme :

```text
unavailable → on
unavailable → off
unknown → on
unknown → off
```

Il est préférable de cibler uniquement les vrais changements fonctionnels :

```yaml
triggers:
  - trigger: state
    entity_id: switch.mcz_ego_air_mode_ete
    from: "off"
    to: "on"
    id: mode_ete

  - trigger: state
    entity_id: switch.mcz_ego_air_mode_ete
    from: "on"
    to: "off"
    id: mode_hiver
```

## Exemple d’automation mode été / hiver

```yaml
alias: Mode été / hiver chauffage
description: >-
  Active ou désactive le chauffage et les automatisations associées selon le
  mode MCZ

triggers:
  - trigger: state
    entity_id: switch.mcz_ego_air_mode_ete
    from: "off"
    to: "on"
    id: mode_ete

  - trigger: state
    entity_id: switch.mcz_ego_air_mode_ete
    from: "on"
    to: "off"
    id: mode_hiver

actions:
  - choose:
      - conditions:
          - condition: trigger
            id: mode_ete
        sequence:
          - target:
              entity_id: switch.schedule_planification_temperature_poele
            action: switch.turn_off
            data: {}

          - target:
              entity_id:
                - climate.mcz_ego_air
                - climate.radiateur_axel
                - climate.radiateur_chambre
                - climate.seche_serviette
                - climate.radiateur_bureau
            action: climate.turn_off
            data: {}

          - target:
              entity_id:
                - automation.presence_poele
                - automation.erreur_poele
                - automation.gestion_poele_nuit
                - automation.gestion_ouverture_fenetres_radiateurs
            action: automation.turn_off
            data:
              stop_actions: true

      - conditions:
          - condition: trigger
            id: mode_hiver
        sequence:
          - target:
              entity_id: switch.schedule_planification_temperature_poele
            action: switch.turn_on
            data: {}

          - target:
              entity_id:
                - climate.mcz_ego_air
                - climate.radiateur_axel
                - climate.radiateur_chambre
                - climate.seche_serviette
                - climate.radiateur_bureau
            action: climate.turn_on
            data: {}

          - target:
              entity_id:
                - automation.presence_poele
                - automation.erreur_poele
                - automation.gestion_poele_nuit
                - automation.gestion_ouverture_fenetres_radiateurs
            action: automation.turn_on
            data: {}

    default: []

mode: single
```

## Débogage

Pour activer les logs détaillés de l’intégration, ajouter temporairement dans `configuration.yaml` :

```yaml
logger:
  default: info
  logs:
    custom_components.mcz_maestro: debug
```

Puis redémarrer Home Assistant.

Les lignes importantes à surveiller sont :

```text
MCZ status request: C|RecuperoInfo
MCZ recv: ...
MCZ send: C|WriteParametri|...
```

Différence importante :

```text
C|RecuperoInfo
```

est une lecture d’état normale.

```text
C|WriteParametri|...
```

est une vraie commande envoyée au poêle.

Exemples :

```text
C|WriteParametri|34|1   → allumage
C|WriteParametri|34|40  → extinction
C|WriteParametri|36|3   → puissance 3
C|WriteParametri|42|41  → consigne native 20,5 °C
```

## Diagnostics Home Assistant

L’intégration expose un diagnostic téléchargeable depuis Home Assistant.

Il permet d’aider au dépannage en regroupant certaines informations utiles sur l’état connu du poêle, la configuration et les dernières données remontées.

## Développement

Les tests de protocole sont dans :

```text
tests/test_protocol.py
```

Ils couvrent notamment :

- les commandes principales
- le parsing `C|RecuperoInfo`
- les deltas JSON
- la conversion des températures
- les temps de fonctionnement

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
- Les pertes Wi-Fi du poêle peuvent provoquer des états temporairement indisponibles.
- Les automatisations Home Assistant doivent être écrites avec prudence pour éviter des actions au retour de disponibilité.

## Commandes sensibles non exposées

Certaines commandes MCZ ne sont volontairement pas exposées par défaut, car elles peuvent être sensibles ou liées à la maintenance :

```text
Reset_Alarm
Reset_Active
Diagnostics
Feeding_Screw
Factory_Reset
```

## Contributions

Les contributions sont bienvenues, notamment pour :

- améliorer la compatibilité avec d’autres modèles MCZ
- documenter les trames selon les firmwares
- enrichir les capteurs
- améliorer les traductions
- fiabiliser la gestion des pertes Wi-Fi
- ajouter des tests unitaires de protocole
- corriger ou améliorer le code généré avec l’aide de l’IA

## Avertissement

Cette intégration pilote un appareil de chauffage réel.

Utilisation à vos risques et périls.

Vérifiez toujours le comportement du poêle après installation, mise à jour ou modification d’automatisations.

Ne laissez pas une automatisation non testée piloter l’allumage ou l’extinction du poêle sans surveillance initiale.
