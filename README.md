````markdown
# Bot de Predicciones para X

Este es un bot automatizado para X (anteriormente Twitter) que responde a menciones con predicciones o respuestas analíticas y publica predicciones automáticas cada 6 horas sobre temas predefinidos. Utiliza SerpAPI para buscar información en internet, OpenAI para generar respuestas basadas en análisis y la API de X (v1.1 y v2) para interactuar con la plataforma.

## Características principales

* **Responde a menciones:** Analiza tweets que mencionan al bot y responde según el contexto (preguntas, solicitudes de predicción o mensajes genéricos).
* **Publicaciones automáticas:** Publica predicciones sobre temas específicos cada 6 horas.
* **Automatización clara:** Indica en su perfil y tweets que es un bot automatizado, cumpliendo con las políticas de X.

Este bot es ideal para quienes desean un perfil en X que ofrezca predicciones o análisis automatizados, como por ejemplo sobre política, economía o clima.

## Requisitos previos

Para usar este bot, necesitas lo siguiente:

### 1. Cuentas y claves API

* **X Developer Account:** Regístrate en el portal de desarrolladores de X para obtener:
    * `X_API_KEY`
    * `X_API_SECRET`
    * `X_ACCESS_TOKEN`
    * `X_ACCESS_TOKEN_SECRET`
    * `X_BEARER_TOKEN`
    Asegúrate de que tu app tenga permisos de `Read and Write`. **Importante:** Desde cambios recientes en la API de X, necesitarás un plan de acceso de pago (como el nivel Pro o superior) para poder publicar tweets a través de la API. El nivel gratuito tiene limitaciones severas o puede no permitir la publicación.
* **SerpAPI:** Crea una cuenta en SerpAPI para obtener una `SERPAPI_KEY`.
* **OpenAI:** Regístrate en OpenAI para obtener una `OPENAI_API_KEY`.

### 2. Dependencias de Python

Instala las siguientes librerías:

* `tweepy`: Para interactuar con la API de X.
* `openai`: Para generar respuestas con OpenAI.
* `serpapi`: Para búsquedas en internet.
* `python-dotenv`: Para manejar variables de entorno.
* `schedule`: Para programar publicaciones automáticas.

Ejecuta este comando para instalarlas:

