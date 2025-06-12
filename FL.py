import machine
import time
import network
import ubinascii
from umqtt.simple import MQTTClient
import ujson

# Configuración WiFi
WIFI_SSID = "INFINITUM0F58"
WIFI_PASSWORD = "xDtf3kf5zs"

# Configuración MQTT
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_CLIENT_ID = ubinascii.hexlify(machine.unique_id())
MQTT_TOPIC_FOTO = "sensor/fotointerruptor"
MQTT_TOPIC_LED = "actuador/led"

# Pines
PIN_FOTOINTERRUPTOR = 25
PIN_LED_R = 27
PIN_LED_G = 14
PIN_LED_B = 12

# Hardware
fotointerruptor = machine.Pin(PIN_FOTOINTERRUPTOR, machine.Pin.IN)
led_r = machine.PWM(machine.Pin(PIN_LED_R), freq=1000)
led_g = machine.PWM(machine.Pin(PIN_LED_G), freq=1000)
led_b = machine.PWM(machine.Pin(PIN_LED_B), freq=1000)

# Variables globales
ultimo_envio = 0
intervalo_envio = 5000  # 5 segundos
color_actual = {"r": 0, "g": 0, "b": 0}
modo_color = "normal"

# --- Función modificada con PWM INVERTIDO (para ánodo común) ---
def establecer_color_led(r, g, b):
    """Establece el color del LED RGB (sin inversión PWM para ánodo común)."""
    global color_actual
    
    # Conversión directa (0-255 a 0-1023) SIN INVERTIR
    r_pwm = int((r / 255) * 1023)
    g_pwm = int((g / 255) * 1023)
    b_pwm = int((b / 255) * 1023)
    
    # Aplicar PWM
    led_r.duty(r_pwm)
    led_g.duty(g_pwm)
    led_b.duty(b_pwm)
    
    color_actual = {"r": r, "g": g, "b": b}
    print(f"LED: R={r}, G={g}, B={b} (PWM: R={r_pwm}, G={g_pwm}, B={b_pwm})")

# --- Resto del código (sin cambios) ---
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Conectando WiFi...')
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        for _ in range(20):
            if wlan.isconnected():
                break
            time.sleep(0.5)
    if wlan.isconnected():
        print('WiFi OK! IP:', wlan.ifconfig()[0])
        return True
    else:
        print('Error WiFi')
        return False

def callback_mqtt(topic, msg):
    global modo_color
    try:
        payload = ujson.loads(msg)
        if "color" in payload:
            r = payload["color"].get("r", 0)
            g = payload["color"].get("g", 0)
            b = payload["color"].get("b", 0)
            establecer_color_led(r, g, b)
            modo_color = "custom"
        elif "mode" in payload:
            modo_color = payload["mode"]
            if modo_color == "concentracion":
                establecer_color_led(0, 255, 0)  # Verde
            elif modo_color == "descanso":
                establecer_color_led(0, 0, 255)  # Azul
            elif modo_color == "alerta":
                establecer_color_led(255, 0, 0)  # Rojo
            elif modo_color == "apagado":
                establecer_color_led(0, 0, 0)    # Apagar
    except Exception as e:
        print("Error MQTT:", e)

def leer_estado_fotointerruptor():
    return fotointerruptor.value()

def enviar_datos_fotointerruptor(client):
    global ultimo_envio
    try:
        valor = leer_estado_fotointerruptor()
        objeto_detectado = valor == 0
        client.publish(MQTT_TOPIC_FOTO, ujson.dumps({
            "value": valor,
            "object_detected": objeto_detectado,
            "is_optimal": objeto_detectado,
            "timestamp": time.time(),
            "led_status": color_actual
        }))
        print(f"Fotointerruptor: {valor} (Objeto: {objeto_detectado})")
        
        # Control automático del LED (si no está en modo custom)
        if modo_color != "custom":
            if objeto_detectado:
                establecer_color_led(0, 255, 0)  # Verde
            else:
                establecer_color_led(255, 165, 0) # Naranja
        return True
    except Exception as e:
        print("Error enviando datos:", e)
        return False

# --- Programa principal ---
if conectar_wifi():
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, MQTT_PORT)
        client.set_callback(callback_mqtt)
        client.connect()
        client.subscribe(MQTT_TOPIC_LED)
        print("MQTT conectado!")
        
        # Test inicial de LED (opcional)
        print("\n--- Prueba LED ---")
        establecer_color_led(255, 0, 0)   # Rojo
        time.sleep(1)
        establecer_color_led(0, 255, 0)   # Verde
        time.sleep(1)
        establecer_color_led(0, 0, 255)   # Azul
        time.sleep(1)
        establecer_color_led(0, 0, 0)     # Apagar
        print("--- Fin prueba ---\n")
        
        # Bucle principal
        while True:
            client.check_msg()
            ahora = time.ticks_ms()
            if time.ticks_diff(ahora, ultimo_envio) >= intervalo_envio:
                enviar_datos_fotointerruptor(client)
                ultimo_envio = ahora
            time.sleep_ms(100)
            
    except Exception as e:
        print("Error:", e)
        machine.reset()