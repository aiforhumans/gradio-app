import gradio as gr
import openai
import json
import os

# Configure OpenAI to use the local LM Studio server
openai.api_base = "http://localhost:1234/v1"
openai.api_key = "not-needed"

# Global variable to store the system message
system_message = "You are a helpful assistant."

def predict(message, history):
    global system_message
    history_openai_format = [{"role": "system", "content": system_message}]
    for human, assistant in history:
        history_openai_format.append({"role": "user", "content": human})
        history_openai_format.append({"role": "assistant", "content": assistant})
    history_openai_format.append({"role": "user", "content": message})

    response = openai.ChatCompletion.create(
        model="local-model",  # This field is ignored by LM Studio but still required
        messages=history_openai_format,
        temperature=0.7,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    return response.choices[0].message.content

def generate_wpp_format(char_name, nickname, species, age, features, body, mind, personality, loves, hates, description):
    wpp_format = f"""[character("{char_name}")
{{
Nickname("{nickname}")
Species("{species}")
Age("{age}")
Features("{features}")
Body("{body}")
Mind("{mind}")
Personality("{personality}")
Loves("{loves}")
Hates("{hates}")
Description("{description}")
}}]"""
    return wpp_format

def save_character(char_name, nickname, species, age, features, body, mind, personality, loves, hates, description):
    global system_message
    system_message = generate_wpp_format(char_name, nickname, species, age, features, body, mind, personality, loves, hates, description)
    with open("character_data.json", "w") as f:
        json.dump({
            "char_name": char_name,
            "nickname": nickname,
            "species": species,
            "age": age,
            "features": features,
            "body": body,
            "mind": mind,
            "personality": personality,
            "loves": loves,
            "hates": hates,
            "description": description
        }, f)
    return "Character saved successfully!"

def load_character():
    global system_message
    if os.path.exists("character_data.json"):
        with open("character_data.json", "r") as f:
            data = json.load(f)
        system_message = generate_wpp_format(**data)
        return list(data.values())
    return [""] * 11  # Return empty strings if no data is found

# Create the tabbed interface
with gr.Blocks() as demo:
    with gr.Tabs():
        with gr.TabItem("Chat"):
            chatbot = gr.Chatbot(height=600)
            msg = gr.Textbox()
            clear = gr.Button("Clear")

            def user(user_message, history):
                return "", history + [[user_message, None]]

            def bot(history):
                bot_message = predict(history[-1][0], history[:-1])
                history[-1][1] = bot_message
                return history

            msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
                bot, chatbot, chatbot
            )
            clear.click(lambda: None, None, chatbot, queue=False)

        with gr.TabItem("Settings"):
            gr.Markdown("# Character Settings")
            char_name = gr.Textbox(label="Character Name")
            nickname = gr.Textbox(label="Nickname")
            species = gr.Textbox(label="Species")
            age = gr.Textbox(label="Age")
            features = gr.Textbox(label="Features")
            body = gr.Textbox(label="Body")
            mind = gr.Textbox(label="Mind")
            personality = gr.Textbox(label="Personality")
            loves = gr.Textbox(label="Loves")
            hates = gr.Textbox(label="Hates")
            description = gr.Textbox(label="Description", lines=5)
            
            save_button = gr.Button("Save Character")
            load_button = gr.Button("Load Character")
            result = gr.Textbox(label="Result")

            save_button.click(save_character, 
                              inputs=[char_name, nickname, species, age, features, body, mind, personality, loves, hates, description], 
                              outputs=result)
            load_button.click(load_character, 
                              outputs=[char_name, nickname, species, age, features, body, mind, personality, loves, hates, description])

demo.launch()