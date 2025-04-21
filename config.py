from dotenv import load_dotenv
import os

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
AVITO_LOGIN = os.getenv('AVITO_LOGIN')
AVITO_PASSWORD = os.getenv('AVITO_PASSWORD')

AVITO_PROFILE_URL = "https://www.avito.ru/profile"
AVITO_MESSENGER_URL = "https://www.avito.ru/profile/messenger"
CHAT_ID = 895828653