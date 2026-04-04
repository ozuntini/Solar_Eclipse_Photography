# Architecture du système Solar Eclipse Photography

## Vue d'ensemble

**Solar Eclipse Photography** est une migration en Python/GPhoto2 du script Magic Lantern `eclipse_OZ.lua`. C'est une application de contrôle d'appareil photo multi-caméras spécialisée pour la photographie d'éclipse solaire sur Raspberry Pi.

**Version:** 3.0.1  
**Langage:** Python 3.7+  
**Licence:** Non spécifiée  
**Status:** En développement actif

---

## Architecture générale

```
┌─────────────────────────────────────────────────────────────────┐
│                         main.py                                 │
│                (Point d'entrée application)                     │
└────────────┬────────────────────────────────────────────────────┘
             │
    ┌────────┴───────┬─────────────────┬─────────────┐
    │                │                 │             │
┌───▼───┐      ┌─────▼────┐      ┌─────▼────┐    ┌───▼───┐
│config │      │ hardware │      │scheduling│    │ utils │
│       │      │          │      │          │    │       │
└───────┘      └──────────┘      └──────────┘    └───────┘
```

### Modules principaux

| Module | Responsabilité | Fichiers |
|--------|-----------------|----------|
| **config** | Analyse et structure de configuration | `eclipse_config.py`, `config_parser.py` |
| **hardware** | Contrôle caméras et filtre | `camera_controller.py`, `multi_camera_manager.py`, `filter_controller.py` |
| **scheduling** | Exécution d'actions programmées | `action_scheduler.py`, `time_calculator.py`, `action_types.py` |
| **utils** | Utilitaires système | `logger.py`, `validation.py`, `constants.py` |

---

## 1. Module Configuration (`config/`)

### Architecture

```
config/
├── __init__.py              # Exports publics
├── eclipse_config.py        # Structures de données
└── config_parser.py         # Analyse de fichiers
```

### Classes principales

#### `eclipse_config.py`

**`EclipseTimings`** (dataclass)
- Représente les 5 contacts de l'éclipse
- Attributs: `c1`, `c2`, `max`, `c3`, `c4` (objets `time`)

**`ActionConfig`** (dataclass)
- Configuration d'une action photographique
- Attributs clés:
  - `action_type`: 'Photo', 'Boucle', 'Interval', ou 'Filter'
  - `time_ref`: Référence temporelle ('C1', 'C2', 'Max', 'C3', 'C4', ou '-')
  - `start_operator`: '+' ou '-' (relative au time_ref)
  - `start_time`, `end_time`: Décalages temporels
  - `interval_or_count`: Secondes/nombre pour boucles/intervalles
  - `aperture`, `iso`, `shutter_speed`: Paramètres de capture
  - `mlu_delay`: Délai d'attente après verrouillage du miroir (ms)

**`VerificationConfig`** (dataclass)
- Paramètres de vérification système
- Attributs: `check_battery`, `check_storage`, `check_mode`, `check_autofocus`

**`SystemConfig`** (dataclass)
- Configuration globale du système
- Attributs: `eclipse_timings`, `verification`, `actions`, `test_mode`

**`CameraSettings`** (dataclass)
- Paramètres GPhoto2
- Attributs: `capturetarget`, `iso`, `aperture`, `shutter`

**`CameraStatus`** (dataclass)
- État actuel de la caméra
- Attributs: `battery_level`, `free_space_mb`, `mode`, `af_enabled`, `connected`

#### `config_parser.py`

**`ConfigParser`** (classe)
- Parse fichiers SOLARECL.TXT/config_eclipse.txt
- Méthodes principales:
  - `parse_eclipse_config(filename)` → `SystemConfig`
  - `_parse_config()` → `EclipseTimings`
  - `_parse_verification()` → `VerificationConfig`
  - `_parse_action()` → `ActionConfig`
  - `_split_config_line()` → gère séparateurs (virgules, deux-points)

**`ConfigParserError`** (exception personnalisée)
- Erreur de parsing avec numéro de ligne

### Format de fichier configuration

