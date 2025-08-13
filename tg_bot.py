import os
import requests
import json
import wikipedia as wiki
wiki.set_lang("ru")

latest_updates = 0
BOT_TOKEN = "8459199288:AAF1Lwnv77d7VvEd1HMcYZP6Qhz38vGghQo"
DOWNLOAD_FOLDER = os.path.join(os.path.expanduser('~'), 'Downloads')

def get_weather(city):
    try:
        url = f"https://wttr.in/{city}?format=%C+%t+%w+%h&lang=ru"
        response = requests.get(url)
        if response.status_code == 200:
            weather_data = response.text.split()
            if len(weather_data) >= 3:
                condition = weather_data[0]
                temp = weather_data[1]
                wind = weather_data[2]
                humidity = weather_data[3] if len(weather_data) > 3 else "N/A"
                return (f"Weather in {city}:\n"
                        f"State: {condition}\n"
                        f"Temperature: {temp}\n"
                        f"Wind: {wind}\n"
                        f"Humidity: {humidity}")
        return "Failed to retrieve weather data"
    except Exception as e:
        print(f"Error while getting weather: {e}")
        return "Error retrieving weather data"

def count_files_in_downloads():
    try:
        files = [f for f in os.listdir(DOWNLOAD_FOLDER) if os.path.isfile(os.path.join(DOWNLOAD_FOLDER, f))]
        return f"In the downloads folder {len(files)} files"
    except Exception as e:
        print(f"Error while counting files: {e}")
        return "Failed to check download folder"

def delete_file(filename):
    try:
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return f"File '{filename}' successfully removed"
        return f"File '{filename}' not found"
    except Exception as e:
        print(f"Error deleting file: {e}")
        return f"Error deleting file '{filename}'"

def get_updates():
    global latest_updates
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {'offset': latest_updates}
    
    try:
        response = requests.get(url, params=params)
        updates = response.json()
        result = updates.get('result', [])
        
        if not result:
            return

        for update in result:
            latest_updates = update['update_id'] + 1
            message = update.get('message', {})
            chat_id = message.get('from', {}).get('id')
            first_name = message.get('from', {}).get('first_name', 'user')
            text = str(message.get('text', '')).lower().strip()
            
            if not text or not chat_id:
                continue

            response_text = ""
            
            if text == 'Hello':
                response_text = f'Hello, {first_name}!'
            elif text in ['How are you?', 'How are you']:
                response_text = "I'm doing great! And you?"
            elif text.startswith('weather'):
                city = text.replace('weather', '').strip()
                if city:
                    response_text = get_weather(city)
                else:
                    response_text = "Specify the city after the command, for example: 'weather Almaty'"
            elif text in ['how many files', 'files']:
                response_text = count_files_in_downloads()
            elif text.startswith('delete file'):
                filename = text.replace('delete file', '').strip()
                if filename:
                    response_text = delete_file(filename)
                else:
                    response_text = "Specify the file name, for example: 'delete file document.pdf'"
            elif text.startswith('tell me about'):
                query = text.replace('tell me about', '').strip()
                if query:
                    try:
                        wiki_result = wiki.summary(query, sentences=2)
                        response_text = wiki_result
                    except:
                        response_text = 'I did not find information for this request'
                else:
                    response_text = "Please specify a topic, for example: 'tell me about Python'"
            elif text == 'teams':
                response_text = ("Available commands:\n"
                                "Hello - Greeting\n"
                                "How are you - Find out my status\n"
                                "weather [city] - Check the weather\n"
                                "how many files - Count files in downloads\n"
                                "delete file [name] - Delete file\n"
                                "tell me about [topic] - Wikipedia Search")
            else:
                response_text = "I didn't understand the command. Type 'commands' for a list of available commands."
            
            send_message(chat_id, response_text)
            
    except Exception as e:
        print(f"Error in get_updates: {e}")

def send_message(chat_id, text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        params = {'chat_id': chat_id, 'text': text}
        requests.get(url, params=params)
    except Exception as e:
        print(f"Error sending message: {e}")

if __name__ == '__main__':
    print("The bot has been launched")
    while True:
        get_updates()