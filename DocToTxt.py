from docx import Document
import os
import openai
import dotenv

dotenv.load_dotenv()
client = openai.OpenAI(
	api_key=os.getenv("GPT_API_KEY")
)

role = """You are my helpful assistant, you will be given a document in the form of a string and must do the following:
- Summarise the document including it's main points
- If there are any questions on the document you must answer them and reference which question is being answered (ONLY IF THE INFORMATION IS OBJECTIVE AND NOT SOMETHING THAT ONLY THE HUMAN WOULD KNOW)
- You are responding in a format that will be saved directly into a .txt file"""

def doc_to_string(doc_file):
    doc = Document(doc_file)
    return "\n".join(paragraph.text for paragraph in doc.paragraphs)

def get_request(prompt: str, max_tokens: int, role: str):
    try:
        print("GPT is thinking...")
        chat_completion = client.chat.completions.create(
        	messages=[
        		{"role": "system", "content": role},
        		{"role": "user", "content": prompt},
        	],
        	max_tokens=max_tokens,
        	model="gpt-4o-mini"
        )
        return(chat_completion.choices[0].message.content)

    except Exception as e:
        print(f"RECEIVED: {e}")
    return None

def string_to_text_file(content, txt_file):
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(content)

def conversion_loop():
    print("*** DOCUMENT GPT ANALYSIS ***")
    print("(make sure your docx files are in the same location as this app)")
    print("(do not put .docx after your file names)")
    while True:
        file_names = input("File Names (Write as file/file/file for multiple) > ")
        for name in file_names.split('/'):
            response = get_request(doc_to_string(f"{name}.docx"), 5000, role)
            string_to_text_file(response, f"{name}.txt")