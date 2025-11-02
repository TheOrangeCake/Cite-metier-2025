import requests
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
		"temperature": 0.4
	}
	response = requests.post(BASE_URL, headers=headers, json=data)
	if response.status_code != 200:
		print("❌ Error:", response.status_code, response.text)
		return "ERROR"

	return response.json()["choices"][0]["message"]["content"]

def AI_call(prompt, main, addon_path):
    
    # get the current addons_file to send
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
    explanation = ask_ai_code(message)
    if not explanation:
        explanation = "The assistant could not generate a response."
    
    result = explanation.strip().upper()
    if result in ("INVALID", "REJECTED"):
        explanation = "Veuillez utiliser un langage respectueux." if result == "REJECTED" else "Essayez de formuler une demande plus simple ou plus claire"
        return {"status": result, "message": message}
    
    start_pos = explanation.find("#--Start--")
    end_pos = explanation.find("#--End--")
    output = explanation[start_pos : end_pos + 8]
    with open(addon_path, 'w') as file:
        file.write(output)
    return {"status": result, "message": explanation}