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

# Technical Setup Guide 🇬🇧

## Prerequisites
- Python 3.11 or higher
- Node.js and npm (for running the frontend)
- Docker (optional, for containerized deployment)

## Project Structure
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

## Installation Steps

1. **Clone the Repository**
```bash
git clone [repository-url]
cd YOUTOXIC_NLP_EQUIPO14
```

2. **Backend Setup**
```bash
cd BACKEND
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r ../docker-backend/requirements.txt
```

3. **Environment Configuration** Create a ```.env``` file in the BACKEND directory:
```bash
OPENAI_API_KEY=your_openai_api_key
```

4. **Database Initialization**:
 The application uses SQLite and will automatically create a database at ```BACKEND/DB/youtube_comments.db```

 5. **Running the Application**:
    
    a. **Start the Backend**
    ```bash
        cd BACKEND
        uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```

    b. **Serve the Frontend**: Use any static file server to serve the FRONTEND directory. For example:
    ```bash
        cd FRONTEND
        python -m http.server 8080
    ```

5. **Docker Deployment (Optional)**
To run the backend in a container:
```bash
cd docker-backend
docker build -t youtoxic-backend .
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key youtoxic-backend
```

**Usage**

1. Access the application at ```http://localhost:8080```
2. Use the Scanner to analyze YouTube video comments
3. View analytics in the Reports section
4. Access premium features with OpenAI integration

**API Endpoints**

- ```POST /scan_video```: Analyze video comments using ML models
- ```POST /scan_video_openai```: Premium analysis using OpenAI
- ```POST /get_reports```: Generate analysis reports
- ```POST /chat```: Interactive chat functionality

**Note**

Make sure to keep your OpenAI API key confidential and never commit it to version control.




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


