import requests
import json
from config import API_TOKEN, BASE_URL, PRODUCT_ID, MODEL_CODE, MODEL_TEXT, CODER_PROMPT
from change_logger import get_logger

headers = {
	"Authorization": f"Bearer {API_TOKEN}",
	"Content-Type": "application/json"
}

def ask_ai_code(messages):
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
                    print(text_part, end="", flush=True) 
                    final_text += text_part
            except Exception as e:
                print(f"\n Stream parsing error: {e}")
                continue
    print("\nStream completed.\n")
    return final_text.strip()
    

def AI_call(prompt, main, addon_path):
    
    # get the current addons_file to send
    code_to_send = get_logger().get_previous_content()
    
    output = ""
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
    explanation = ask_ai_code(message)
    if not explanation:
        explanation = "The assistant could not generate a response."
    
    result = explanation.strip()
    if result in ("INVALID", "REJECTED"):
        explanation = "Veuillez utiliser un langage respectueux." if result == "REJECTED" else "Essayez de formuler une demande plus simple ou plus claire"
        return {"status": result, "message": explanation, "output": output}
    
    start_pos = explanation.find("#--Start--")
    end_pos = explanation.find("#--End--")
    if start_pos == -1 or end_pos == -1:
        print("Missing '#--Start--' flag or Missing '#--End--' flag")
        result = "INVALID"
        explanation = "Le code généré par AI n'est pas correct"
        return {"status": result, "message": explanation, "output": output}
    # if start_pos == -1 or end_pos == -1:
    #     print("Missing '#--start-- or '#--End--' tags in file'")
    #     return {"status":"ERROR", "message": explanation}
    output = explanation[start_pos:end_pos + 8]
    if not output:
        result = "INVALID"
        explanation = "Le code généré par AI n'est pas correct"
        print("Missing output")
    return {"status": result, "message": explanation, "output": output}