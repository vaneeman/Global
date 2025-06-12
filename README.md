# Asistente de Estudio para Aplicaciones IoT

## 📌 Descripción
Este sistema IoT funciona como asistente de estudio inteligente que:
- Detecta **ruido ambiental** (con KY-037) y alerta con un buzzer (KY-023) cuando supera niveles óptimos
- Monitorea **presencia de objetos/materiales** (con KY-010) usando el LED RGB (KY-016) como indicador visual
- Muestra datos en tiempo real en pantalla OLED mediante LVGL
- Registra históricos en PostgreSQL para análisis de patrones de estudio

## 🔧 Componentes

| Componente | Especificaciones | Cantidad | Función | Precio |
|-----------|------------------|----------|---------|--------|
| ESP32 | WiFi/Bluetooth, dual-core | 2 | Control principal | $150 c/u |
| KY-037 | Sensor de sonido | 1 | Detectar ruido ambiental | $41 |
| KY-010 | Fotointerruptor | 1 | Detectar libros/materiales | $35 |
| KY-023 | Buzzer | 1 | Alerta por exceso de ruido | $30 |
| KY-016 | LED RGB | 1 | Indicar color segun objeto detectado | $45 |


## 🛠 Software
- **PostgreSQL**: Guarda registros de:
  - Id del usuario
  - Id del sensor o actuador
  - Fecha
  - Valores detectados
    
- **Node-RED**: Programa:
  - Comunicación entre el código y la base de datos
  - Manejo de componentes
    
- **MQTT**: Programa
  -Comunicación entre los ESP32

- **Thonny**: Aplicación
  - Programación de los componentes

## ⚙️ Aplicaciones prácticas
1. **Tutor inteligente**: 
   - Vibra (buzzer) cuando detecta distracciones por ruido
   - LED avisa si faltan materiales sobre el escritorio

2. **Analizador de hábitos**:
   - Genera reportes de:
     - Horas productivas vs. ruidosas
     - Frecuencia de uso de materiales

3. **Control remoto**:
   - Desde Node-RED se puede:
     - Ajustar sensibilidad
     - Desactivar alarmas
     - Consultar datos históricos
    
4. **Flujos Node-Red**:
   - ![image](https://github.com/user-attachments/assets/3905cf11-3c4a-437e-bad3-fff6688fbabc)
  
   - ![image](https://github.com/user-attachments/assets/50ab4993-4220-4ec2-b70c-89e72382ac80)
  
5. **Diagramas de conexión**:
   - ![image](https://github.com/user-attachments/assets/e5d80c49-39d8-49a1-a385-08acc4f308df)
  
   - ![image](https://github.com/user-attachments/assets/d5f3d71c-7aab-4dba-9963-b7f0ef23f8a7)
  
6.  **Evidencias**:
   - https://drive.google.com/drive/folders/1X42RL7Pne7ViGDMH0zqVPKJQFgnzg1Ct?usp=drive_link
     





🔹 *Sistema desarrollado para la materia Aplicaciones IoT*