```bash
pip install tweepy openai serpapi python-dotenv schedule
````

### 3\. Archivo .env

Crea un archivo `.env` en la raíz del proyecto con tus claves:

```
X_API_KEY=tu_api_key
X_API_SECRET=tu_api_secret
X_ACCESS_TOKEN=tu_access_token
X_ACCESS_TOKEN_SECRET=tu_access_token_secret
X_BEARER_TOKEN=tu_bearer_token
SERPAPI_KEY=tu_serpapi_key
OPENAI_API_KEY=tu_openai_api_key
```

## Configuración

### 1\. Configurar las claves API

Copia tus claves de X, SerpAPI y OpenAI en el archivo `.env` como se muestra arriba.

### 2\. Personalizar el bot

Edita estas variables en el código (`script.py`):

  * `BOT_USERNAME`: El handle de tu bot en X (por ejemplo, "accuracybot").
  * `CREATOR_NAME`: Tu handle de X (por ejemplo, "@laconchalalorav").
  * `PREDICTION_KEYWORDS`: Lista de palabras clave que activan respuestas de predicción (por ejemplo, `["predicción", "probabilidad", "chance"]`).

### 3\. Perfil del bot

Al iniciar, el bot actualiza automáticamente su descripción en X para indicar que es automatizado (por ejemplo, "Bot de predicciones. Automatizado por @laconchalalorav.").

## Funcionamiento del bot

### 1\. Respuestas a menciones

El bot monitorea menciones cada 60 segundos y responde según el contenido del tweet:

  * **Preguntas explícitas:** Si el tweet contiene un signo de interrogación (`?`), busca información con SerpAPI y genera una respuesta analítica con OpenAI.
  * **Palabras clave de predicción:** Si detecta palabras como "predicción" o "probabilidad" (definidas en `PREDICTION_KEYWORDS`), genera una predicción basada en el contexto.
  * **Otros casos:** Si no hay pregunta ni palabras clave, responde con un mensaje genérico pidiéndole al usuario que haga una pregunta o solicitud.

### 2\. Publicaciones automáticas

Cada 6 horas, el bot publica una predicción sobre uno de los temas predefinidos en la lista `temas` (por ejemplo, "¿Pierre Poilievre será elegido Primer Ministro de Canadá?"). Usa SerpAPI para buscar datos y OpenAI para generar la predicción.

### 3\. Interacción con APIs

  * **SerpAPI:** Busca información en Google y extrae fragmentos relevantes.
  * **OpenAI:** Analiza el contexto y genera respuestas breves (máximo 150 tokens) usando el modelo `gpt-3.5-turbo`.
  * **API de X:** Usa v1.1 para publicar tweets y actualizar el perfil, y v2 para buscar menciones.

## Personalización

Puedes adaptar el bot a tus necesidades modificando el código:

  * **Palabras clave:** Cambia `PREDICTION_KEYWORDS` para ajustar qué términos activan predicciones.
    ```python
    PREDICTION_KEYWORDS = ["forecast", "odds", "future"]
    ```
  * **Temas automáticos:** Edita la lista `temas` en `publicar_prediccion_automatica()` para cambiar los temas de las predicciones automáticas.
    ```python
    temas = ["Will AI take over the world?", "Will stocks rise next month?"]
    ```
  * **Frecuencia de publicaciones:** Modifica `schedule.every(6).hours` a otro intervalo (por ejemplo, `schedule.every(3).hours`).
  * **Modelo de OpenAI:** Cambia `"gpt-3.5-turbo"` a otro modelo como `"gpt-4"` si tienes acceso.
  * **Firma:** Ajusta el texto `"Automatizado por {CREATOR_NAME}"` en `responder_tweet` y `publicar_tweet`.

## Ejecución del bot

### 1\. Preparar el entorno

  * Asegúrate de que el archivo `.env` esté configurado.
  * Instala las dependencias con:
    ```bash
    pip install -r requirements.txt
    ```
  * Crea un archivo `requirements.txt` con:
    ```
    tweepy
    openai
    serpapi
    python-dotenv
    schedule
    ```

### 2\. Ejecutar el bot

  * Corre el script:
    ```bash
    python script.py
    ```
  * El bot:
      * Actualizará su perfil.
      * Publicará una predicción inicial.
      * Comenzará a monitorear menciones y publicar cada 6 horas.

### 3\. Mantenerlo activo

  * **Localmente:** Usa `nohup` para ejecutarlo en segundo plano (Linux/Mac):
    ```bash
    nohup python script.py &
    ```
  * **En la nube:** Despliega el bot en un servidor como Heroku, AWS o un VPS para mantenerlo siempre activo.

## Posibles mejoras

Aquí tienes ideas para extender el bot:

  * **Multilingüe:** Agrega soporte para otros idiomas modificando `PREDICTION_KEYWORDS` y los prompts de OpenAI.
  * **Análisis de sentimientos:** Usa OpenAI para detectar el tono de los tweets y ajustar las respuestas.
  * **Más fuentes de datos:** Integra APIs adicionales (clima, noticias, etc.) además de SerpAPI.
  * **Notificaciones:** Añade alertas por email si el bot falla (usa `smtplib`).
  * **Historial:** Guarda las predicciones en un archivo para análisis posterior.

## Notas importantes

  * **Plan de API de X requerido:** Para que el bot pueda publicar tweets, necesitarás suscribirte a un plan de pago de la API de X (como el nivel Pro o superior). El nivel gratuito actual tiene limitaciones muy estrictas o puede no permitir la publicación de tweets vía API. Revisa la [documentación oficial de la API de X](https://www.google.com/search?q=https://developer.twitter.com/en/docs/twitter-api/getting-started/about-twitter-api%23v2-access-level) para los detalles más recientes sobre los niveles de acceso.
  * **Límites de la API de X:** Incluso con planes de pago, existen límites de uso (cantidad de tweets, requests, etc.). Tenlos en cuenta para el funcionamiento continuo del bot.
  * **Costos:** SerpAPI y OpenAI generan costos según el uso. Monitorea tus límites y presupuestos para evitar sorpresas.
  * **Políticas de X:** Cumple con las reglas de automatización de X indicando claramente que es un bot en el perfil y/o en los tweets.

## Ejemplo de uso

Un usuario tuitea:

> @accuracybot ¿Lloverá esta tarde en Nueva York?

El bot responde:

> @usuario Basado en los datos actuales, hay un 60% de probabilidad de lluvia esta tarde en Nueva York. Automatizado por @laconchalalorav.

Publicación automática:

> Según análisis recientes, hay un 45% de probabilidad de que la economía mejore el próximo trimestre. \#Predicción \#Bot Automatizado por @laconchalalorav.

## Contribuciones

Si quieres mejorar este bot:

  * Haz un fork del repositorio.
  * Envía un pull request con tus cambios.
  * Reporta issues si encuentras errores o tienes ideas.

-----

Creado por @laconchalalorav

GitHub | X

```
```