# Changelog

Tous les changements notables pour ce projet seront documentés dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/),
et ce projet adhère à [Semantic Versioning](https://semver.org/).

---

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
- Versioning de l'application
- Entête du fichier Changelog.md
- Rotation du fichier journal.
- Rotation du fichier log.

### Modifié (Changed)
- Formatage du fichier Changelog
- Codage de l'ouverture et fermeture du filtre dans le script. Maintenant C = Close/Fermer - O = Open/ouvrir. Afin de simplifier la lecture

### Corrigé (Fixed)
- 

### Supprimé (Removed)
- 

## 2026-05-02
- Ajout d'une ligne avec les circonstances de l'éclipse dans le journal pour être utilisée par le monitor.
- Correction du action_journal pour calculer et afficher le scheduled_at.

## 2026-05-01
- Gestion de l'interruption via le Ctrl-C
- Création d'une journalisation des actions et adaptation des différents scripts.
- Tests de fonctionnement avec correctifs de typos

## 2026-04-19
- Corrections suite à un test de réinstallation complète
- Ajout du chargement de la librairie Filter.controler
- Mise à jour du Readme

## 2026-04-11
- Passage en package pip pour filter_controler
- Adaptation du requirements.txt
- Correction du __init__.py de hardware
- Modification du action_scheduler.py pour charger les class de filter_controller.py
- Tests de fonctionnement
- Renomage de Changelog et passage en md
- Nettoyage de l'arborescence

## 2026-04-05
Création du Manuel d'utilistaion
Amélioration de la gestion du nombre de champs dans le script d'orchestration pour chaque commande
Adaptation du config_parser.py

## 2026-04-02
Création du fichier ARCHITECTURE.md
Correction du fichier DOCUMENTATION_PYTHON.md

## 2026-04-01
Nettoyage de la racine pour supprimer les fichiers de test lua
Mise à jour du install.sh pour ajouter la règle udev pour le flatpanel
Tests avec le script config_photo_filter.txt

## 2026-03-31
Ajout du filter_controller.py dans hardware
Mise à jour du requirements.txt pour charger pyserial
Modification des différents modules pour gérer le filtre

## 2026-03-15
Création d'un script bash de lancement, SEP_launch.sh 
Gestion de la vitesse compatible avec la notation du boitier. en s de 30s à 0.3s et en 1/s de 1/4s à 1/4000s
Suppression du test_mode dans le script. Il est remplacé par le --test-mode à l'appel du programme main.

## 2026-03-10
Création des scripts de tests
Test des modes Photo unique, Boucle et Interval

## 2026-03-09
Correction de la vérification de Shutterspeed. Seconde > 1/4 >= Fraction
Correction des constantes pour Shutterspeed et ISO
Ajout de conseils de vérifications dans le script config_eclipse.txt

## 2026-03-08
Application du setting capturetarget pour stocker les images sur la MemoryCard
Utilisation des constantes définie dans utils/constants.py
Création du répertoire scripts_eclipse pour ranger les scripts
Création d'un générateur de script a améliorer

## 2026-03-07
Ajout d'un ligne de séparation à l'init du log
Correction du bug sur le settings aperture retirer le f/

## 2026-04-01
Récupération du code source suite à la migration en Python par l'IA
Réorganisation de l'arborescence