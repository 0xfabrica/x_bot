import tweepy
import openai
import serpapi
import os
import time
import schedule
import re
from dotenv import load_dotenv
from datetime import datetime

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Configuración de las claves API
X_API_KEY = os.getenv("X_API_KEY")
X_API_SECRET = os.getenv("X_API_SECRET")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
X_BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")

# Configurar OpenAI
openai.api_key = OPENAI_API_KEY

# Configurar autenticación para X usando Tweepy (API v1.1 para publicación y actualización de perfil)
auth = tweepy.OAuthHandler(X_API_KEY, X_API_SECRET, X_BEARER_TOKEN)
auth.set_access_token(X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET)
auth.secure = True  # Asegurarse de que la conexión sea segura
api = tweepy.API(auth, wait_on_rate_limit=True)

# Configurar cliente para API v2 (para búsqueda de tweets)
bearer_token = os.getenv("X_BEARER_TOKEN")
client = tweepy.Client(
    bearer_token=bearer_token,
    consumer_key=X_API_KEY,
    consumer_secret=X_API_SECRET,
    access_token=X_ACCESS_TOKEN,
    access_token_secret=X_ACCESS_TOKEN_SECRET,
    wait_on_rate_limit=True
)

# Nombre del bot y del creador
BOT_USERNAME = "tu_usuario_bot"
CREATOR_NAME = "tu_nombre"  # Por ejemplo, "@MiUsuario"

# Lista de palabras clave para detectar temas de predicción
PREDICTION_KEYWORDS = ["predicción", "probabilidad", "chance", "ganará", "elected", "pierre poilievre"]

# Actualizar la descripción del perfil para indicar que es un bot automatizado
def actualizar_perfil():
    try:
        api.update_profile(description=f"Bot de predicciones. Automatizado por {CREATOR_NAME}.")
        print(f"Perfil actualizado: Bot de predicciones. Automatizado por {CREATOR_NAME}.")
    except Exception as e:
        print(f"Error al actualizar el perfil: {str(e)}")

# Función para buscar información en internet usando SerpAPI
def buscar_informacion(query):
    try:
        from serpapi import GoogleSearch
        params = {
            "q": query,
            "api_key": SERPAPI_KEY,
            "engine": "google"
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        snippets = [result.get("snippet") for result in results.get("organic_results", [])[:3]]
        return " ".join(snippets) if snippets else "No encontré información relevante."
    except Exception as e:
        print(f"Error al buscar con SerpAPI: {str(e)}")
        return "No pude encontrar información relevante en este momento."

# Función para generar una respuesta con OpenAI
def generar_respuesta(contexto, pregunta):
    prompt = f"Contexto: {contexto}\nPregunta: {pregunta}\nResponde de forma breve y analítica, como si fueras un bot de predicciones."
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un bot de predicciones analítico."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error al generar respuesta con OpenAI: {str(e)}")
        return "No pude generar una predicción en este momento."

# Función para responder a un tweet
def responder_tweet(tweet_id, texto_respuesta):
    try:
        texto_con_firma = f"{texto_respuesta}\nAutomatizado por {CREATOR_NAME}."
        if len(texto_con_firma) > 280:
            texto_con_firma = texto_con_firma[:277] + "..."
        api.update_status(status=texto_con_firma, in_reply_to_status_id=tweet_id, auto_populate_reply_metadata=True)
        print(f"Respondido al tweet {tweet_id}: {texto_con_firma}")
    except Exception as e:
        print(f"Error al responder al tweet {tweet_id}: {str(e)}")

# Función para publicar un tweet
def publicar_tweet(texto):
    try:
        texto_con_firma = f"{texto}\nAutomatizado por {CREATOR_NAME}."
        if len(texto_con_firma) > 280:
            texto_con_firma = texto_con_firma[:277] + "..."
        api.update_status(status=texto_con_firma)
        print(f"Tweet publicado: {texto_con_firma}")
    except Exception as e:
        print(f"Error al publicar tweet: {str(e)}")

