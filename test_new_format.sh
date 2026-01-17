#!/bin/bash
# Test rapide de réception UDP avec le nouveau format (ecg + bpm)

echo "🧪 TEST DE RÉCEPTION UDP - Format ECG + BPM"
echo "=========================================="
echo ""
echo "Ce script va envoyer des paquets de test au serveur"
echo ""

# Vérifier si nc est installé
if ! command -v nc &> /dev/null; then
    echo "❌ netcat (nc) n'est pas installé"
    echo "   Installez-le avec: sudo apt install netcat"
    exit 1
fi

echo "📡 Envoi de paquets de test vers localhost:3333..."
echo ""

# Paquet 1 - Toutes les données
echo "1️⃣  Paquet complet (ecg, bpm, accel):"
PACKET1='{"ecg":2450,"bpm":72,"x":0.145,"y":-0.023,"z":0.987}'
echo "   $PACKET1"
echo "$PACKET1" | nc -u -w1 localhost 3333
sleep 1

# Paquet 2 - Sans timestamp
echo ""
echo "2️⃣  Paquet sans timestamp:"
PACKET2='{"ecg":2500,"bpm":75,"x":0.1,"y":0.2,"z":1.0}'
echo "   $PACKET2"
echo "$PACKET2" | nc -u -w1 localhost 3333
sleep 1

# Paquet 3 - BPM invalide (trop haut)
echo ""
echo "3️⃣  Paquet avec BPM invalide (>180):"
PACKET3='{"ecg":2300,"bpm":200,"x":0,"y":0,"z":1}'
echo "   $PACKET3"
echo "$PACKET3" | nc -u -w1 localhost 3333
sleep 1

# Paquet 4 - Sans BPM
echo ""
echo "4️⃣  Paquet sans BPM:"
PACKET4='{"ecg":2600,"x":0.2,"y":-0.1,"z":0.95}'
echo "   $PACKET4"
echo "$PACKET4" | nc -u -w1 localhost 3333
sleep 1

# Paquet 5 - ECG uniquement
echo ""
echo "5️⃣  Paquet ECG uniquement:"
PACKET5='{"ecg":2700}'
echo "   $PACKET5"
echo "$PACKET5" | nc -u -w1 localhost 3333
sleep 1

echo ""
echo "=========================================="
echo "✅ 5 paquets de test envoyés !"
echo ""
echo "📊 Vérifiez dans l'interface web (http://localhost:5000)"
echo "   ou dans les logs du serveur que les données sont reçues."
echo ""
echo "Format attendu :"
echo '  {"ecg": 2450, "bpm": 72, "x": 0.1, "y": 0.2, "z": 1.0}'
echo ""
