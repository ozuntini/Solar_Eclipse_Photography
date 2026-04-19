# Changelog 19/04/2026
- Corrections suite à un test de réinstallation complète
- Ajout du chargement de la librairie Filter.controler
- Mise à jour du Readme

## Changelog 11/04/2026
- Passage en package pip pour filter_controler
- Adaptation du requirements.txt
- Correction du __init__.py de hardware
- Modification du action_scheduler.py pour charger les class de filter_controller.py
- Tests de fonctionnement
- Renomage de Changelog et passage en md
- Nettoyage de l'arborescence

## Changelog 05/04/2026
Création du Manuel d'utilistaion
Amélioration de la gestion du nombre de champs dans le script d'orchestration pour chaque commande
Adaptation du config_parser.py

## Changelog 02/04/2026
Création du fichier ARCHITECTURE.md
Correction du fichier DOCUMENTATION_PYTHON.md

## Changelog 01/04/2026
Nettoyage de la racine pour supprimer les fichiers de test lua
Mise à jour du install.sh pour ajouter la règle udev pour le flatpanel
Tests avec le script config_photo_filter.txt

## Changelog 31/03/2026
Ajout du filter_controller.py dans hardware
Mise à jour du requirements.txt pour charger pyserial
Modification des différents modules pour gérer le filtre

## Changelog 15/03/2026
Création d'un script bash de lancement, SEP_launch.sh 
Gestion de la vitesse compatible avec la notation du boitier. en s de 30s à 0.3s et en 1/s de 1/4s à 1/4000s
Suppression du test_mode dans le script. Il est remplacé par le --test-mode à l'appel du programme main.

## Changelog 10/03/2026
Création des scripts de tests
Test des modes Photo unique, Boucle et Interval

## Changelog 09/03/2026
Correction de la vérification de Shutterspeed. Seconde > 1/4 >= Fraction
Correction des constantes pour Shutterspeed et ISO
Ajout de conseils de vérifications dans le script config_eclipse.txt

## Changelog 08/03/2026
Application du setting capturetarget pour stocker les images sur la MemoryCard
Utilisation des constantes définie dans utils/constants.py
Création du répertoire scripts_eclipse pour ranger les scripts
Création d'un générateur de script a améliorer

## Changelog 07/03/2026
Ajout d'un ligne de séparation à l'init du log
Correction du bug sur le settings aperture retirer le f/

## Changelog 01/03/2026
Récupération du code source suite à la migration en Python par l'IA
Réorganisation de l'arborescence