# Función para determinar si un tweet es una pregunta
def es_pregunta(texto):
    return "?" in texto

# Función para detectar palabras clave de predicción
def contiene_palabras_clave(texto):
    texto = texto.lower()
    return any(keyword in texto for keyword in PREDICTION_KEYWORDS)

# Función para procesar un tweet y decidir cómo responder
def procesar_mencion(tweet):
    tweet_id = tweet.id
    pregunta = tweet.text.replace(f"@{BOT_USERNAME}", "").strip()
    username = client.get_user(id=tweet.author_id).data.username

    # Caso 1: Es una pregunta explícita
    if es_pregunta(pregunta):
        contexto = buscar_informacion(pregunta)
        respuesta = generar_respuesta(contexto, pregunta)
        respuesta_completa = f"@{username} {respuesta}"
        responder_tweet(tweet_id, respuesta_completa)

    # Caso 2: Contiene palabras clave relacionadas con predicciones
    elif contiene_palabras_clave(pregunta):
        contexto = buscar_informacion(pregunta)
        respuesta = generar_respuesta(contexto, f"¿Cuál es la probabilidad de que {pregunta}?")
        respuesta_completa = f"@{username} {respuesta}"
        responder_tweet(tweet_id, respuesta_completa)

    # Caso 3: No es una pregunta ni contiene palabras clave
    else:
        respuesta_completa = f"@{username} No estoy seguro de cómo ayudarte. ¿Puedes hacer una pregunta o pedirme una predicción?"
        responder_tweet(tweet_id, respuesta_completa)

# Función para buscar y procesar tweets recientes
def procesar_tweets():
    bot_id = client.get_me().data.id
    last_tweet_id = None

    while True:
        try:
            query = f"@{BOT_USERNAME} -from:{BOT_USERNAME}"
            tweets = client.search_recent_tweets(
                query=query,
                max_results=10,
                since_id=last_tweet_id,
                tweet_fields=["author_id", "created_at"],
                user_fields=["username"]
            )

            if tweets.data:
                for tweet in reversed(tweets.data):
                    if tweet.author_id == bot_id:
                        continue

                    print(f"Nuevo tweet recibido: {tweet.text}")
                    procesar_mencion(tweet)
                    last_tweet_id = tweet.id

            else:
                print("No se encontraron nuevos tweets.")

            time.sleep(60)

        except Exception as e:
            print(f"Error al procesar tweets: {str(e)}")
            time.sleep(60)

# Función para publicar predicciones automáticas
def publicar_prediccion_automatica():
    temas = [
        "Pierre Poilievre elected Canadian Prime Minister?",
        "Will the economy improve in the next quarter?",
        "Will it rain this afternoon in New York?"
    ]
    pregunta = temas[datetime.now().hour % len(temas)]  # Rotar temas según la hora
    contexto = buscar_informacion(pregunta)
    respuesta = generar_respuesta(contexto, pregunta)
    tweet = f"{respuesta} #Predicción #Bot"
    publicar_tweet(tweet)

# Programar publicaciones automáticas cada 6 horas
schedule.every(6).hours.do(publicar_prediccion_automatica)

# Función principal para mantener el bot vivo
def mantener_bot_vivo():
    actualizar_perfil()
    print(f"Iniciando bot @{BOT_USERNAME}...")

    # Publicar una predicción inicial al iniciar
    publicar_prediccion_automatica()

    while True:
        try:
            # Procesar tweets
            procesar_tweets()

            # Ejecutar tareas programadas (publicaciones automáticas)
            schedule.run_pending()

        except Exception as e:
            print(f"Error crítico en el bot: {str(e)}")
            time.sleep(300)  # Esperar 5 minutos antes de reintentar

if __name__ == "__main__":
    mantener_bot_vivo()