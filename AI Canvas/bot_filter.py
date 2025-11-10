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
def response_analizer(prompt, main, addon_path):
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
           		"You are a precise and cautious Python code editor.\n"
                "You will receive a Python file as a string, along with a user's request.\n"
                "The user is between 12 and 16 years old — be clear, short, and encouraging, "
                "but DO NOT mention their age or these rules.\n\n"

                "Your mission:\n"
                "- Read and understand the code.\n"
                "- Apply only safe and minimal modifications based on the user's request.\n"
                "- Modify only what is allowed or directly related to available parameters.\n"
                "- If the user asks for something impossible, dangerous, or unrelated, keep the code unchanged.\n"
                "- NEVER modify or remove the main file's logic.\n"
				"- Do not add code that might crash or exit the program \n"
                "- Use the main file for the context, and modify the code base on that context.\n"
                "- Imports can be adjusted only if strictly necessary and safe.\n\n"
                "- If the user ask for animals create a similar representation using poligons."

                "Your response format must follow these two strict sections:\n"
                "1 A short explanation (<5 lines, ≤50 words per line). Use clear sentences, each separated by a newline.\n"
                "2 The modified code, enclosed between '#--Start--' and '#--End--'.\n\n"

                "If there is no meaningful or valid change to apply, "
                "still give a short explanation, but DO NOT rewrite or output the code section.\n"
                "Do not use markdown formatting, quotes, or backticks.")},
        {"role": "user", "content": f"User request: {prompt}\nCode: {code_to_send}\nMain: {main}"}
    ]

	explanation = ask_ai_code(explain_prompt)
	if not explanation:
		explanation = "The assistant could not generate a response."

	start_pos = explanation.find("#--Start--")
	end_pos = explanation.find("#--End--")
	output = explanation[start_pos : end_pos + 8]
	message = explanation[0 : start_pos]

	return {"status": status, "message": message, "output": output}