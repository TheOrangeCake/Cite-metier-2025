import requests
from config import API_TOKEN, BASE_URL, PRODUCT_ID, MODEL_CODE, MODEL_TEXT
from change_logger import get_logger

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def ask_ai_code(messages):
    data = {
        "model": MODEL_CODE,
        "messages": messages,
        "temperature": 0.4
    }
    response = requests.post(BASE_URL, headers=headers, json=data)
    if response.status_code != 200:
        print("❌ Error:", response.status_code, response.text)
        return "ERROR"

    return response.json()["choices"][0]["message"]["content"]


def ask_ai_text(messages):
    data = {
        "model": MODEL_TEXT,
        "messages": messages,
        "temperature": 0.7
    }
    response = requests.post(BASE_URL, headers=headers, json=data)
    if response.status_code != 200:
        print("❌ Error:", response.status_code, response.text)
        return "ERROR"

    return response.json()["choices"][0]["message"]["content"]



def conversation_moderation(prompt):
    if not prompt.strip():
        return {"status": "INVALID", "message": "You need to provide a valid text."}
    conversation_moderation = [
        {
            "role": "system", "content": 
            (
            "You are a moderation agent. "
            "If the message contains insults, hate speech, or vulgarity, reply ONLY with 'REJECTED'. "
            "If the message is safe but impossible (nonsense or dangerous), reply ONLY with 'INVALID'. "
            "If the message is too long, more than 200 characters, reply only 'INVALID'."
            "Otherwise reply ONLY with 'OK'."
            )
        },
        {
            "role": "user", "content": prompt 
        }
    ]

    result = ask_ai_text(conversation_moderation)
    if not result:
        return "ERROR"
    result = result.strip().upper()
    if "REJECTED" in result:
        return "REJECTED"
    elif "INVALID" in result:
        return "INVALID"
    elif "OK" in result:
         return "OK"


# ------------------- RESPONSE ANALYZER -------------------
def response_analizer(prompt, main):
    """Returns ONLY the text that should appear on screen."""
    status = conversation_moderation(prompt)

    # Rejected — stop here with a short message
    if status == "REJECTED":
        return {"status": "REJECTED", "message": "Please use respectful language so we can continue chatting."}

    # The current file to send
    code_to_send = get_logger().get_previous_content()
    
    # Otherwise, always generate an AI explanation (even if INVALID)
    explain_prompt = [
        {"role": "system", "content": (
            "You are a careful code editor. Given the Python file, apply the minimal editable changes to satisfy users's request"
            "Return ONLY the full updated file contents (valid Python). Do NOT include explanations or markdown."
        )},
        {"role": "user", "content": f"User request: {prompt}\nCode: {code_to_send}"}
    ]

    explanation = ask_ai_code(explain_prompt)
    if not explanation:
        explanation = "The assistant could not generate a response."

    start_pos = explanation.find("#--Start--")
    end_pos = explanation.find("#--End--")
    output = explanation[start_pos : end_pos + 8]
    with open('changes/addons.py', 'w') as file:
        file.write(output)
    
    return {"status": status, "message": explanation}