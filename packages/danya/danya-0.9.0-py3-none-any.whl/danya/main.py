import requests
import importlib.resources
from .login import token

class Client:
    def __init__(self, model='gpt-5', reasoning_effort=None):
        self.url = 'http://5.35.46.26:10500/chat'
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.system_prompt = (
            'Всегда форматируй все формулы и символы в Unicode или ASCII. '
            'Не используй LaTeX или другие специальные вёрстки. '
            'В коде не пиши никаких комментариев. '
            'Пиши по-русски.'
        )

    def get_response(self, message):
        messages = [
            {'role': 'system', 'content': self.system_prompt},
            {'role': 'user',   'content': message}
        ]
        headers = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'
        }
        data = {
            'model': self.model,
            'messages': messages
        }
        if self.reasoning_effort is not None:
            data['reasoning_effort'] = self.reasoning_effort
        try:
            response = requests.post(self.url, headers=headers, json=data, timeout=600)
            response.raise_for_status()
            jr = response.json()
            return jr['choices'][0]['message']['content']
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error occurred: {e.response.status_code} - {e.response.text}")
            raise 
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raw_response = response.text if 'response' in locals() else "N/A"
            print(f"Raw response from server: {raw_response}")
            return f"Error processing request: {e}"

def read_txt_file(file_name):
    with importlib.resources.open_text('danya.data', file_name) as file:
        return file.read()

def ask(message, m=1):
    """
    Отправляет запрос к модели через сервер-прокси и возвращает ответ.

    Параметры:
        message (str): Текст запроса.
        m (int): Номер модели для использования:
            1 — gpt-5 no reasoning
            2 — gpt-5 medium reasoning
            3 — gpt-5 high reasoning
    Возвращает:
        str: Ответ модели.
    """
    config_map = {
        1: {'model': 'gpt-5', 'reasoning_effort': None},
        2: {'model': 'gpt-5', 'reasoning_effort': 'medium'},
        3: {'model': 'gpt-5', 'reasoning_effort': 'high'},

        # 1: {'model': 'gpt-4.1', 'reasoning_effort': None},
        # 2: {'model': 'o4-mini', 'reasoning_effort': 'medium'},
        # 3: {'model': 'o4-mini', 'reasoning_effort': 'high'},
        # 4: {'model': 'gemini-2.5-pro-preview-06-05', 'reasoning_effort': None},
    }
    config = config_map.get(m, config_map[1])
    client = Client(model=config['model'], reasoning_effort=config['reasoning_effort'])
    return client.get_response(message)

def get(a='м'):
    authors = {'а': 'artyom', 'д': 'danya', 'м': 'misha'}
    a = a.lower().replace('d', 'д').replace('a', 'а').replace('m', 'м')
    name = authors.get(a, 'misha') 
    return read_txt_file(f"{name}_dl.txt")