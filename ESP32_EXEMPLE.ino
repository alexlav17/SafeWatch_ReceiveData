/*
 * Exemple de code ESP32 pour envoyer des données au Raspberry Pi
 * Compatible avec le serveur flask_app.py
 * 
 * Bibliothèques requises:
 * - WiFi (inclus dans ESP32)
 * - WiFiUdp (inclus dans ESP32)
 */

#include <WiFi.h>
#include <WiFiUdp.h>

// ===== CONFIGURATION WIFI =====
const char* ssid = "VOTRE_WIFI_SSID";
const char* password = "VOTRE_WIFI_PASSWORD";

// ===== CONFIGURATION RASPBERRY PI =====
const char* raspberryIP = "192.168.1.42";  // ⚠️ CHANGER AVEC L'IP DE VOTRE RASPBERRY PI
const uint16_t udpPort = 3333;

// ===== CONFIGURATION CAPTEURS =====
// Pins
const int ECG_PIN = 34;  // Pin ADC pour signal ECG (ADC1_CH6)
const int ACCEL_SDA = 21;   // I2C SDA pour accéléromètre
const int ACCEL_SCL = 22;   // I2C SCL pour accéléromètre

// Fréquence d'envoi
const unsigned long SEND_INTERVAL = 100;  // 100ms = 10Hz

// ===== VARIABLES GLOBALES =====
WiFiUDP udp;
unsigned long lastSendTime = 0;
unsigned long packetCount = 0;

// Simulations (à remplacer par de vraies lectures de capteurs)
float simAccelX = 0.0;
float simAccelY = 0.0;
float simAccelZ = 1.0;
int simECG = 2500;
int simBPM = 72;


void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n╔═══════════════════════════════════════════╗");
  Serial.println("║   ESP32 -> RASPBERRY PI SENDER           ║");
  Serial.println("╚═══════════════════════════════════════════╝\n");
  
  // Connexion WiFi
  Serial.printf("📡 Connexion au WiFi: %s\n", ssid);
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi connecté!");
    Serial.printf("   IP ESP32: %s\n", WiFi.localIP().toString().c_str());
    Serial.printf("   IP Raspberry: %s\n", raspberryIP);
    Serial.printf("   Port UDP: %d\n\n", udpPort);
    
    // Démarrer UDP
    udp.begin(udpPort);
    Serial.println("✅ UDP initialisé");
    Serial.printf("⏱️  Fréquence d'envoi: %d Hz\n\n", 1000 / SEND_INTERVAL);
    Serial.println("═══════════════════════════════════════════\n");
  } else {
    Serial.println("\n❌ Échec de connexion WiFi!");
    Serial.println("   Vérifiez vos identifiants et redémarrez l'ESP32");
  }
  
  // Initialiser les pins ADC
  analogReadResolution(12);  // 12-bit ADC (0-4095)
  pinMode(ECG_PIN, INPUT);
  
  // TODO: Initialiser l'accéléromètre I2C ici
  // Wire.begin(ACCEL_SDA, ACCEL_SCL);
  // accelerometer.begin();
}


void loop() {
  unsigned long currentTime = millis();
  
  // Envoyer les données toutes les 100ms (10Hz)
  if (currentTime - lastSendTime >= SEND_INTERVAL) {
    lastSendTime = currentTime;
    
    // Lire les capteurs
    readSensors();
    
    // Créer et envoyer le paquet JSON
    sendDataPacket();
  }
}


void readSensors() {
  // ===== SIGNAL ECG =====
  // Lire l'ADC (0-4095, 12-bit)
  int rawECG = analogRead(ECG_PIN);
  
  // Utiliser la valeur brute directement (pas de mapping)
  simECG = rawECG;
  
  // TODO: Calculer le BPM à partir du signal ECG
  // Pour l'instant, simulation avec variation aléatoire
  simBPM = 60 + random(-5, 5);
  
  
  // ===== ACCÉLÉROMÈTRE =====
  // TODO: Lire l'accéléromètre réel (ex: ADXL345, MPU6050)
  // Pour l'instant, simulation d'un mouvement sinusoïdal
  float t = millis() / 1000.0;
  simAccelX = 0.5 * sin(t * 2.0);
  simAccelY = 0.3 * cos(t * 1.5);
  simAccelZ = 1.0 + 0.1 * sin(t);
  
  // Limiter à ±2g
  simAccelX = constrain(simAccelX, -2.0, 2.0);
  simAccelY = constrain(simAccelY, -2.0, 2.0);
  simAccelZ = constrain(simAccelZ, -2.0, 2.0);
}


