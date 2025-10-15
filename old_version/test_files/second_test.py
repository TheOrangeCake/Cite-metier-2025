# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    second_test.py                                     :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: emurillo <emurillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2025/10/10 23:08:44 by emurillo          #+#    #+#              #
#    Updated: 2025/10/10 23:19:00 by emurillo         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import requests

API_TOKEN = "yTTpaBNjD-ojjc8koDh-L09f8THJX8xhHrxAjPQuOO1QLV8aKe60zkIP2QSNKGvef8sYZckbYlCw30Hl"
PRODUCT_ID = "105933"

url = f"https://api.infomaniak.com/1/ai/{PRODUCT_ID}/openai/chat/completions"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

data = {
    "model": "Qwen/Qwen3-Coder-480B-A35B-Instruct",
    "messages": [{"role": "system", "content": "You are a helpful assistant."},
                 {"role": "user", "content": "Hello"}],
    "temperature": 0.5
}

response = requests.post(url, headers=headers, json=data)
print(response.status_code)
print(response.text)