Exemple `config_eclipse.txt`:
```
Config,14:41:05,16:02:49,16:03:53,16:04:58,17:31:03
Verif,3,0,20,4000
Photo,C1,+,00:30:00,_,_,_,8,200,1/1000,100
Boucle,C2,+,00:05:00,-,00:15:00,2,5.6,400,1/500,50
Interval,Max,-,00:02:00,+,00:02:00,5,8,320,1/250,0
Filter,C1,-,00:01:00,_,_,_,1
```

---

## 2. Module Hardware (`hardware/`)

### Architecture

```
hardware/
├── __init__.py                  # Exports: CameraController, MultiCameraManager
├── camera_controller.py         # Contrôle caméra individuelle
├── multi_camera_manager.py      # Orchestration multi-caméras
└── filter_controller.py         # Contrôle panneau Gemini AutoFlatPanel
```

### `camera_controller.py`

**Dépendances externes**
- GPhoto2 (avec fallback mock pour développement)
- Utilise l'API Python `gphoto2`

**`CameraController`** (classe)
- Interface caméra individuelle
- Remplace l'API Magic Lantern par GPhoto2

**Méthodes principales**
| Méthode | Équivalent Lua | Retour |
|---------|-----------------|--------|
| `connect(address)` | caméra.init() | bool |
| `disconnect()` | caméra.exit() | void |
| `get_status()` | caméra.battery.level | CameraStatus |
| `configure_settings(settings)` | caméra.iso.value = ... | bool |
| `capture_image(test_mode)` | caméra.shoot(false) | str/None |
| `mirror_lockup(enabled, delay)` | MLU configuration | bool |

**Fonctionnalités**
- Connexion/déconnexion GPhoto2
- Lecture de statut (batterie, stockage, mode, AF)
- Configuration caméra (ISO, ouverture, vitesse, cible)
- Capture image
- Support verrouillage miroir (MLU)
- Mock mode pour développement sans GPhoto2

**Stratégie de fallback GPhoto2**
```python
try:
    import gphoto2 as gp
    GPHOTO2_AVAILABLE = True
except ImportError:
    GPHOTO2_AVAILABLE = False
    gp = MockGPhoto2()  # Mock objects pour tests
```

### `multi_camera_manager.py`

**`MultiCameraManager`** (classe)
- Gère dictionnaire de `CameraController`
- Coordination capture synchrone multi-caméras

**Méthodes principales**
| Méthode | Description | Retour |
|---------|-------------|--------|
| `discover_cameras()` | Détecte caméras GPhoto2 | List[int] |
| `configure_all(settings)` | Configure toutes caméras | Dict[id, bool] |
| `configure_individual(id, settings)` | Configure caméra spécifique | bool |
| `capture_all(test_mode)` | Capture parallèle | Dict[id, str/None] |
| `capture_sequence(count, interval)` | Séquence de captures | List[Dict] |
| `get_all_status()` | Statut de toutes caméras | Dict[id, CameraStatus] |
| `validate_all_cameras()` | Validation pré-session | bool |
| `disconnect_all()` | Déconnecte toutes caméras | void |
| `set_active_cameras(ids)` | Restreint caméras actives | void |

**Synchronisation capture parallèle**
- Utilise threading pour captures simultanées
- Timeout 30s par caméra
- Log résultats pour chaque caméra

### `filter_controller.py`

**`GeminiAutoFlatPanel`** (classe)
- Contrôle Gemini Flat Panel via USB/Serial
- Protocole propriétaire (commandes texte)

**Commandes**
```
>O# : Ouvrir couvercle (retrait filtre solaire)
>C# : Fermer couvercle (mise en place filtre)
>S# : Statut du dispositif
```

**Énumération `CoverState`**
```python
OPEN = "opened"
CLOSED = "closed"
MOVING = "moving"
UNKNOWN = "unknown"
```

**Méthodes principales**
| Méthode | Retour |
|---------|--------|
| `connect()` | bool |
| `disconnect()` | void |
| `send_command(cmd)` | str/None |
| `open_cover()` | CoverState |
| `close_cover()` | CoverState |
| `get_device_status()` | Dict/None |
| `health_check()` | bool |

---

## 3. Module Scheduling (`scheduling/`)

### Architecture

```
scheduling/
├── __init__.py                  # Exports
├── action_scheduler.py          # Exécution d'actions
├── time_calculator.py           # Calculs temporels
└── action_types.py              # Définitions d'actions
```

