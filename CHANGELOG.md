# Changelog

Tous les changements notables pour ce projet seront documentés dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/),
et ce projet adhère à [Semantic Versioning](https://semver.org/).

---

## [Version 3.0.2] - 2026-07-25
### Ajouté (Added)
- Test unitaire pour valider que `aperture=0` n'envoie pas de valeur d'ouverture au boitier.
- Test unitaire pour valider le parsing des vitesses au format fractionnaire (ex: `1/500`).
- Conservation de la valeur littérale `ShutterSpeed` issue du script (ex: `1/4`, `0.3`, `1/500`) dans la configuration d'action.

### Modifié (Changed)
- Mise à jour de `MANUEL_D'UTILISATION.md` pour documenter la règle `aperture=0` (ouverture non envoyée au boitier) et les formats `ShutterSpeed` acceptés (`0.002` et `1/500`).
- Mise à jour de `README.md` pour rappeler la règle `aperture=0`.
- Validation système des vitesses d'obturation basée sur la valeur littérale du script, sans normalisation flottante (ex: `1/4` reste `1/4`, `0.3` reste `0.3`).

### Corrigé (Fixed)
- Dans `ActionScheduler`, si `aperture=0` dans le script de séquence, le paramètre ouverture n'est plus envoyé à l'appareil photo.
- Dans `ConfigParser`, correction du parsing des vitesses d'obturation au format fractionnaire (`1/500`) en plus du format décimal en secondes.
- Correction du plantage à l'initialisation sur les lignes `Photo` contenant `ShutterSpeed=1/500`.
- Suppression des faux warnings `Unusual shutter speed` causés par la conversion flottante (ex: `1` devenu `1.0`).
- Ajout de méthodes de compatibilité legacy dans `MultiCameraManager` (`connect_all_cameras`, `capture_synchronized`).

## [Version 3.0.1] - 2026-06-06
### Ajouté (Added)
- Monitoring périodique de santé caméra (`CAMERA_HEALTH`) avec batterie, dernier fichier photo et horodatage de la dernière photo.
- Nouveau module `scheduling/camera_health_monitor.py`.

### Modifié (Changed)
- Intégration du monitoring santé caméra dans `ActionScheduler` pendant les périodes d'attente et entre actions.
- Ajout de `ActionJournal.log_camera_health()` pour journalisation JSON Lines structurée.
- Mise à jour de `README.md` pour documenter le monitoring santé caméra.

## [Version 3.0.0] - 2026-06-16
### Ajouté (Added)
- Versioning de l'application.
- Entête du fichier `CHANGELOG.md`.
- Rotation du fichier journal.
- Rotation du fichier log.

### Modifié (Changed)
- Formatage du fichier changelog.
- Codage de l'ouverture et fermeture du filtre dans le script: `C` = close/fermer, `O` = open/ouvrir, afin de simplifier la lecture.

### Corrigé (Fixed)
- Correction du manuel d'utilisation sur la commande `Filter`.

### Supprimé (Removed)
- Aucun.

## 2026-05-02
- Ajout d'une ligne avec les circonstances de l'éclipse dans le journal pour être utilisée par le monitor.
- Correction de `action_journal` pour calculer et afficher `scheduled_at`.

## 2026-05-01
- Gestion de l'interruption via le Ctrl-C
- Création d'une journalisation des actions et adaptation des différents scripts.
- Tests de fonctionnement avec correctifs de typos

## 2026-04-19
- Corrections suite à un test de réinstallation complète
- Ajout du chargement de la librairie `Filter.controler`.
- Mise à jour du Readme

## 2026-04-11
- Passage en package pip pour `filter_controler`.
- Adaptation du requirements.txt
- Correction du `__init__.py` de `hardware`.
- Modification de `action_scheduler.py` pour charger les classes de `filter_controller.py`.
- Tests de fonctionnement
- Renommage du changelog et passage en `.md`.
- Nettoyage de l'arborescence

## 2026-04-05
- Création du manuel d'utilisation.
- Amélioration de la gestion du nombre de champs dans le script d'orchestration pour chaque commande.
- Adaptation de `config_parser.py`.

## 2026-04-02
- Création du fichier `ARCHITECTURE.md`.
- Correction du fichier `DOCUMENTATION_PYTHON.md`.

## 2026-04-01
- Nettoyage de la racine pour supprimer les fichiers de test Lua.
- Mise à jour de `install.sh` pour ajouter la règle udev pour le flatpanel.
- Tests avec le script `config_photo_filter.txt`.

## 2026-03-31
- Ajout de `filter_controller.py` dans `hardware`.
- Mise à jour de `requirements.txt` pour charger `pyserial`.
- Modification des différents modules pour gérer le filtre.

## 2026-03-15
- Création d'un script bash de lancement: `SEP_launch.sh`.
- Gestion de la vitesse compatible avec la notation du boitier: en secondes de 30s à 0.3s et en fraction de 1/4s à 1/4000s.
- Suppression du `test_mode` dans le script, remplacé par `--test-mode` à l'appel du programme `main`.

## 2026-03-10
- Création des scripts de tests.
- Test des modes Photo unique, Boucle et Interval.

## 2026-03-09
- Correction de la vérification de `ShutterSpeed` (seconde > 1/4 >= fraction).
- Correction des constantes pour `ShutterSpeed` et `ISO`.
- Ajout de conseils de vérification dans le script `config_eclipse.txt`.

## 2026-03-08
- Application du setting `capturetarget` pour stocker les images sur la MemoryCard.
- Utilisation des constantes définies dans `utils/constants.py`.
- Création du répertoire `scripts_eclipse` pour ranger les scripts.
- Création d'un générateur de script à améliorer.

## 2026-03-07
- Ajout d'une ligne de séparation à l'init du log.
- Correction du bug sur le setting `aperture` (retrait du `f/`).

## 2026-04-01
- Récupération du code source suite à la migration en Python par l'IA.
- Réorganisation de l'arborescence.