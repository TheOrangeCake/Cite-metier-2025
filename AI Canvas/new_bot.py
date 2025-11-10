import requests
import json
from config import API_TOKEN, BASE_URL, PRODUCT_ID, MODEL_CODE, MODEL_TEXT, CODER_PROMPT
from change_logger import get_logger

headers = {
	"Authorization": f"Bearer {API_TOKEN}",
	"Content-Type": "application/json"
}

def ask_ai_code(messages, only_explanation):
    data = {
        "model": MODEL_CODE,
        "messages": messages,
        "temperature": 0.4,
        "max_tokens": 2000,
        "stream": True
    }
    response = requests.post(BASE_URL, headers=headers, json=data, stream = True)
    if response.status_code != 200:
        print("❌ Error:", response.status_code, response.text)
        return "ERROR"

    final_text = ""
    buffer = ""
    explanation_sent = False
    explanation_text = ""

    for line in response.iter_lines():
        if not line:
            continue
        if line.startswith(b"data: "):
            content = line[len(b"data: "):].decode("utf-8")
            if content.strip() == "[DONE]":
                break
            try:
                data_json = json.loads(content)
                delta = data_json["choices"][0]["delta"]
                if "content" in delta:
                    text_part = delta["content"]
                    # print(text_part, end="", flush=True) 
                    final_text += text_part
                    buffer += text_part

                    if not explanation_sent and "#--Start--" in buffer:
                        parts = buffer.split("#--Start--", 1)
                        explanation_text += parts[0]
                        if only_explanation:
                            only_explanation(explanation_text.strip())
                        explanation_sent = True
                        buffer = "#--Start--" + parts[1]

                    # Send to logger to display while waiting
                    if explanation_sent:
                        get_logger().stream_code(text_part)

            except Exception as e:
                print(f"\n Stream parsing error: {e}")
                continue
    # print("\nStream completed.\n")
    return final_text.strip()

def AI_call(prompt, main, addon_path, q):
    code_to_send = get_logger().get_previous_content()

    message = [
    {
        "role": "system",
        "content": CODER_PROMPT
    },
    {
        "role": "user",
        "content": f"User request: {prompt}\nCode to edit:\n{code_to_send}\nMain file (context):\n{main}"
    }
    ]

    def handle_explanation(text):
        if q:
            q.put({"status": "explanation", "message": text})

    explanation = ask_ai_code(message, handle_explanation)
    if explanation == "ERROR":
        if q:
            q.put({"status": "error", "message": "La requête à l'IA a échoué."})
        return
    elif explanation == "INVALID":
        if q:
            q.put({"status": "error", "message": "Essayez de formuler une demande plus simple ou plus claire."})
        return
    elif explanation == "REJECTED":
        if q:
            q.put({"status": "error", "message": "Veuillez utiliser un langage respectueux."})
        return

    start_pos = explanation.find("#--Start--")
    end_pos = explanation.find("#--End--")
    if start_pos == -1 or end_pos == -1:
        if q:
            q.put({"status": "error", "message": "Format de code AI invalide"})
        return

    output = explanation[start_pos:end_pos + 8]
    if q:
        q.put({"status": "code", "output": output})