### `time_calculator.py`

**`TimeCalculator`** (classe)
- Conversion temps et calculs relatifs éclipse
- Cache pré-calculé des temps de référence

**Méthodes principales**
| Méthode | Équivalent Lua | Description |
|---------|-----------------|-------------|
| `time_to_seconds(t)` | convert_second() | time → secondes depuis minuit |
| `seconds_to_time(s)` | pretty_time() | secondes → time object |
| `convert_relative_time(ref, op, offset)` | convert_time() | Convertit C1±00:30:00 → temps absolu |
| `wait_until(target)` | Boucle attente | Attend jusqu'à target_time |
| `get_time_difference(t1, t2)` | Calcul durée | Durée en secondes entre deux heures |
| `validate_eclipse_sequence()` | Validation | Vérifie chrono: C1<C2<Max<C3<C4 |

**Validation éclipse**
- Vérifie ordre chronologique C1→C2→Max→C3→C4
- Vérifie durée totalité ≤ 7m32s
- Log avertissements si anormal

### `action_types.py`

**Hiérarchie d'actions**
```
BaseAction (abstract)
├── PhotoAction          → Capture unique
├── LoopAction           → Boucle d'intervalles (exemple: Photo toutes les 2s)
├── IntervalAction       → N photos distribuées (exemple: 5 photos entre C1 et C4)
└── FilterAction         → Contrôle panneau filtre
```

**`BaseAction`** (classe abstraite)
- Méthodes abstraites: `validate()`, `get_description()`
- Attributs: `config: ActionConfig`, `action_type: ActionType`

**Concrétisations**

| Classe | Validation | Description |
|--------|-----------|-------------|
| `PhotoAction` | start_time, time_ref requis | Capture simple |
| `LoopAction` | start/end_time, interval_or_count | Boucle continue sur durée |
| `IntervalAction` | start/end_time, photo count | N photos distribuées |
| `FilterAction` | start_time, cover (0/1) | Commande filtre |

**Factory**
```python
create_action(config: ActionConfig) → BaseAction
```
- Route vers classe appropriée
- Valide configuration
- Lève ValueError si invalide

### `action_scheduler.py`

**`ActionScheduler`** (classe)
- Exécute actions en temps réel
- Suivi statistiques

**Méthodes principales**
| Méthode | Description |
|---------|-------------|
| `execute_action(action)` | Route selon type (Photo/Boucle/Interval/Filter) |
| `execute_photo_action(action)` | Capture unique à temps précis |
| `execute_loop_action(action)` | Boucle captures sur durée |
| `execute_interval_action(action)` | N captures distribuées |
| `execute_filter_action(action)` | Ouverture/fermeture filtre |
| `get_execution_stats()` | Retourne compteurs |

**Mécanique temporelle Photo action**
```
1. Calcul temps déclenchement (relatif ou absolu)
2. Si MLU > 0:
   - Attendre (start_time - MLU - 1s)
   - Appliquer verrouillage miroir
   - Sleep(MLU ms)
3. Capture simultanée toutes caméras
4. Compter réussites
```

**Mécanique Boucle**
```
1. Calcul start/end times
2. Configuration caméras
3. Attendre start_time
4. BOUCLE tant que now < end_time:
   - À intervalle régulier: capture tous caméras
   - Sleep(100ms) pour éviter busy-wait
5. Log nombre d'itérations
```

**Mécanique Interval**
```
1. Calcul duration = end_time - start_time
2. Calcul interval_entre_photos = duration / (count - 1)
3. Pour chaque photo (0 à count-1):
   - Capture
   - Sleep(interval)
```

**Statistiques suivi**
```python
actions_executed: int      # Actions réussies
photos_taken: int          # Photos capturées totales
execution_errors: int      # Erreurs lors exécution
test_mode: bool            # Flag simulation
```

---

## 4. Module Utils (`utils/`)

### Architecture

```
utils/
├── __init__.py              # Exports publics
├── constants.py             # Constantes globales
├── logger.py                # Configuration logging
└── validation.py            # Validation système/caméras
```

### `constants.py`

