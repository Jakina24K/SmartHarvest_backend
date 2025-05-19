import re
import requests
import markdown2

def generate_content(model, version, api_key, text, systemInstruction = "" , responseMimeType = "text/plain" ):
    # responseMimeType = "text/plain" # "application/json"
    url = f"https://generativelanguage.googleapis.com/{version}/models/{model}:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "generationConfig": {
            "temperature": 1,
            "topP": 0.95,
            "topK": 64,
            "maxOutputTokens": 8192,
            "responseMimeType": responseMimeType
        },
        "safetySettings": [
            { "category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE" },
            { "category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE" },
            {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_NONE"
            },
            { "category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE" }
        ],
        "systemInstruction": {
            "role": "system",
            "parts": [
            {
                "text": systemInstruction
            }
            ]
        },
        "contents": [
            {
            "role": "user",
            "parts": [
                {
                "text": text
                }
            ]
            }
        ]
        }

    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise exception for non-2xx status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
 
def clean_markdown(markdown_string):
    # Convert Markdown to HTML
    html = markdown2.markdown(markdown_string)
    
    # Remove HTML tags to get plain text
    plain_text = re.sub(r'<.*?>', '', html)
    
    # Remove excessive newlines and spaces
    cleaned_text = re.sub(r'\n\s*\n', '\n\n', plain_text)
    
    # Remove code block backticks
    cleaned_text = re.sub(r'```', '', cleaned_text)
    
    # Remove Markdown list indicators
    cleaned_text = re.sub(r'^(\*|-|\d+\.)\s+', '', cleaned_text, flags=re.MULTILINE)
    
    return cleaned_text.strip()   

def clean_text(text):
    # Remove leading and trailing whitespace
    cleaned_text = text.strip()
    
    # Remove excessive newlines and spaces
    cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text)
    
    return cleaned_text


def process_generated_content(model, version, api_key, text, markdown = False):
    try:
        result = generate_content(model, version, api_key, text)
        if result and 'candidates' in result and result['candidates']:
            generated_content = result['candidates'][0]['content']['parts'][0]['text']
            cleaned_content = generated_content  if  markdown else clean_markdown(generated_content)
            return cleaned_content
        else:
            print("No valid response received from the API.")
            return None
    except Exception as e:
        print(f"Error occurred: {e} \n{result}")
        return None