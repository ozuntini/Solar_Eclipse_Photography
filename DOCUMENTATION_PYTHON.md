# Documentation Eclipse Photography Controller - Version Python

## Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture et structure](#architecture-et-structure)
3. [Installation et configuration](#installation-et-configuration)
4. [Utilisation](#utilisation)
5. [Modules et API](#modules-et-api)
6. [Tests et validation](#tests-et-validation)
7. [Comparaison avec la version Lua](#comparaison-avec-la-version-lua)
8. [Validation de cohérence Lua/Python](#validation-de-cohérence-luapython)
9. [Dépannage](#dépannage)
10. [Développement et contribution](#développement-et-contribution)

## Vue d'ensemble

### Présentation

Eclipse Photography Controller est une migration Python/GPhoto2 du script Magic Lantern `eclipse_OZ.lua`. Cette application permet l'automatisation de la photographie d'éclipse avec support multi-caméras sur Raspberry Pi ou tout système Linux compatible.

### Objectifs de la migration

- **Modernisation**: Passage de Lua/Magic Lantern vers Python/GPhoto2
- **Portabilité**: Fonctionnement sur Raspberry Pi et systèmes Linux
- **Multi-caméras**: Support natif de plusieurs appareils photo
- **Robustesse**: Gestion d'erreurs avancée et logging détaillé
- **Testabilité**: Suite de tests complète et validation automatique

### Fonctionnalités principales

- ✅ Parsing et validation des fichiers de configuration SOLARECL.TXT
- ✅ Calculs précis de timing d'éclipse avec références temporelles (C1, C2, Max, C3, C4)
- ✅ Support des actions : Photo, Boucle, Interval
- ✅ Contrôle multi-caméras via GPhoto2
- ✅ Configuration automatique des paramètres caméra (ISO, ouverture, vitesse)
- ✅ Validation système et vérifications pré-vol
- ✅ Mode test et simulation
- ✅ Logging structuré avec niveaux configurables
- ✅ Tests de régression et comparaison avec version Lua

## Architecture et structure

### Structure des répertoires

```
python/
├── main.py                        # Point d'entrée principal
├── config/                        # Configuration et parsing
│   ├── __init__.py
│   ├── config_parser.py           # Parser SOLARECL.TXT
│   └── eclipse_config.py          # Classes de configuration
├── hardware/                      # Contrôle matériel
│   ├── __init__.py
│   ├── camera_controller.py       # Interface GPhoto2
│   ├── multi_camera_manager.py    # Gestion multi-caméras
│   └── filter_controller.py       # Contrôle panneau Gemini AutoFlatPanel  
├── scheduling/                    # Planification et exécution
│   ├── __init__.py
│   ├── time_calculator.py         # Calculs temporels
│   ├── action_scheduler.py        # Planificateur d'actions
│   └── action_types.py            # Types d'actions
├── utils/                         # Utilitaires communs
│   ├── __init__.py
│   ├── constants.py               # Constantes globales
│   ├── logger.py                  # Configuration logging
│   └── validation.py              # Validations système
├── tests/                         # Tests unitaires et intégration
│   ├── __init__.py
│   ├── test_config_parser.py
│   ├── test_time_calculator.py
│   ├── test_camera_controller.py
│   ├── test_action_scheduler.py
│   ├── test_integration.py
│   ├── test_lua_python_comparison.py
│   └── test_migration_validation.py
├── lua_simulator.py               # Simulateur Lua pour tests
├── run_comparison_tests.py        # Tests comparatifs
├── requirements.txt               # Dépendances Python
├── pyproject.toml                 # Configuration projet
└── README.md                      # Documentation utilisateur
```

### Architecture modulaire

#### Module `config`
- **Purpose**: Parsing et validation des fichiers de configuration
- **Classes principales**:
  - `ConfigParser`: Parser principal pour SOLARECL.TXT
  - `EclipseTimings`: Structure des temps d'éclipse
  - `ActionConfig`: Configuration d'une action photographique
  - `SystemConfig`: Configuration système globale

#### Module `hardware`
- **Purpose**: Interface avec les appareils photo via GPhoto2
- **Classes principales**:
  - `CameraController`: Contrôle d'un seul appareil
  - `MultiCameraManager`: Gestion de plusieurs appareils
  - `CameraSettings`: Configuration caméra (ISO, ouverture, vitesse)
  - `CameraStatus`: État actuel d'un appareil
  - `GeminiAutoFlatPanel` : Contrôle Gemini Flat Panel via USB/Serial

#### Module `scheduling`
- **Purpose**: Planification et exécution des actions photographiques
- **Classes principales**:
  - `TimeCalculator`: Calculs de timing avec références d'éclipse
  - `ActionScheduler`: Exécuteur d'actions (Photo, Boucle, Interval)
  - `ActionType`: Types d'actions supportés

#### Module `utils`
- **Purpose**: Utilitaires communs et services transversaux
- **Composants**:
  - `constants.py`: Constantes globales et valeurs par défaut
  - `logger.py`: Configuration du système de logging
  - `validation.py`: Validations système et pré-vol

## Installation et configuration

### Prérequis système

```bash
# Raspberry Pi OS ou Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip gphoto2 libgphoto2-dev

# Dépendances Python
pip3 install -r requirements.txt
```

### Dépendances Python principales

- `gphoto2` (>= 2.3.0): Interface Python pour libgphoto2
- `dataclasses`: Structures de données (Python 3.7+)
- `typing`: Annotations de type
- `pytest`: Framework de tests
- `pathlib`: Manipulation de chemins

### Configuration matérielle

```bash
# Vérifier détection des appareils
gphoto2 --auto-detect

# Tester capture basique
gphoto2 --capture-image-and-download
```

### Variables d'environnement optionnelles

```bash
export ECLIPSE_LOG_LEVEL=DEBUG           # Niveau de logging
export ECLIPSE_TEST_MODE=1              # Mode test permanent
export ECLIPSE_CONFIG_DIR=/path/to/configs  # Répertoire configs
```

## Utilisation

### Utilisation basique

```bash
# Exécution standard
python main.py config_eclipse.txt

# Mode test (simulation sans capture)
python main.py config_eclipse.txt --test-mode

# Debugging avec logs détaillés
python main.py config_eclipse.txt --log-level DEBUG --log-file eclipse.log

# Limitation à certaines caméras
python main.py config_eclipse.txt --cameras 0 1 2
```

### Options de ligne de commande

```
usage: main.py [-h] [--test-mode] [--log-level {DEBUG,INFO,WARNING,ERROR}]
               [--log-file LOG_FILE] [--cameras CAMERAS [CAMERAS ...]]
               [--strict-mode]
               config_file

Eclipse Photography Controller

positional arguments:
  config_file           Fichier de configuration (ex: SOLARECL.TXT)

optional arguments:
  -h, --help           show this help message and exit
  --test-mode          Mode simulation (pas de capture réelle)
  --log-level {DEBUG,INFO,WARNING,ERROR}
                       Niveau de logging (défaut: INFO)
  --log-file LOG_FILE  Fichier de log (défaut: console)
  --cameras CAMERAS [CAMERAS ...]
                       IDs des caméras à utiliser (ex: 0 1 2)
  --strict-mode        Mode strict (arrêt sur toute erreur)
```

### Format de fichier de configuration

Le format reste compatible avec les fichiers SOLARECL.TXT originaux :

```
# Configuration d'éclipse
Config,18,10,29,19,27,3,19,28,23,19,29,43,20,46,31,1

# Vérifications pré-vol
Verif,3,0,50,2000

# Actions photographiques
Photo,C1,-,0,5,0,-,-,-,8,100,4,0
Boucle,C2,-,0,1,0,+,0,0,30,10,8,200,0.002,0
Interval,Max,+,0,0,30,+,0,1,0,20,5.6,800,0.001,500
Filter,C3,-,00:01:00,_,_,_,0
```

## Modules et API

### Module config

#### ConfigParser

```python
class ConfigParser:
    """Parser principal pour fichiers SOLARECL.TXT"""
    
    def parse_file(self, file_path: str) -> SystemConfig:
        """Parse un fichier de configuration complet"""
    
    def parse_config_line(self, line_parts: List[str]) -> EclipseTimings:
        """Parse une ligne Config avec les temps d'éclipse"""
    
    def parse_action_line(self, line_parts: List[str]) -> ActionConfig:
        """Parse une ligne d'action (Photo/Boucle/Interval)"""
    
    def validate_configuration(self, config: SystemConfig) -> bool:
        """Valide la cohérence de la configuration"""
```

#### EclipseTimings

```python
@dataclass
class EclipseTimings:
    """Structure des temps de contact d'éclipse"""
    c1: time                    # Premier contact
    c2: time                    # Début totalité
    maximum: time               # Maximum éclipse
    c3: time                    # Fin totalité
    c4: time                    # Dernier contact
    test_mode: bool = False     # Mode test activé
```

#### ActionConfig

```python
@dataclass
class ActionConfig:
    """Configuration d'une action photographique"""
    action_type: str            # "Photo", "Boucle", "Interval"
    time_ref: str              # Référence temporelle (C1,C2,Max,C3,C4,-)
    start_operator: str        # Opérateur début (+/-)
    start_time: time          # Temps de début/offset
    end_operator: Optional[str] # Opérateur fin (+/-)
    end_time: Optional[time]   # Temps de fin/offset
    interval_or_count: int     # Intervalle (s) ou nombre
    aperture: Optional[float]  # Ouverture (f-number)
    iso: Optional[int]         # Sensibilité ISO
    shutter_speed: Optional[float] # Vitesse obturation (s)
    mlu_delay: int = 0         # Délai miroir relevé (ms)
```

### Module hardware

#### CameraController

```python
class CameraController:
    """Contrôleur d'un appareil photo via GPhoto2"""
    
    def __init__(self, camera_id: int = 0):
        """Initialise contrôleur pour caméra donnée"""
    
    def connect(self) -> bool:
        """Établit connexion avec l'appareil"""
    
    def configure_settings(self, settings: CameraSettings) -> bool:
        """Configure ISO, ouverture, vitesse"""
    
    def capture_image(self, test_mode: bool = False) -> bool:
        """Capture une image"""
    
    def get_status(self) -> CameraStatus:
        """Récupère état actuel de l'appareil"""
    
    def disconnect(self):
        """Ferme connexion proprement"""
```

#### MultiCameraManager

```python
class MultiCameraManager:
    """Gestionnaire de plusieurs appareils photo"""
    
    def __init__(self, camera_ids: Optional[List[int]] = None):
        """Initialise avec liste d'IDs caméras"""
    
    def initialize_cameras(self) -> Dict[int, bool]:
        """Initialise toutes les caméras"""
    
    def configure_all(self, settings: CameraSettings) -> Dict[int, bool]:
        """Configure tous les appareils"""
    
    def capture_all(self, test_mode: bool = False) -> Dict[int, bool]:
        """Capture simultanée sur tous appareils"""
    
    def get_status_all(self) -> Dict[int, CameraStatus]:
        """État de tous les appareils"""
```

### Module scheduling

#### TimeCalculator

```python
class TimeCalculator:
    """Calculateur de timing avec références d'éclipse"""
    
    def __init__(self, eclipse_timings: EclipseTimings):
        """Initialise avec temps d'éclipse"""
    
    def calculate_absolute_time(self, time_ref: str, operator: str, 
                              offset: time) -> time:
        """Calcule temps absolu depuis référence + offset"""
    
    def time_to_seconds(self, t: time) -> int:
        """Convertit time en secondes depuis minuit"""
    
    def seconds_to_time(self, seconds: int) -> time:
        """Convertit secondes en objet time"""
    
    def wait_until(self, target_time: time, test_mode: bool = False):
        """Attend jusqu'au temps cible (avec simulation en test)"""
```

#### ActionScheduler

```python
class ActionScheduler:
    """Planificateur et exécuteur d'actions photographiques"""
    
    def __init__(self, camera_manager: MultiCameraManager, 
                 time_calculator: TimeCalculator, test_mode: bool = False):
        """Initialise avec gestionnaire caméras et calculateur temps"""
    
    def execute_action(self, action: ActionConfig) -> bool:
        """Exécute une action selon son type"""
    
    def execute_photo_action(self, action: ActionConfig) -> bool:
        """Exécute action Photo (équivalent take_shoot Lua)"""
    
    def execute_loop_action(self, action: ActionConfig) -> bool:
        """Exécute action Boucle (équivalent boucle Lua)"""
    
    def execute_interval_action(self, action: ActionConfig) -> bool:
        """Exécute action Interval (nouvel type)"""
```

### Module utils

#### SystemValidator

```python
class SystemValidator:
    """Validateur système et vérifications pré-vol"""
    
    def validate_system(self, config: SystemConfig) -> bool:
        """Validation complète du système"""
    
    def validate_cameras(self, camera_manager: MultiCameraManager,
                        verification_config: VerificationConfig) -> bool:
        """Validation état des appareils photo"""
    
    def validate_timing_sequence(self, timings: EclipseTimings) -> bool:
        """Validation cohérence séquence temporelle"""
    
    def validate_storage_space(self, min_space_mb: int) -> bool:
        """Validation espace disque disponible"""
```

## Tests et validation

### Architecture de tests

La suite de tests est organisée en plusieurs niveaux :

1. **Tests unitaires** : Chaque module testé individuellement
2. **Tests d'intégration** : Interaction entre modules  
3. **Tests de régression** : Non-régression vs version Lua
4. **Tests de validation** : Cohérence comportementale

### Exécution des tests

```bash
# Tests unitaires complets
python -m pytest tests/ -v

# Tests d'un module spécifique
python -m pytest tests/test_time_calculator.py -v

# Tests de comparaison Lua/Python
python -m pytest tests/test_lua_python_comparison.py -v

# Tests avec couverture
python -m pytest tests/ --cov=config --cov=hardware --cov=scheduling --cov=utils

### Tests unitaires par module

#### test_config_parser.py
- Parsing des différents types de lignes
- Validation des formats temporels
- Gestion des erreurs de syntaxe
- Validation de cohérence des configurations

#### test_time_calculator.py
- Calculs de temps avec références d'éclipse
- Conversions temporelles (time ↔ secondes)
- Gestion des offsets positifs/négatifs
- Validation des séquences temporelles

#### test_camera_controller.py
- Simulation des interactions GPhoto2
- Configuration des paramètres caméra
- Gestion des erreurs de connexion
- Validation des formats de paramètres

#### test_action_scheduler.py
- Exécution des différents types d'actions
- Synchronisation temporelle précise
- Configuration automatique des caméras
- Gestion des modes test/production

### Tests d'intégration

#### test_integration.py
- Flux complet de traitement
- Intégration config → hardware → scheduling
- Scénarios d'éclipse complets
- Gestion d'erreurs cross-modules

### Tests de validation migration

#### test_migration_validation.py
- Validation équivalence fonctionnelle Lua/Python
- Tests de non-régression comportementale
- Comparaison des outputs pour inputs identiques
- Validation des performances temporelles

## Comparaison avec la version Lua

### Équivalences fonctionnelles

| Fonction Lua | Équivalent Python | Module | Notes |
|--------------|------------------|---------|-------|
| `read_script()` | `ConfigParser.parse_file()` | config | Parsing SOLARECL.TXT |
| `convert_second()` | `TimeCalculator.time_to_seconds()` | scheduling | Conversion temps |
| `pretty_time()` | `TimeCalculator.seconds_to_time()` | scheduling | Format temps |
| `do_action()` | `ActionScheduler.execute_action()` | scheduling | Distribution actions |
| `take_shoot()` | `ActionScheduler.execute_photo_action()` | scheduling | Action Photo |
| `boucle()` | `ActionScheduler.execute_loop_action()` | scheduling | Action Boucle |
| `verify_conf()` | `SystemValidator.validate_cameras()` | utils | Vérifications pré-vol |
| `camera.*` | `CameraController.*` | hardware | Interface caméra |

### Améliorations apportées

#### Robustesse
- ✅ Gestion d'erreurs exhaustive avec try/catch
- ✅ Validation des inputs à tous les niveaux
- ✅ Recovery automatique sur erreurs non-critiques
- ✅ Logging structuré avec niveaux configurables

#### Fonctionnalités étendues
- ✅ Support multi-caméras natif
- ✅ Action "Interval" en plus de Photo/Boucle
- ✅ Mode test complet avec simulation
- ✅ Configuration flexible par ligne de commande
- ✅ Validation pré-vol avancée

#### Architecture moderne
- ✅ Code modulaire et testable
- ✅ Séparation claire des responsabilités
- ✅ API documentée avec type hints
- ✅ Configuration par dataclasses
- ✅ Packaging Python standard

### Limitations connues

#### Dépendances externes
- ❌ Nécessite GPhoto2 installé système
- ❌ Limité aux appareils compatibles GPhoto2

#### Performance
- ⚠️ Overhead Python vs Lua sur timing critique
- ⚠️ Gestion mémoire différente pour sessions longues

#### 2. Tests comparatifs automatisés

```python
def test_time_calculations_equivalence():
    """Teste équivalence calculs temporels Lua vs Python"""
    test_cases = [
        ('C1', '-', (0, 5, 0)),    # C1 - 5 minutes
        ('C2', '+', (0, 1, 30)),   # C2 + 1m30s  
        ('Max', '-', (0, 0, 10)),  # Max - 10 secondes
    ]
    
    for time_ref, operator, offset in test_cases:
        lua_result = lua_simulator.calculate_time(time_ref, operator, offset)
        python_result = time_calculator.calculate_absolute_time(time_ref, operator, offset)
        assert lua_result == python_result, f"Mismatch for {time_ref}{operator}{offset}"
```

#### 3. Validation comportementale

```python
def run_comparative_test(config_file: str) -> Dict[str, Any]:
    """Exécute test comparatif complet Lua vs Python"""
    
    # Simulation Lua
    lua_results = run_lua_simulation(config_file)
    
    # Exécution Python
    python_results = run_python_simulation(config_file)
    
    # Comparaison des résultats
    comparison = {
        'config_parsing': compare_config_parsing(lua_results, python_results),
        'time_calculations': compare_time_calculations(lua_results, python_results),
        'action_sequence': compare_action_sequence(lua_results, python_results),
        'camera_configs': compare_camera_configs(lua_results, python_results)
    }
    
    return comparison
```

### Scripts de validation disponibles

#### 1. Tests pytest intégrés
```bash
# Tests comparatifs unitaires
python -m pytest tests/test_lua_python_comparison.py -v
```

### Critères de validation

#### Parsing de configuration
- ✅ **CRITIQUE**: Même interprétation des lignes Config/Verif/Actions
- ✅ **CRITIQUE**: Mêmes calculs de temps d'éclipse
- ✅ **CRITIQUE**: Même validation des paramètres

#### Calculs temporels
- ✅ **CRITIQUE**: Équivalence des conversions time ↔ secondes
- ✅ **CRITIQUE**: Même logique pour références temporelles (C1, C2, Max, C3, C4)
- ✅ **CRITIQUE**: Même gestion des offsets positifs/négatifs
- ✅ **TOLÉRANCE**: ±1ms sur timing final (différences d'implémentation)

#### Séquence d'actions
- ✅ **CRITIQUE**: Même ordre d'exécution des actions
- ✅ **CRITIQUE**: Mêmes temps de déclenchement calculés
- ✅ **MAJEUR**: Même logique de boucles et intervalles
- ⚠️ **ACCEPTABLE**: Différences mineures sur gestion d'erreurs

#### Configuration caméra  
- ✅ **MAJEUR**: Mêmes valeurs ISO/ouverture/vitesse appliquées
- ⚠️ **ACCEPTABLE**: Formats différents (Magic Lantern vs GPhoto2)
- ⚠️ **ACCEPTABLE**: Ordre de configuration différent

### Résolution des divergences

#### Divergences acceptables
1. **Formats de paramètres caméra** : Magic Lantern vs GPhoto2 utilisent des formats différents
2. **Gestion d'erreurs** : Python plus robuste avec try/catch systématiques  
3. **Logging** : Format et niveau de détail différents
4. **Performance** : Overhead Python acceptable pour robustesse gagnée

#### Divergences critiques (à corriger)
1. **Calculs temporels** : Toute différence >1ms doit être investiguée
2. **Parsing configuration** : Interprétation différente = régression critique
3. **Séquence d'actions** : Ordre ou timing différent = bug bloquant

### Procédure de validation pour nouvelles fonctionnalités

1. **Implémentation Python** avec tests unitaires
2. **Extension simulateur Lua** si nécessaire  
3. **Tests comparatifs** sur jeux de données représentatifs
4. **Validation critères** selon grille ci-dessus
5. **Documentation** des éventuelles divergences acceptées

### Outils de debugging

#### Logs de débogage
```python
# Dans time_calculator.py
self.logger.debug(f"Reference {time_ref}: {reference_seconds}s")
self.logger.debug(f"Offset: {operator}{offset_seconds}s")  
self.logger.debug(f"Final time: {result_seconds}s ({self.seconds_to_time(result_seconds)})")
```

Cette approche de validation garantit la fidélité comportementale entre les deux implémentations tout en permettant les améliorations architecturales nécessaires.

## Dépannage

### Problèmes courants

#### 1. Erreurs de connexion caméra
```
ERROR: No camera detected by GPhoto2
```

**Solutions** :
```bash
# Vérifier détection
gphoto2 --auto-detect

# Vérifier permissions
sudo usermod -a -G plugdev $USER
newgrp plugdev

# Redémarrer services conflictuels
sudo systemctl stop gvfs-gphoto2-volume-monitor
sudo killall gvfsd-gphoto2
```

#### 2. Erreurs de configuration
```
ERROR: Configuration file parsing failed
```

**Solutions** :
- Vérifier encodage UTF-8 du fichier
- Contrôler format des lignes (virgules, espaces)
- Valider format des temps (HH:MM:SS)

#### 3. Problèmes de timing
```
WARNING: Action execution delayed by 2.3s
```

**Solutions** :
- Vérifier charge système (top/htop)
- Utiliser nice/ionice pour priorité
- Réduire niveau de logging en production

### Logs de diagnostic

#### Activation debugging complet
```bash
python main.py config.txt --log-level DEBUG --log-file debug.log
```

#### Analyse des logs
```bash
# Erreurs uniquement
grep "ERROR" debug.log

# Performance timing
grep "execution delayed\|took\|duration" debug.log

# Actions exécutées
grep "Photo action\|Loop action\|Interval action" debug.log
```

### Mode de récupération

#### Test de cohérence avant éclipse
```bash
# Simulation complète 2 heures avant
python main.py config.txt --test-mode

# Validation matériel 30 minutes avant  
python main.py config.txt --test-mode --strict-mode
```

#### Vérifications pré-vol
```python
# Dans le code
validator = SystemValidator()
if not validator.validate_system(config):
    logger.critical("System validation failed - ABORT")
    return 1
```

## Développement et contribution

### Configuration environnement développement

```bash
# Clone et setup
git clone https://github.com/ozuntini/Solar_Eclipse_Photography.git

# Environnement virtuel
python -m venv eclipse_env
source eclipse_env/bin/activate

# Dépendances développement
pip install -r requirements.txt
pip install pytest pytest-cov black mypy

# Hooks pre-commit (optionnel)
pip install pre-commit
pre-commit install
```

### Standards de code

#### Formatting
```bash
# Black pour formatting automatique
black --line-length 100 *.py */*.py

# Vérification style
flake8 --max-line-length 100 *.py */*.py
```

#### Type checking
```bash
# MyPy pour vérification types
mypy --strict *.py */*.py
```

#### Tests
```bash
# Tests avec couverture minimale 90%
pytest --cov=. --cov-min=90

# Tests performance/régression
./run_regression_tests.sh
```

### Architecture extensible

#### Ajout nouveau type d'action

1. **Définir ActionType** dans `scheduling/action_types.py`
```python
class CustomAction(ActionType):
    def execute(self, scheduler: ActionScheduler, action: ActionConfig) -> bool:
        # Implémentation spécifique
        pass
```

2. **Enregistrer type** dans `action_scheduler.py`
```python
def execute_action(self, action: ActionConfig) -> bool:
    action_map = {
        "Photo": self.execute_photo_action,
        "Boucle": self.execute_loop_action, 
        "Interval": self.execute_interval_action,
        "Custom": self.execute_custom_action  # Nouveau
    }
```

3. **Ajouter tests** dans `tests/test_action_scheduler.py`

#### Support nouveaux appareils

1. **Étendre CameraController** dans `hardware/camera_controller.py`
2. **Ajouter mappings** dans `utils/constants.py`
3. **Tests compatibilité** dans `tests/test_camera_controller.py`

### Roadmap

#### Version 3.1.0
- [ ] Support appareils WiFi (gphoto2 network)
- [ ] Interface web de monitoring
- [ ] Intégration GPS pour timing automatique
- [ ] Export données EXIF enrichies

#### Version 3.2.0  
- [ ] Support vidéo (capture timelapses)
- [ ] Intégration services cloud (upload auto)
- [ ] API REST pour contrôle externe
- [ ] Application mobile compagnon

#### Version 4.0.0
- [ ] Réécriture en Rust pour performances
- [ ] Support temps réel dur (RTOS)
- [ ] Intégration IA pour optimisation auto
- [ ] Clustering multi-systèmes

---

**Version**: 3.0.1  
**Dernière mise à jour**: Décembre 2024  
**Auteurs**: Équipe Eclipse-OZ  
**License**: GNU GPL v3