**Constantes d'application**
```python
APP_NAME = "Eclipse Photography Controller"
APP_VERSION = "3.0.0"
APP_DESCRIPTION = "Python/GPhoto2 migration of Magic Lantern eclipse_OZ.lua"

# Defaults GPhoto2
DEFAULT_CAPTURE_TARGET = "1"  # Memory card
DEFAULT_ISO = 400
DEFAULT_APERTURE = 8.0
DEFAULT_SHUTTER = "1/250"

# Serial filter
DEFAULT_SERIAL_PORT = "/dev/ttyUSB0"
DEFAULT_BAUD_RATE = 9600
DEFAULT_TIMEOUT = 1.0

# Validation
MIN_BATTERY_LEVEL = 50  # %
MIN_FREE_SPACE_MB = 5000  # MB
GPHOTO2_SHUTTER_VALUES = [...]
```

### `logger.py`

**`setup_logging(level, log_file, enable_color)`**
- Configure logging racine
- Console avec couleurs (colorlog) si disponible
- Optionnellement fichier log
- Format: `timestamp - logger - level - message`

**`EclipseLoggerAdapter`** (classe)
- Wrapper logging avec contexte éclipse
- Ajoute phase, camera_id, action_type aux messages
- Exemple: `[Phase:C1 Cam:0] Photo captured`

**Factory loggers**
```python
get_logger(name) → Logger
create_phase_logger(phase) → EclipseLoggerAdapter
create_camera_logger(camera_id) → EclipseLoggerAdapter
create_action_logger(action_type) → EclipseLoggerAdapter
quick_setup(level, log_to_file) → Logger
```

### `validation.py`

**`SystemValidator`** (classe)
- Valide pré-conditions avant photographie éclipse

**Validation système** (`validate_system()`)
```
✓ Python version ≥ 3.7
✓ GPhoto2 disponible (commande + module Python)
✓ Permissions USB (udev rules)
✓ Espace stockage ≥ 1GB
✓ Horloge système ≥ 2020
```

**Validation caméras** (`validate_cameras(camera_manager, config)`)
```
Pour chaque caméra:
  ✓ Connectée
  ✓ Batterie ≥ MIN_BATTERY_LEVEL (config ou 50%)
  ✓ Stockage ≥ MIN_FREE_SPACE_MB (config ou 5000MB)
  ✓ Mode OK (si config.check_mode)
  ✓ AF status OK (si config.check_autofocus)
```

**Validation configuration** (`validate_configuration(config)`)
```
✓ Timings éclipse logiques
✓ Séquence actions valides
✓ Paramètres caméra raisonnables (ISO, aperture, shutter)
```

---

## 5. Point d'entrée (`main.py`)

### `EclipsePhotographyController`

**Architecture**
```python
class EclipsePhotographyController:
    __init__(config_file, **options)
    
    Components:
    - config: SystemConfig
    - camera_manager: MultiCameraManager
    - time_calculator: TimeCalculator
    - scheduler: ActionScheduler
    - validator: SystemValidator
    - logger: Logger
```

**Cycle de vie**
```
1. __init__() → Initialise état
2. initialize() → Setup logging, parse config, détermine caméras, valide système/caméras
3. run() → Affiche timings éclipse, valide séquence, exécute actions en boucle
4. cleanup() → Déconnecte caméras
5. signal_handler() → Gestion SIGINT/SIGTERM
```

### Exécution

**Ligne de commande**
```bash
python main.py config_eclipse.txt [options]
python main.py config_eclipse.txt --test-mode
python main.py config_eclipse.txt --cameras 0 1 2 --log-level DEBUG
```

**Options**
```
--test-mode         : Simule captures sans GPhoto2
--log-level LEVEL   : DEBUG, INFO, WARNING, ERROR (défaut: INFO)
--log-file FILE     : Fichier log (défaut: eclipse_oz.log)
--cameras IDS       : Caméras spécifiques ex: 0 1 2
--strict-mode       : Arrête séquence au premier erreur
--version           : Affiche version
```

**Retour exit code**
- 0 : Succès
- 1 : Erreur

---

## 6. Flux d'exécution complet

### Diagramme flux principal

