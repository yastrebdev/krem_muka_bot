chat_store = {}  # {chat_id: avito_chat_url}

def add_chat(chat_id: str, url: str):
    chat_store[chat_id] = url

def get_chat_url(chat_id: str):
    return chat_store.get(chat_id)