void sendDataPacket() {
  // Créer le timestamp ISO 8601
  char timestamp[30];
  unsigned long seconds = millis() / 1000;
  unsigned long ms = millis() % 1000;
  sprintf(timestamp, "2026-01-14T%02lu:%02lu:%02lu.%03luZ", 
          (seconds / 3600) % 24, 
          (seconds / 60) % 60, 
          seconds % 60, 
          ms);
  
  // Créer le JSON
  String json = "{";
  json += "\"timestamp\":\"" + String(timestamp) + "\",";
  json += "\"ecg\":" + String(simECG) + ",";
  json += "\"bpm\":" + String(simBPM) + ",";
  json += "\"x\":" + String(simAccelX, 3) + ",";
  json += "\"y\":" + String(simAccelY, 3) + ",";
  json += "\"z\":" + String(simAccelZ, 3);
  json += "}";
  
  // Envoyer via UDP
  udp.beginPacket(raspberryIP, udpPort);
  udp.print(json);
  int result = udp.endPacket();
  
  packetCount++;
  
  // Afficher dans le Serial toutes les 10 paquets
  if (packetCount % 10 == 0) {
    Serial.printf("[%05lu] ", packetCount);
    Serial.printf("❤️ BPM:%3d | 📊 ECG:%4d | ", simBPM, simECG);
    Serial.printf("📐 X:%6.3f Y:%6.3f Z:%6.3f | ", simAccelX, simAccelY, simAccelZ);
    Serial.printf("%s\n", result ? "✅" : "❌");
  }
  
  // Afficher le JSON complet toutes les 50 paquets
  if (packetCount % 50 == 0) {
    Serial.println("\n📦 Paquet JSON:");
    Serial.println(json);
    Serial.println();
  }
}


// ===== FONCTIONS POUR VRAIS CAPTEURS =====

/*
 * Exemple pour MAX30102 (capteur cardiaque/SpO2)
 * 
 * #include "MAX30105.h"
 * MAX30105 particleSensor;
 * 
 * void setupHeartSensor() {
 *   if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) {
 *     Serial.println("MAX30105 non trouvé!");
 *   }
 *   particleSensor.setup();
 * }
 * 
 * int readHeartSignal() {
 *   return particleSensor.getIR();  // Lecture IR
 * }
 */


/*
 * Exemple pour ADXL345 (accéléromètre)
 * 
 * #include <Wire.h>
 * #include <Adafruit_ADXL345_U.h>
 * Adafruit_ADXL345_Unified accel = Adafruit_ADXL345_Unified(12345);
 * 
 * void setupAccelerometer() {
 *   if(!accel.begin()) {
 *     Serial.println("ADXL345 non trouvé!");
 *   }
 *   accel.setRange(ADXL345_RANGE_2_G);
 * }
 * 
 * void readAccelerometer(float &x, float &y, float &z) {
 *   sensors_event_t event;
 *   accel.getEvent(&event);
 *   x = event.acceleration.x / 9.81;  // Convertir en g
 *   y = event.acceleration.y / 9.81;
 *   z = event.acceleration.z / 9.81;
 * }
 */


/*
 * Exemple pour MPU6050 (accéléromètre + gyroscope)
 * 
 * #include <Wire.h>
 * #include <MPU6050.h>
 * MPU6050 mpu;
 * 
 * void setupMPU6050() {
 *   Wire.begin();
 *   mpu.initialize();
 *   if (!mpu.testConnection()) {
 *     Serial.println("MPU6050 non trouvé!");
 *   }
 * }
 * 
 * void readMPU6050(float &x, float &y, float &z) {
 *   int16_t ax, ay, az;
 *   mpu.getAcceleration(&ax, &ay, &az);
 *   x = ax / 16384.0;  // Convertir en g (±2g range)
 *   y = ay / 16384.0;
 *   z = az / 16384.0;
 * }
 */