```
START
  │
  ├─→ initialize()
  │    ├─→ Setup logging
  │    ├─→ Parse config_eclipse.txt → SystemConfig
  │    ├─→ Découvre caméras GPhoto2
  │    ├─→ SystemValidator.validate_system() ← Python, GPhoto2, USB, Storage, Time
  │    ├─→ SystemValidator.validate_configuration()
  │    └─→ SystemValidator.validate_cameras()
  │
  ├─→ run()
  │    ├─→ Log timings éclipse (C1, C2, Max, C3, C4)
  │    ├─→ TimeCalculator.validate_eclipse_sequence()
  │    ├─→ Log info caméras
  │    │
  │    └─→ POUR CHAQUE action dans actions:
  │         ├─→ ActionScheduler.execute_action()
  │         │    ├─→ create_action() → PhotoAction/LoopAction/IntervalAction/FilterAction
  │         │    ├─→ Calcul temps déclenchement
  │         │    ├─→ TimeCalculator.wait_until(trigger_time)
  │         │    ├─→ MultiCameraManager.configure_all() [sauf Filter]
  │         │    └─→ SELON TYPE:
  │         │         ├─ Photo: capture_all() × 1
  │         │         ├─ Loop: capture_all() × N à intervalle
  │         │         ├─ Interval: capture_all() × N distribué
  │         │         └─ Filter: GeminiAutoFlatPanel.open/close_cover()
  │         └─→ Incrémente stats
  │
  ├─→ cleanup()
  │    └─→ MultiCameraManager.disconnect_all()
  │
  └─→ EXIT(code)
```

### Exemple exécution action Photo

```
Action: Photo,C2,+,00:05:00,_,_,_,8,200,1/500,100

1. TimeCalculator.convert_relative_time("C2", "+", 00:05:00)
   → Calcule C2 + 5 minutes = temps absolu

2. ActionScheduler._configure_cameras_for_action()
   → CameraSettings(iso=200, aperture=8, shutter="1/500")
   → MultiCameraManager.configure_all() 
     → CameraController.configure_settings() × N caméras

3. ActionScheduler._calculate_action_time(..., 'start')
   → trigger_time = temps absolue

4. ActionScheduler.execute_photo_action()
   a) TimeCalculator.wait_until(trigger_time - 100ms MLU delay)
   b) ActionScheduler._apply_mirror_lockup(100)
   c) MultiCameraManager.capture_all(test_mode=False)
      - Lance N threads (1 par caméra)
      - CameraController.capture_image() × N
      - Attend timeout 30s
      - Log résultats
   d) Compte réussites

5. Incrémente ActionScheduler.photos_taken
```

---

## 7. Patterns et bonnes pratiques

### Design Patterns

| Pattern | Usage | Exemple |
|---------|-------|---------|
| **Factory** | Création d'objets | `create_action(config)` |
| **Adapter** | Logging contexte | `EclipseLoggerAdapter` |
| **Strategy** | Exécution actions | Boucle/Photo/Interval polymorphe |
| **Observer** | Gestion signaux | `signal_handler()` SIGINT/SIGTERM |
| **Singleton** | Loggers | `logging.getLogger(name)` |

### Gestion d'erreurs

**Hiérarchie exceptions**
```
Exception
├── ConfigParserError          (config parsing)
├── ValidationError            (validation système)
└── Exceptions Python standard (GPhoto2, Serial, etc.)
```

**Stratégie**
- Try/except systématique autour GPhoto2/Serial
- Fallback gracieux (mock, continues partielles)
- Log détaillé exc_info=True pour debug

### Concurrence

- **Threading**: Captures parallèles
  - Locks (threading.Lock) pour résultats
  - Timeout 30s par thread
  - Synchronisation capture (sleep 0.1-0.25s)

- **Timing critique**
  - time_calculator.wait_until() vs time.time()
  - Delta 30s acceptable pour timing éclipse
  - MLU delay appliqué avant capture

### Configuration

- **Fichier texte** SOLARECL.TXT compatible Magic Lantern
- **Parser robuste**:
  - Gère virgules + doubles-points
  - Valide ranges temporels
  - Stockage en dataclasses
- **Defaults** pour paramètres manquants

---

## 8. Points d'extension

### Améliorations possibles

