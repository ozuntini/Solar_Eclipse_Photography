#!/usr/bin/env python3
"""
Script de test pour le contrôle d'un GeminiAutoFlatPanel via USB/Serial.
Ce script permet d'ouvrir ou de fermer le panneau, ou de vérifier son état actuel.
Il utilise la classe `GeminiAutoFlatPanel` définie dans `filter_controller.py`.
"""
from filter_control.filter_controller import GeminiAutoFlatPanel, CoverState  # Import modifié pour correspondre à la structure du projet Solar Eclipse Photography
import logging
import argparse


parser = argparse.ArgumentParser(
    description='Contrôler un GeminiAutoFlatPanel',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
Exemples:
  python test_filter_controller.py Open
  python test_filter_controller.py Close
  python test_filter_controller.py Status
  python test_filter_controller.py --port /dev/ttyUSB0 --baudrate 9600 Open
"""
)
parser.add_argument('--port', default='/dev/gflatpanel', help='Port USB (par défaut: /dev/gflatpanel)')
parser.add_argument('--baudrate', type=int, default=9600, help='Vitesse de communication (par défaut: 9600)')
parser.add_argument('--timeout', type=float, default=1, help='Délai d\'attente en secondes (par défaut: 1)')
parser.add_argument('action', choices=['Open', 'Close', 'Status'], help='Action à effectuer')

args = parser.parse_args()

def get_telemetry(deviceId, motorStatus, lightStatus, coverStatus):
    # Mapping pour le moteur
    # 0: Arrêté, 1: En mouvement
    motor_labels = {
        0: "STOPPED ✅",
        1: "RUNNING ⚙️"
    }

    # Mapping critique pour le couvercle (Filtre Solaire)
    # On utilise des termes de sécurité pour éviter toute confusion
    cover_labels = {
        0: "TRANSITION - MOVING ⚠️",      # En cours de mouvement
        1: "SAFE - FILTER ENGAGED ✅",    # Filtre bien en place
        2: "DANGER - FILTER RETRACTED 🔥", # Filtre retiré (Photo uniquement)
        3: "ERROR - UNKNOWN POSITION ❌"   # État indéterminé
    }

    return {
        "device_id": f"UNIT_{deviceId}" if deviceId is not None else "UNKNOWN_DEVICE ❓",
        "motor": motor_labels.get(motorStatus, "UNKNOWN ❓"),
        "light": "ON 💡" if lightStatus == 1 else "OFF 🌑",
        "status": cover_labels.get(coverStatus, "CRITICAL ERROR 🚨")
    }

# Exemple d'utilisation :
# data = get_telemetry(1, 0, 0, 0)
# print(f"État actuel : {data['status']}")

# Configurer le logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Créer une instance
panel = GeminiAutoFlatPanel(port=args.port, baudrate=args.baudrate, timeout=args.timeout)

try:
    # Se connecter
    if panel.connect():
        try:
            if panel.health_check() is not None:
                logging.info("Health check passed: Le panneau est en bonne santé.")
            if args.action == 'Open':
                print("🔓 Ouverture du panneau...")
                cover = panel.open_cover()
                if cover == CoverState.OPENED:
                    print("✅ Panneau ouvert avec succès")
                else:
                        print("❌ Échec de l'ouverture du panneau")
            elif args.action == 'Close':
                print("🔒 Fermeture du panneau...")
                cover = panel.close_cover()
                if cover == CoverState.CLOSED:
                    print("✅ Panneau fermé avec succès")
                else:
                    print("❌ Échec de la fermeture du panneau")
            elif args.action == 'Status':
                print("🔍 Vérification de l'état du panneau...")
                status = panel.get_device_status()
                telemetry = get_telemetry(
                    deviceId=str(status['device_id']),
                    motorStatus=int(status['motor_status']),
                    lightStatus=int(status['light_status']),
                    coverStatus=int(status['cover_status'])
                )
                if status:
                    print(f"✅ État du device:")
                    print(f"   ID: {telemetry['device_id']}")
                    print(f"   Moteur: {telemetry['motor']}")
                    print(f"   Lumière: {telemetry['light']}")
                    print(f"   Couvercle: {telemetry['status']}")
                else:
                    print("❌ Impossible de lire l'état")
        except Exception as e:
            logging.error(f"Une erreur est survenue lors de l'exécution de l'action: {e}")
    else:
        print("❌ Échec de la connexion au panneau")
        
finally:
    # Toujours fermer la connexion
    panel.disconnect()