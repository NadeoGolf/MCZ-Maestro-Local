# MCZ Maestro Local pour Home Assistant

Intégration locale Home Assistant pour piloter un poêle MCZ Maestro via WebSocket, basée sur le protocole utilisé par `maestrogateway`.

## Fonctions principales

- Connexion locale WebSocket au poêle, par défaut `ws://192.168.120.1:81`.
- Thermostat Home Assistant avec deux modes de contrôle :
  - `home_assistant_thermostat` : Home Assistant régule ON/OFF avec hystérésis.
  - `mcz_native_setpoint` : la consigne de température est envoyée au poêle avec `Temperature_Setpoint`.
- Commande ON/OFF explicite :
  - `switch.alimentation`
- Puissance sous forme de liste déroulante `select` de 1 à 5.
- Commandes MCZ sûres ajoutées : Eco, Silent, Active, sons touches, profil, consigne native.
- Capteurs de diagnostic : firmware, database ID, heures de fonctionnement, heures avant entretien, nombre d'allumages, température carte mère, RPM vis sans fin, etc. Plusieurs sont désactivés par défaut pour garder l'interface lisible.
- Diagnostics Home Assistant téléchargeables depuis l'intégration.
- Options de configuration : nom affiché, modèle, type Air/Hydro, mode de contrôle, intervalle de polling.

## Ce qui n'est pas ajouté volontairement

- Pas de `select` supplémentaire pour les ventilateurs.
- Pas d'entité ni de commande `Pellet_Sensor`, car le poêle cible n'en possède pas.
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

Redémarre Home Assistant, puis ajoute l'intégration depuis :

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

Il faut publier ce contenu dans un dépôt GitHub, puis l'ajouter comme dépôt personnalisé HACS de type `Integration`.

## Automations utiles

Régler la puissance :

```yaml
service: select.select_option
target:
  entity_id: select.mcz_ego_air_puissance
data:
  option: "3"
```

Allumer le poêle avec le switch :

```yaml
service: switch.turn_on
target:
  entity_id: switch.mcz_ego_air_alimentation
```


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

## Développement

Les tests de protocole sont dans :

```text
tests/test_protocol.py
```

Ils couvrent les commandes principales, le parsing `C|RecuperoInfo`, les deltas JSON, la conversion des températures et les temps de fonctionnement.


## Configuration thermostat depuis l'appareil

Les réglages du thermostat local Home Assistant sont exposés comme entités `number` dans la catégorie `Configuration` de l'appareil Home Assistant :

- `Tolérance froide thermostat` : allumage si la température ambiante est inférieure ou égale à la consigne moins cette valeur.
- `Tolérance chaude thermostat` : extinction si la température ambiante est supérieure ou égale à la consigne plus cette valeur.
- `Température absence thermostat` : température utilisée par le preset Away / absence.
- `Durée minimale cycle thermostat` : délai minimal entre deux commandes automatiques ON/OFF.

Exemple avec une consigne à 20 °C, une tolérance froide à 1,5 °C et une tolérance chaude à 0,5 °C : le poêle démarre à 18,5 °C ou moins et s'arrête à 20,5 °C ou plus.

Ces paramètres concernent principalement le mode `Thermostat Home Assistant local`. L'écran `Configurer` de l'intégration ne conserve que les réglages globaux comme le nom, le modèle, le type, le mode de contrôle et l'intervalle de lecture.
