<<<<<<< HEAD:test.py
# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    test.py                                            :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: emurillo <emurillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2025/10/10 19:23:55 by emurillo          #+#    #+#              #
#    Updated: 2025/10/10 23:22:01 by emurillo         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import requests

API_TOKEN = "yTTpaBNjD-ojjc8koDh-L09f8THJX8xhHrxAjPQuOO1QLV8aKe60zkIP2QSNKGvef8sYZckbYlCw30Hl"  # <-- replace with your Infomaniak token
PRODUCT_ID = "105933"
BASE_URL = f"https://api.infomaniak.com/1/ai/{PRODUCT_ID}/openai/chat/completions"

def talk_to_ai(message):
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "Qwen/Qwen3-Coder-480B-A35B-Instruct",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message}
        ],
        "temperature": 0.6
    }

    response = requests.post(BASE_URL, headers=headers, json=data)
    if response.status_code != 200:
        print("❌ Error:", response.status_code, response.text)
        return None

    content = response.json()["choices"][0]["message"]["content"]
    return content

def is_clean(text):
    bad_words = ["idiot", "stupid", "fuck", "shit"]
    for word in bad_words:
        if word in text.lower():
            return False
    return True

def main():
    print("💬 Type your message to the AI (or 'exit' to quit):\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break

        if not is_clean(user_input):
            print("🚫 Please use polite language.")
            continue

        ai_response = talk_to_ai(user_input)
        if ai_response and is_clean(ai_response):
            print(f"\n🤖 AI: {ai_response}\n")
        else:
            print("⚠️ The AI’s response was filtered.\n")

if __name__ == "__main__":
    main()
=======
# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    test.py                                            :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: emurillo <emurillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2025/10/10 19:23:55 by emurillo          #+#    #+#              #
#    Updated: 2025/10/11 09:34:40 by emurillo         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import requests

API_TOKEN = "yTTpaBNjD-ojjc8koDh-L09f8THJX8xhHrxAjPQuOO1QLV8aKe60zkIP2QSNKGvef8sYZckbYlCw30Hl"  # <-- replace with your Infomaniak token
PRODUCT_ID = "105933"
BASE_URL = f"https://api.infomaniak.com/1/ai/{PRODUCT_ID}/openai/chat/completions"

def talk_to_ai(message):
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "Qwen/Qwen3-Coder-480B-A35B-Instruct",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant. That will help people understand the code, they will modify \
            the code under certain restrictions by giving you a request, non code based, and after deciding if the changes are possible\
            you will return an explanation on why this is a good request or a unrealistic way of working. you will be working with teenagers\
            ages between 12-16, and maybe older."},
            {"role": "user", "content": message}
        ],
        "temperature": 0.6
    }

    response = requests.post(BASE_URL, headers=headers, json=data)
    if response.status_code != 200:
        print("❌ Error:", response.status_code, response.text)
        return None

    content = response.json()["choices"][0]["message"]["content"]
    return content

def is_clean(text):
    bad_words = ["idiot", "stupid", "fuck", "shit"]
    for word in bad_words:
        if word in text.lower():
            return False
    return True

def main():
    print("💬 Type your message to the AI (or 'exit' to quit):\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break

        if not is_clean(user_input):
            print("🚫 Please use polite language.")
            continue

        ai_response = talk_to_ai(user_input)
        if ai_response and is_clean(ai_response):
            print(f"\n🤖 AI: {ai_response}\n")
        else:
            print("⚠️ The AI’s response was filtered.\n")

if __name__ == "__main__":
    main()
>>>>>>> origin/emurillo:emurillo/test_files/test.py
