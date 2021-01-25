import requests
import json
import pyttsx3
import speech_recognition as sr
import re
import threading
import time

API_KEY = "tBNQv3O-OvMg"
PROJECT_TOKEN = "tnjT50jkKT2T"
RUN_TOKEN = "tX8SCBy6g_yJ"


class Data:
    def __init__(self, api_key, project_token):
        self.api_key = api_key
        self.project_token = project_token
        self.params = {
            "api_key": self.api_key
        }
        self.data = self.get_data()

    def get_data(self):
        r = requests.get(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/last_ready_run/data', params=self.params)
        data = json.loads(r.text)
        return data

    def get_total_cases(self):
        data = self.data['total']
        for content in data:
            if content['name'] == "Coronavirus Cases:":
                return content['value']

    def get_total_deaths(self):
        data = self.data['total']
        for content in data:
            if content['name'] == "Deaths:":
                return content['value']
        return "0"

    def get_country_data(self, country):
        data = self.data["country"]
        for content in data:
            if content['name'].lower() == country.lower():
                return content
        return "0"

    def get_list_of_coutries(self):
        countries = []
        for country in self.data['country']:
            countries.append(country['name'].lower())
        return countries

    def update_data(self):
        self.r = requests.post(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/run', params=self.params)
        # data = json.loads(r.text)
        # return data

        def poll():
            # pass
            time.sleep(0.1)
            old_data = self.data
            while True:
                new_data = self.get_data()
                if new_data != old_data:
                    self.data = new_data
                    # print("Data Updated")
                    break
                time.sleep(1)

        t = threading.Thread(target=poll)
        t.start()

# print(data.get_list_of_coutries())
# print("Total Covid19 cases in India are: ", data.get_country_data('india')['total_cases'])

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# speak("hello")

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
            # print(said)
        except:
            print("Unknown Command")
    return said.lower()

# print(get_audio())

def main():
    print("Started program")
    data = Data(API_KEY, PROJECT_TOKEN)
    END_PHRASE = "exit"
    country_list = data.get_list_of_coutries()

    TOTAL_PATTERNS = {
                    re.compile(r"[\w\s]+ total [\w\s]+ cases$"):data.get_total_cases,
                    re.compile(r"[\w\s]+ total cases$"):data.get_total_cases,
                    re.compile(r"[\w\s]+ total [\w\s]+ death$"):data.get_total_deaths,
                    re.compile(r"[\w\s]+ total death$"):data.get_total_deaths
                    }

    COUNTRY_PATTERNS = {
                    re.compile(r"number of total cases [\w\s]+"): lambda country: data.get_country_data(country)['total_cases'],
                    re.compile(r"number of total death cases [\w\s]+"): lambda country: data.get_country_data(country)['total_deaths']
                    }

    UPDATE_COMMAND = "update"
    

    while True:
        print("Listening...")
        text = get_audio()
        print(text)
        result = None

        for pattern, func in COUNTRY_PATTERNS.items():
            if pattern.match(text):
                words = set(text.split(" "))
                for country in country_list:
                    if country in words:
                        result = func(country)
                        break

        for pattern, func in TOTAL_PATTERNS.items():
            if pattern.match(text):
                result = func()
                break
        
        if text == UPDATE_COMMAND:
            result = "Data is being updated. Please wait a moment!"
            print("Data Updated")
            data.update_data()
        

        if result:
            print(result)
            speak(result)

        if text.find(END_PHRASE) != -1:
            print("Exiting Program")
            break

main()