import os
import subprocess
import telebot
import requests
import time

BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
ALLOWED_USER_IDS = list(map(int, os.environ['ALLOWED_USER_IDS'].split(',')))

bot = telebot.TeleBot(BOT_TOKEN)

def get_updates(offset):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {'offset': offset, 'timeout': 30}
    response = requests.get(url, params=params)
    return response.json()

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {'chat_id': chat_id, 'text': text}
    requests.post(url, params=params)

def handle_message(message):
    chat_id = message['chat']['id']
    user_id = message['from']['id']
    
    if user_id not in ALLOWED_USER_IDS:
        send_message(chat_id, "You are not authorized to use this bot.")
        return

    if 'text' not in message:
        send_message(chat_id, "Please send a text message with a command.")
        return

    text = message['text']

    try:
        result = subprocess.run(text, shell=True, check=True, capture_output=True, text=True, timeout=60)
        output = result.stdout or result.stderr
        if output:
            send_message(chat_id, output[:4096])  # Telegram message limit
        else:
            send_message(chat_id, "Command executed successfully with no output.")
    except subprocess.CalledProcessError as e:
        send_message(chat_id, f"Error: {e.stderr[:4096]}")
    except subprocess.TimeoutExpired:
        send_message(chat_id, "Command execution timed out after 60 seconds.")
    except Exception as e:
        send_message(chat_id, f"An error occurred: {str(e)[:4096]}")

# ... rest of your code ...

def main():
    offset = 0
    start_time = time.time()
    max_runtime = 270  # 4.5 minutes (to stay within GitHub Actions 5 minute limit)

    while time.time() - start_time < max_runtime:
        try:
            updates = get_updates(offset)
            for update in updates.get('result', []):
                offset = update['update_id'] + 1
                if 'message' in update:
                    handle_message(update['message'])
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        time.sleep(1)

if __name__ == '__main__':
    main()
