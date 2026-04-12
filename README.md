# Eclipse Photography Controller - Python Migration

## Vue d'ensemble

Ce projet est une migration complète du script `eclipse_OZ.lua` de Magic Lantern vers Python avec support GPhoto2.  
Il permet le contrôle automatisé de plusieurs appareils photo Canon pour la photographie d'éclipses solaires.
<hr style="height:8px; border:none; background-color:red;">

> [!CAUTION]
> ## ⚠️ DANGER CRITIQUE : RISQUE DE CÉCITÉ ⚠️
> **CE SYSTÈME EST EXCLUSIVEMENT RÉSERVÉ À L'ASTROPHOTOGRAPHIE.**
> 
> * **INTERDICTION FORMELLE** d'utiliser ce dispositif pour l'observation visuelle (œil à l'oculaire).
> * Une défaillance logicielle, un bug du script ou une coupure de courant peut entraîner le retrait imprévu du filtre.
> * L'observation directe du soleil sans filtre à travers un instrument optique provoque une **perte de vue immédiate et définitive**.
> 
> **L'utilisateur assume l'entière responsabilité de l'utilisation de ce code.**

![Danger](https://img.shields.io/badge/DANGER-EYE_SAFETY-red?style=for-the-badge)
![Photo Only](https://img.shields.io/badge/Usage-Astrophotography_Only-blue?style=for-the-badge)

<hr style="height:8px; border:none; background-color:red;">

## Documentation

📚 **Documentation complète disponible** :

- **[DOCUMENTATION_PYTHON.md](DOCUMENTATION_PYTHON.md)** - Documentation technique complète de l'application Python
- **[GUIDE_FONCTIONNEMENT.md](GUIDE_FONCTIONNEMENT.md)** - Guide pratique d'utilisation quotidienne  
- **[VALIDATION_COHERENCE_LUA_PYTHON.md](VALIDATION_COHERENCE_LUA_PYTHON.md)** - Guide de validation et tests comparatifs Lua/Python
- **[MANUEL_D'UTILISATION.md](MANUEL_D'UTILISATION.md)** - Manuel d'aide à l'utilisation et à la constuction du fichier de script

## Fonctionnalités

### ✅ Migration complète des fonctionnalités Magic Lantern
- **Planification temporelle** : Support des temps absolus et relatifs (C1, C2, Max, C3, C4)
- **Types d'actions** : Photo unique, Boucles, Intervalles
- **Paramètres photographiques** : ISO, ouverture, vitesse, mirror lockup
- **Mode test** : Simulation complète sans déclenchement réel

### 🆕 Nouvelles fonctionnalités
- **Multi-caméras** : Contrôle simultané de plusieurs appareils
- **Gestion d'erreurs** : Isolation des pannes par appareil
- **Logging avancé** : Traçabilité complète des opérations
- **Validation système** : Vérifications automatiques pré-séquence

## Installation

### Prérequis système (Raspberry Pi)

```bash
# Mettre à jour le système
sudo apt update && sudo apt upgrade -y

# Installer les dépendances système
sudo apt install -y python3-pip python3-venv git
sudo apt install -y gphoto2 libgphoto2-dev libgphoto2-port12
sudo apt install -y build-essential pkg-config
```

### Installation automatique

```bash
# Rendre le script exécutable et lancer l'installation
chmod +x install.sh
./install.sh
```

### Installation manuelle

```bash
# Créer l'environnement virtuel
python3 -m venv ~/eclipse_env
source ~/eclipse_env/bin/activate

# Installer les dépendances Python
pip install -r requirements.txt

Attention à pip install git+https://github.com/ozuntini/Filter_Control.git

# Configurer les permissions USB pour Canon
echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="04a9", MODE="0666"' | sudo tee /etc/udev/rules.d/99-canon-cameras.rules
sudo udevadm control --reload-rules
```

## Configuration

### Format du fichier de configuration

Le format est compatible avec le fichier `SOLARECL.TXT` original :

```
# Configuration de l'éclipse
Config,C1,C2,Max,C3,C4,test_mode

# Actions photographiques
Photo,reference,operateur,temps,_,_,_,_,_,ouverture,iso,vitesse,mlu
Boucle,reference,op_debut,temps_debut,op_fin,temps_fin,intervalle,_,_,ouverture,iso,vitesse,mlu
Interval,reference,op_debut,temps_debut,op_fin,temps_fin,nombre,_,_,ouverture,iso,vitesse,mlu
```
C.F. **[MANUEL_D'UTILISATION.md](MANUEL_D'UTILISATION.md)** pour vous aider à la construction de ce script.

### Exemples de configuration

Voir le fichier `config_eclipse.txt` pour un exemple complet.

## Utilisation

### Commandes de base

```bash
# Activer l'environnement
source ~/eclipse_env/bin/activate

# Lancement standard
python3 main.py config_eclipse.txt

# Mode test (simulation)
python3 main.py config_eclipse.txt --test-mode

# Avec paramètres avancés
python3 main.py config_eclipse.txt --cameras 0 1 2 --log-level DEBUG
```

### Options disponibles

- `--test-mode` : Mode simulation sans déclenchement réel
- `--log-level DEBUG|INFO|WARNING|ERROR` : Niveau de logging
- `--log-file FICHIER` : Fichier de log personnalisé
- `--cameras ID [ID ...]` : Utiliser des caméras spécifiques
- `--strict-mode` : Arrêter à la première erreur

### Vérification du système

```bash
# Test de détection des caméras
gphoto2 --auto-detect

# Test de connexion Python
python3 -c "
from hardware.multi_camera_manager import MultiCameraManager
mgr = MultiCameraManager()
print(f'Caméras détectées: {mgr.discover_cameras()}')
mgr.disconnect_all()
"
```

## Architecture

### Structure du projet

```
python/
├── main.py                     # Point d'entrée principal
├── config/                     # Parsing et validation configuration
│   ├── __init__.py             # Exports publics
│   ├── eclipse_config.py       # Structures de données
│   └── config_parser.py        # Analyse de fichiers
├── hardware/                   # Contrôle matériel
│   ├── __init__.py             # Exports: CameraController, MultiCameraManager
│   ├── camera_controller.py    # Contrôle caméra individuelle
│   ├── multi_camera_manager.py # Orchestration multi-caméras
│   └── filter_controller.py    # Contrôle panneau Gemini AutoFlatPanel
├── scheduling/                 # Planification et exécution
│   ├── __init__.py             # Exports
│   ├── action_scheduler.py     # Exécution d'actions
│   ├── time_calculator.py      # Calculs temporels
│   └── action_types.py         # Définitions d'actions
├── utils/                      # Utilitaires
│   ├── __init__.py             # Exports publics
│   ├── constants.py            # Constantes globales
│   ├── logger.py               # Configuration logging
│   └── validation.py           # Validation système/caméras
└── tests/                      # Tests unitaires
```

### Flux d'exécution

1. **Initialisation** : Parse configuration, initialise logging
2. **Validation** : Vérifie système et caméras
3. **Découverte** : Détecte et connecte les caméras
4. **Planification** : Calcule les temps d'exécution
5. **Exécution** : Exécute la séquence d'actions
6. **Nettoyage** : Déconnecte les caméras proprement

## Tests

### Exécution des tests

```bash
# Tous les tests
python3 -m pytest tests/

# Tests spécifiques
python3 -m pytest tests/test_config_parser.py -v

# Tests avec couverture
python3 -m pytest tests/ --cov=. --cov-report=html
```

### Tests manuels

```bash
# Test du parser de configuration
python3 -c "
from config import parse_config_file
config = parse_config_file('config_eclipse.txt')
print(f'Actions: {len(config.actions)}')
"

# Test du calculateur de temps
python3 -c "
from config import parse_config_file
from scheduling import TimeCalculator
config = parse_config_file('config_eclipse.txt')
calc = TimeCalculator(config.eclipse_timings)
print(f'Séquence valide: {calc.validate_eclipse_sequence()}')
"
```

## Comparaison Magic Lantern vs Python

### Équivalences API

| Magic Lantern | Python/GPhoto2 | Description |
|---------------|----------------|-------------|
| `camera.iso.value = 1600` | `gp.gp_widget_set_value(iso_widget, "1600")` | Configuration ISO |
| `camera.aperture.value = 8` | `gp.gp_widget_set_value(aperture_widget, "f/8")` | Configuration ouverture |
| `camera.shoot(false)` | `gp.gp_camera_capture(camera, gp.GP_CAPTURE_IMAGE)` | Déclenchement |
| `dryos.date` | `datetime.datetime.now()` | Heure système |
| `key.wait()` | `input()` ou handlers GPIO | Attente interaction |

### Fonctionnalités conservées

- ✅ Parsing identique du fichier SOLARECL.TXT
- ✅ Calculs temporels exacts (convert_time, convert_second, pretty_time)
- ✅ Types d'actions (Photo, Boucle, Interval)
- ✅ Gestion Mirror Lock-Up
- ✅ Mode test complet
- ✅ Vérifications système (batterie, stockage, mode)

### Améliorations apportées

- 🆕 Support multi-caméras simultané
- 🆕 Gestion d'erreurs avancée avec isolation par appareil
- 🆕 Logging structuré avec niveaux et rotation
- 🆕 Validation système complète
- 🆕 Tests unitaires exhaustifs
- 🆕 Interface en ligne de commande riche

## Dépannage

### Problèmes courants

**Caméras non détectées**
```bash
# Vérifier les permissions USB
ls -l /dev/bus/usb/*/
# Recharger les règles udev
sudo udevadm control --reload-rules
```

**Erreurs GPhoto2**
```bash
# Tuer les processus en conflit
sudo pkill -f gphoto
sudo pkill -f PTPCamera
# Redémarrer udev
sudo systemctl restart udev
```

**Problèmes de timing**
- Vérifier la synchronisation NTP
- Augmenter `check_interval` si le système est lent
- Utiliser `--log-level DEBUG` pour diagnostiquer

### Logs et diagnostic

```bash
# Logs détaillés
tail -f eclipse_oz.log

# Vérification configuration
python3 main.py config_eclipse.txt --test-mode --log-level DEBUG

# Test sans caméras
python3 -c "
from utils.validation import SystemValidator
validator = SystemValidator()
print(f'Système OK: {validator.validate_system()}')
"
```

## Performance et limitations

### Performance

- **Timing** : Précision < 1s sur séquences longues (> 2h)
- **Multi-caméras** : Déclenchement simultané < 100ms
- **Ressources** : Compatible Raspberry Pi 3B+ et supérieur

### Limitations connues

- Support limité aux appareils Canon compatibles GPhoto2
- Mirror Lock-Up spécifique par modèle (nécessite adaptation)
- Détection espace libre caméra limitée selon modèle

## Migration depuis Magic Lantern

### Procédure de migration

1. **Sauvegarde** : Copier vos fichiers SOLARECL.TXT existants
2. **Adaptation** : Renommer en config_eclipse.txt (optionnel)
3. **Test** : Exécuter en mode test pour valider
4. **Déploiement** : Installer sur Raspberry Pi
5. **Validation** : Test complet avec matériel réel

### Compatibilité

- ✅ Format SOLARECL.TXT : Compatible à 100%
- ✅ Calculs temporels : Identiques au Lua original
- ✅ Séquences d'actions : Comportement équivalent
- ⚠️ APIs caméra : Différentes mais fonctionnellement équivalentes

## Contribution

### Structure de développement

```bash
# Cloner et configurer
git clone <repository>
cd eclipse_oz_python

# Environnement de développement
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .

# Tests et qualité code
pytest tests/
black .
flake8 .
mypy .
```

### Guidelines

- Tests unitaires obligatoires pour nouveau code
- Documentation inline complète
- Respect PEP 8 avec Black
- Logging approprié pour débogage
- Gestion d'erreurs exhaustive

## Support et communauté

### Ressources

- **Documentation** : Ce README et docstrings dans le code
- **Tests** : Exemples d'usage dans tests/
- **Exemples** : Fichiers config_eclipse.txt

### Rapports de bugs

Inclure dans tout rapport :
- Version Python et OS
- Modèles d'appareils photo
- Fichier de configuration utilisé
- Logs complets avec --log-level DEBUG
- Étapes de reproduction

---

## Changelog

### v3.0.0 - Migration initiale
- Migration complète du script Magic Lantern
- Support multi-caméras GPhoto2
- Architecture modulaire Python
- Tests unitaires complets
- Documentation exhaustive

---

**Auteurs** : Équipe Eclipse_OZ Migration
**Licence** : Compatible avec Magic Lantern
**Support** : Raspberry Pi 3B+ et supérieur