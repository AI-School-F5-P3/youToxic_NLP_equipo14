<img width="841" alt="YouTube_Watchdog_screenshot" src="https://github.com/user-attachments/assets/9f0d60c3-aa9a-4ea5-bd74-463392c5325e">

*GUI final de la aplicación: moderno e intuitivo*

# YouToxic NLP project - equipo 14 - codename: Watchdog 🐕
## La Moderación de Contenido en Crisis
- Volumen Masivo: Más de 500 horas de contenido subido por minuto
- Crecimiento Exponencial: Aumento del 40% en comentarios tóxicos
- Limitaciones Actuales:
  * Equipos de moderación sobrecargados
  * Costos operativos insostenibles
  * Imposibilidad de escalar manualmente

## El Impacto
- Deterioro de la experiencia del usuario
- Riesgo para la reputación de la plataforma
- Pérdida potencial de creadores de contenido

## La Solución: El Guardián de YouTube 🕵🏻‍♂️
Una aplicación que utiliza Inteligencia Artificial con 2 modelos de ML de tipo transformer, para:
- Detección Automática: Análisis en tiempo real de comentarios
- Clasificación Inmediata: Identificación instantánea de contenido tóxico
- Soporte de múltiples idiomas

Una versión Premium de suscripción que utiliza un modelo de Lenguaje LLM proporcionado por OpenAI:
- 100% de precisión en la clasificación

# Technical Setup Guide

## Prerequisitos
- Python 3.11 o superior
- Node.js y npm (para hacer correr el frontend)
- Docker (opcional, para un despliegue contenerizado)

## Estructura del Proyecto
```bash
📦 YOUTOXIC_NLP_EQUIPO14
┣ 📂 BACKEND 
┃ ┣ 📜 aux_db.py # Database operations 
┃ ┣ 📜 aux_openai.py # OpenAI integration 
┃ ┣ 📜 aux.py # Utility functions
┃ ┣ 📜 main.py # FastAPI main application 
┃ ┗ 📜 readme.md 
┣ 📂 docker-backend
┃ ┣ 📜 Dockerfile
┃ ┗ 📜 requirements.txt # To install dependencies
┣ 📂 FRONTEND 
┃ ┣ 📜 index.html # Landing page 
┃ ┣ 📜 premium.css
┃ ┣ 📜 premium.html # Premium features page 
┃ ┣ 📜 reports.css
┃ ┣ 📜 reports.html # Analytics reports 
┃ ┣ 📜 styles.css # Main stylesheet 
┃ ┣ 📜 youtube-scanner.css
┃ ┗ 📜 youtube-scanner.html # Page for scanning and analyzing YouTube comments 
┗ 📜 readme.md 
```

## Pasos para la Instalación

1. **Clonar el Repositorio**
```bash
git clone [repository-url]
cd YOUTOXIC_NLP_EQUIPO14
```

2. **Configuración del Backend**
```bash
cd BACKEND
python -m venv venv
source venv/bin/activate  # En Windows usa: venv\Scripts\activate
pip install -r ../docker-backend/requirements.txt
```

3. **Configuración del Entorno** Crea un archivo ```.env``` en el directorio BACKEND:
```bash
OPENAI_API_KEY=your_openai_api_key
```

4. **Inicialización de la Database**:
 La aplicación utiliza SQLite y creará de manera automática una database en ```BACKEND/DB/youtube_comments.db```

 5. **Ejecutar la Aplicación**:
    
    a. **Iniciar el Backend**
    ```bash
        cd BACKEND
        uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```

    b. **Servir el Frontend**: Utiliza cualquier servidor de archivos estático para servir el directorio FRONTEND. Por ejemplo:
    ```bash
        cd FRONTEND
        python -m http.server 8080
    ```

5. **Despliegue mediante Docker (Opcional)**
Para ejecutar el Backend en un contenedor:
```bash
cd docker-backend
docker build -t youtoxic-backend .
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key youtoxic-backend
```

**Uso**

1. Accede a la aplicación desde ```http://localhost:8080```
2. Usa el scanner para analizar los comentarios de un video de YouTube
3. Comprueba el análisis de los comentarios en la sección Reports
4. Accede a características premium a través de la integración con OpenAI

**API Endpoints**

- ```POST /scan_video```: Analiza comentarios en los videos usando modelos de ML
- ```POST /scan_video_openai```: Análisis Premium usando OpenAI
- ```POST /get_reports```: Genera informes de análisis
- ```POST /chat```: Funcionalidad de chatbot interactivo

**Advertencia**

Asegúrate de mantener confidencial tu clave API de OpenAI y nunca la envíes al control de versiones.


## El Equipo
<img width="198" alt="Jose_circular" src="https://github.com/user-attachments/assets/e4459802-97f9-4757-a47b-28a554ad4815">

| [José Antonio Rodríguez](https://github.com/joserodr68) |
|:---|
|Director de Desarrollo|
|Especialista en Machine Learning y Procesamiento de Lenguaje Natural|

<img width="197" alt="Captura de pantalla 2024-11-20 a las 0 45 56" src="https://github.com/user-attachments/assets/7193fa1f-f1d3-450b-a8cb-1451f16df7be">

| [Aitor Pérez](https://github.com/aitorph7) |
|:---|
|Experto en Análisis de Datos y Optimización de Plataformas|
|Especialista en soluciones escalables|

## Contribuciones

Si deseas contribuir a este proyecto, sigue estas pautas:

1. Crea un Fork del repositorio
2. Crea tu rama de funcionalidades ```git checkout -b feature/AmazingFeature```
3. Mantén los commits sencillos y con mensajes descriptivos
4. Asegúrate de que todo el código nuevo siga el estilo de codificación existente
5. Actualiza la documentación según sea necesario
6. Crea una solicitud de Pull Request que incluya una descripción detallada de tus cambios

### ¡Gracias por visitarnos!

Thank you for visiting our repository! We appreciate your interest in YouToxic NLP project. If you find this project useful, please consider giving it a star ⭐ and sharing it with others who might benefit from it.

For any questions or suggestions, feel free to open an issue or contact the team members directly.

¡Gracias por visitar nuestro repositorio! Agradecemos tu interés en el proyecto YouToxic NLP. Si este proyecto te resulta útil, agradeceremos que nos des una estrella ⭐ y lo compartas con otras personas que puedan beneficiarse de él.

Si tienes alguna pregunta o sugerencia, no dudes en abrir un Issue o comunícate directamente con los miembros del equipo.

---
Hecho con ❤️ por Equipo 14 - AI School F5 P3
