import network
import time
from machine import Pin, ADC, PWM
from umqtt.simple import MQTTClient
import ujson
import gc

# Configuración de hardware
MIC_PIN = 34         # GPIO34 (ADC1_CH6)
BUZZER_PIN = 25      # GPIO25

# Configuración WiFi
WIFI_SSID = "INFINITUM0F58"
WIFI_PASSWORD = "xDtf3kf5zs"


# Configuración MQTT
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC_SENSOR = "noise_monitor/sensor_data"
MQTT_TOPIC_ACTUATOR = "noise_monitor/actuator_status"
MQTT_CLIENT_ID = "esp32_noise_monitor"

# Parámetros ajustables
CALIBRATION_SAMPLES = 100  # Muestras para calibración
NOISE_MULTIPLIER = 1.0     # Multiplicador del ruido base
MIN_THRESHOLD = 100      # Umbral mínimo absoluto
SAMPLE_INTERVAL = 0.5      # Intervalo entre lecturas

class NoiseMonitor:
    def __init__(self):
        # Inicializar hardware
        self.mic = ADC(Pin(MIC_PIN))
        self.mic.atten(ADC.ATTN_11DB)  # Rango completo 0-3.3V
        self.buzzer = PWM(Pin(BUZZER_PIN), freq=2000, duty=0)
        
        # Variables de estado
        self.baseline = 0
        self.threshold = MIN_THRESHOLD
        self.alarm_active = False
        
        # Calibración inicial
        self.calibrate()
        
        # Conectividad WiFi y MQTT
        self.wifi = network.WLAN(network.STA_IF)
        self.mqtt_client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, MQTT_PORT)
        self.connect_wifi()
        self.connect_mqtt()
    
    def connect_mqtt(self):
        """Conecta al broker MQTT"""
        try:
            self.mqtt_client.connect()
            print(f"📡 Conectado al broker MQTT: {MQTT_BROKER}")
        except Exception as e:
            print(f"❌ Error conectando a MQTT: {e}")
    
    def publish_data(self, topic, data):
        """Publica datos en el topic MQTT especificado"""
        try:
            self.mqtt_client.publish(topic, ujson.dumps(data))
        except Exception as e:
            print(f"❌ Error publicando en MQTT: {e}")
            # Intenta reconectar
            try:
                self.mqtt_client.connect()
            except:
                print("❌ No se pudo reconectar a MQTT")
    
    def calibrate(self):
        """Calibra el nivel de ruido ambiente"""
        print("\n🔧 Calibrando sensor... (Mantén silencio)")
        readings = []
        for i in range(CALIBRATION_SAMPLES):
            readings.append(self.mic.read())
            time.sleep_ms(50)
            if i % 20 == 0:
                print(".", end="")
        
        self.baseline = sum(readings) // CALIBRATION_SAMPLES
        noise_range = max(readings) - min(readings)
        self.threshold = max(int(self.baseline * NOISE_MULTIPLIER), MIN_THRESHOLD)
        
        print(f"\n✅ Calibrado: Base={self.baseline} | Umbral={self.threshold}")
    
    def connect_wifi(self):
        """Conecta a WiFi"""
        self.wifi.active(True)
        if not self.wifi.isconnected():
            print("\n📡 Conectando WiFi...")
            self.wifi.connect(WIFI_SSID, WIFI_PASSWORD)
            
            for _ in range(20):
                if self.wifi.isconnected():
                    break
                time.sleep(1)
        
        if self.wifi.isconnected():
            print(f"🌐 WiFi conectado: {self.wifi.ifconfig()[0]}")
    
    def read_noise(self, samples=100):
        """Lee el nivel de ruido con filtrado"""
        values = [self.mic.read() for _ in range(samples)]
        return {
            'avg': sum(values) // samples,
            'max': max(values),
            'min': min(values),
            'is_noisy': max(values) > self.threshold,
            'baseline': self.baseline,
            'threshold': self.threshold,
            'timestamp': time.time()
        }
    
    def trigger_alarm(self, state):
        """Controla el buzzer de manera persistente"""
        if state != self.alarm_active:  # Solo cambiar estado si es diferente
            self.alarm_active = state
            if state:
                self.buzzer.duty(512)  # Activar continuamente
                print("🚨 ¡ALARMA ACTIVADA! Ruido excesivo")
            else:
                self.buzzer.duty(0)    # Desactivar
                print("✅ Alarma desactivada")
            
            # Publicar estado del actuador
            self.publish_data(MQTT_TOPIC_ACTUATOR, {
                'alarm_active': state,
                'timestamp': time.time()
            })
    
    def run(self):
        print("\n=== MONITOR DE RUIDO (MODO PERSISTENTE) ===")
        print(f"Línea base: {self.baseline} | Umbral: {self.threshold}")
        print("(Presiona Ctrl+C para detener)\n")
        
        try:
            while True:
                noise = self.read_noise()
                
                # Publicar datos del sensor
                self.publish_data(MQTT_TOPIC_SENSOR, noise)
                
                # Mostrar valores
                status = "🔊" if noise['is_noisy'] else "🔇"
                print(f"{status} Avg:{noise['avg']:4d} Max:{noise['max']:4d}", end=' ')
                
                # Control de alarma persistente
                if noise['is_noisy']:
                    self.trigger_alarm(True)
                    print("| ¡Ruido excesivo continuo!")
                else:
                    self.trigger_alarm(False)
                    print("| Ambiente normal")
                
                time.sleep(SAMPLE_INTERVAL)
                gc.collect()
                
        except KeyboardInterrupt:
            self.trigger_alarm(False)
            print("\n🔴 Sistema detenido")
        finally:
            self.mqtt_client.disconnect()

# Ejecución
if __name__ == "__main__":
    monitor = NoiseMonitor()
    monitor.run()