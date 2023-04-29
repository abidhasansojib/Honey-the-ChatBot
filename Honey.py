import re
import openai
import random
import gradio as gr
import wolframalpha
import wikipedia
from custom_qa import get_custom_qa_pairs, jb
openai.api_key = "Your openai api key "
wolframalpha_app_id = "Wolfram alpha api key or app id"
qa_pairs = {
    "what is your name": "My name is Honey.",
}
qa_pairs.update(get_custom_qa_pairs())

text_engine_map = {
    "Low": "text-davinci-002",
    "Medium": "text-davinci-003",
}

def generate_response(prompt, engine):
    try:
        response = openai.Completion.create(
            engine=engine,
            prompt=prompt,
            temperature=0.5,
            max_tokens=1024,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def chatbot(message, mode):
    mode_message = ""
    while True:
        message = message.strip()
        if message == "exit":
            mode_message += "Goodbye!Have a great day."
            break
        elif message in qa_pairs:
            mode_message += qa_pairs[message]
        elif "tell me a bangla joke" in message:
        	mode_message += random.choice(jb)        
        elif mode == "Study":
            client = wolframalpha.Client(wolframalpha_app_id)
            res = client.query(message)
            if res["@success"] == "false":
                mode_message += "I couldn't find an answer to that question."
            else:
                mode_message += next(res.results).text
        elif mode == "Information":
            wikipedia.set_lang("en")
            try:
                mode_message += wikipedia.summary(message, sentences=3)
            except wikipedia.exceptions.PageError:
                mode_message += "I couldn't find any information about that."                
        else:
            engine = text_engine_map.get(mode, "text-davinci-002")
            prompt = f"Conversation with Honey:\n\nUser: {message}\nHoney:"
            response = generate_response(prompt, engine)
            mode_message += response
        
        mode_message += "\n\nEnter another question or type 'exit' to end conversation:"
        return mode_message
description = "Hey there!I am Honey.I am your friendly chatbot.I can answer your any questions.Try chatting with me by typing in the text box below!"

input_text = gr.inputs.Textbox(lines=2, label="Enter your massage here")
output_text = gr.outputs.Textbox(label="Honey's response")
mode_dropdown = gr.inputs.Dropdown(["Low", "Medium", "Study", "Information"], label="Select the mode you want to use",default="Low")

iface = gr.Interface(fn=chatbot, inputs=[input_text, mode_dropdown], outputs=output_text, title="Chat with Honey", description=description)
iface.launch()

