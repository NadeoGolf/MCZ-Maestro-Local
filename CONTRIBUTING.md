# Contribuer à MCZ Maestro Local

Les retours d'expérience, corrections et tests sur d'autres modèles sont les
bienvenus. Le pilotage d'un poêle à granulés présente des risques : une
modification de l'allumage, de l'extinction ou de la régulation doit être
revue attentivement et testée dans des conditions contrôlées.

## Signaler un problème

Utilisez [GitHub Issues](https://github.com/NadeoGolf/MCZ-Maestro-Local/issues)
et fournissez : modèle et firmware, version de Home Assistant, version de
l'intégration, mode de contrôle du thermostat, étapes de reproduction et résultat
attendu. Pour les problèmes d'extinction, précisez l'attribut `raw_stove_state`
si disponible, ainsi que l'action Home Assistant utilisée.

**N'envoyez pas publiquement** d'adresse IP publique, de secret réseau ou de
journal contenant des informations personnelles. Vérifiez/redactez les exports
de diagnostics avant toute publication.

## Proposer une modification

1. Créez une branche à partir de `main`.
2. Gardez les changements ciblés, avec un test de non-régression lorsque cela
   est possible.
3. Exécutez les tests unitaires localement :

   ```bash
   python -m pip install -r requirements-dev.txt
   python -m pytest -q tests
   python -m compileall -q custom_components/mcz_maestro
   ```

4. Ouvrez une pull request et décrivez les risques de changement de comportement
   pour l'appareil physique et les résultats des tests.

Les contrôles GitHub Actions lancent également HACS et hassfest. Les tests
unitaires n'exigent pas de poêle physique et ne remplacent pas un essai en
conditions réelles.

## Licence

Les contributions soumises pour intégration au projet doivent pouvoir être
distribuées sous la licence GNU GPL version 3 du dépôt. Référez-vous à
[LICENSE](LICENSE) et [NOTICE.md](NOTICE.md) pour les attributions.