1. **Caméras supplémentaires**
   - Adapter `camera_controller.py` pour API alternatives
   - Implémenter `CameraInterface` abstraite

2. **Filtres hardware**
   - Ajouter FilterAction variants
   - Support PWM GPIO Raspberry Pi

3. **Monitoring distant**
   - `monitoring.py` serveur HTTP JSON
   - Dashboard temps réel

4. **Persistance**
   - Base données captures
   - Historique exécutions

5. **Optimisations**
   - Cache GPhoto2 config
   - Thread pool capture
   - Prediction timing capture

---

## 9. Dépendances externes

### Obligatoires
- **gphoto2** (commande système + module Python)
- **python >= 3.7**
- **pyserial** (pour GeminiAutoFlatPanel)

### Optionnelles
- **colorlog** (logging couleur)

### Devdependencies (tests)
- pytest
- unittest.mock

---

## 10. Fichiers de configuration exemple

### `config_eclipse.txt`

```
# Eclipse 2024-04-08 (exemple)
Config,14:41:05,16:02:49,16:03:53,16:04:58,17:31:03

# Vérification caméra
Verif,3,0,20,4000

# Actions
Photo,C1,-,00:10:00,_,_,_,5.6,100,1/1000,0
Boucle,C2,+,00:00:00,-,00:05:00,1,8,400,1/500,100
Interval,Max,-,00:02:00,+,00:02:00,5,11,800,1/250,50
Filter,C3,-,00:01:00,_,_,_,0
```

### Structure répertoires

```
Solar_Eclipse_Photography/
├── main.py                      # Point d'entrée
├── config_eclipse.txt           # Config session
├── config/                      # Module config
│   ├── __init__.py
│   ├── eclipse_config.py
│   └── config_parser.py
├── hardware/                    # Module hardware
│   ├── __init__.py
│   ├── camera_controller.py
│   ├── multi_camera_manager.py
│   └── filter_controller.py
├── scheduling/                  # Module scheduling
│   ├── __init__.py
│   ├── action_scheduler.py
│   ├── time_calculator.py
│   └── action_types.py
├── utils/                       # Module utils
│   ├── __init__.py
│   ├── constants.py
│   ├── logger.py
│   ├── validation.py
│   └── __pycache__/
├── scripts_eclipse/             # Configs d'exemple
│   ├── config_eclipse.txt
│   ├── config_photo_unique.txt
│   ├── config_photo_boucle.txt
│   ├── config_photo_interval.txt
│   └── config_photo_filter.txt
├── tests/                       # Suite de tests
│   ├── test_*.py
│   └── __init__.py
├── docs/                        # Documentation (créé)
├── scheduling/                  # Cron jobs
├── hardware/                    # Notes hardware
└── doc_migration/               # Migration Lua→Python
```

---

## Conclusion

Cette architecture module la migration complète du script Lua Magic Lantern vers une solution Python production-ready avec:

✅ **Séparation des concerns** nette (config/hardware/scheduling/utils)  
✅ **Multi-caméras** synchrone via threading  
✅ **Timing précis** eclipse avec calculs relatifs (C1/C2/Max/C3/C4)  
✅ **Validation système** pré-exécution complète  
✅ **Mock mode** pour développement sans caméras  
✅ **Logging structuré** avec contexte  
✅ **Gestion erreurs** robuste et gracieuse  
✅ **Tests** complets (11 suites de tests)

Pour questions ou contributions: voir [README.md](README.md) et [DOCUMENTATION_PYTHON.md](DOCUMENTATION_PYTHON.md)
```

Ce document d'architecture couvre:

1. ✅ **Vue d'ensemble** - Structure modulaire
2. ✅ **Configuration** - Parsing, structures de données
3. ✅ **Hardware** - Caméras, filtres, synchronisation
4. ✅ **Scheduling** - Actions, timing, calculs
5. ✅ **Utilities** - Logging, validation, constantes
6. ✅ **Point d'entrée** - Flux principal
7. ✅ **Patterns** - Design, concurrence, erreurs
8. ✅ **Dépendances** - Externes et optionnelles
9. ✅ **Examples** - Config et structure répertoires

Vous pouvez maintenant créer ce fichier dans votre dépôt ou l'adapter selon vos besoins!