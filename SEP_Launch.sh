#!/bin/bash
# Script de test lancement pour Solar_Eclipse_Photography Python

set -e
# Définir une fonction d'erreur
on_error() {
    if [ -n "$VIRTUAL_ENV" ]; then
        # Désactivation de l'environnement virtuel et sortie avec code d'erreur
        echo "Désactivation de l'environnement virtuel et sortie sur erreur..."
        deactivate
    fi
    exit 1
}

# Capturer les erreurs
trap 'on_error' ERR

SEP_SCRIPT_FILE=""
SEP_MODE_TEST=""
SEP_MODE_DEBUG=""
SEP_LOGFILE=""
SEP_STRICT_MODE="--strict-mode"
SEP_JOURNAL_FILE=""

echo "=== Lanceur Solar_Eclipse_Photography ==="

if [ "$1" == "" ] || [ -d "$1" ] || [ "$1" == "-h" ] || [ "$#" -lt 1 ]; then
    echo "usage: SEP_Launch.sh path/script [-n|--no-strict] [-t|--test] [-d|--debug] [--log=path/logfile] [--journal=path/journalfile]"
    exit
else
    SEP_SCRIPT_FILE="$1"
    if [ ! -f "$SEP_SCRIPT_FILE" ] || [ ! -r "$SEP_SCRIPT_FILE" ]; then
        echo "Le fichier "$SEP_SCRIPT_FILE" est introuvable ou n'est pas lisible."
        exit 1
    fi
    # Traiter les paramètres
    shift
    while [[ $# -gt 0 ]]; do
        case $1 in
        -t|--test)
            echo "Mode test activé."
            export SEP_MODE_TEST="--test-mode"
            shift
            ;;
        -d|--debug)
            echo "Mode debug activé."
            export SEP_MODE_DEBUG="--log-level DEBUG"
            shift
            ;;
        -n|--no-strict)
            echo "Mode strict désactivé."
            export SEP_STRICT_MODE=""
            shift
            ;;
        --log=*)
            LOGPATH="${1#--log=}"
            echo "Log activé. Fichier de log: $LOGPATH"
            export SEP_LOGFILE="--log-file $LOGPATH"
            shift
            ;;
        --journal=*)
            JOURNALPATH="${1#--journal=}"
            echo "Journal activé. Fichier de journal: $JOURNALPATH"
            export SEP_JOURNAL_FILE="--journal-file $JOURNALPATH"
            shift
            ;;
        *)
            echo "Option inconnue: $1"
            shift
            ;;
        esac
    done
fi

# echo "Script: $SEP_SCRIPT_FILE"
# echo "Test: $SEP_MODE_TEST"
# echo "Debug: $SEP_MODE_DEBUG"
# echo "Log: $SEP_LOGFILE"
# echo "Journal: $SEP_JOURNAL_FILE"

# Activation de l'environnement virtuel si disponible
if [ -f ~/eclipse_env/bin/activate ]; then
    echo "Activation de l'environnement virtuel..."
    source ~/eclipse_env/bin/activate
fi

# Lancement du script principal
echo "Lancement du script principal..."
echo "Command: python3 ./main.py $SEP_SCRIPT_FILE $SEP_STRICT_MODE $SEP_MODE_TEST $SEP_MODE_DEBUG $SEP_LOGFILE $SEP_JOURNAL_FILE"
echo ""
echo "===================================="
sleep 1
python3 ./main.py $SEP_SCRIPT_FILE $SEP_STRICT_MODE $SEP_MODE_TEST $SEP_MODE_DEBUG $SEP_LOGFILE $SEP_JOURNAL_FILE

# Désactivation de l'environnement virtuel
if [ -n "$VIRTUAL_ENV" ]; then
    echo "Désactivation de l'environnement virtuel..."
    deactivate
fi

# Fin du script
