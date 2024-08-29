import gradio as gr
import requests
import json

# LM Studio API endpoint
API_URL = "http://localhost:1234/v1/chat/completions"

def get_models():
    response = requests.get("http://localhost:1234/v1/models")
    if response.status_code == 200:
        models = response.json()
        return [model["id"] for model in models["data"]]
    else:
        return ["Error fetching models"]

def load_character():
    try:
        with open("character.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"name": "", "age": "", "gender": "", "personality_traits": "", "description": ""}

def save_character(name, age, gender, personality_traits, description):
    character = {
        "name": name,
        "age": age,
        "gender": gender,
        "personality_traits": personality_traits,
        "description": description
    }
    with open("character.json", "w") as f:
        json.dump(character, f)
    return "Character information saved successfully."

def load_user():
    try:
        with open("user.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"name": "", "age": "", "interests": ""}

def save_user(name, age, interests):
    user = {"name": name, "age": age, "interests": interests}
    with open("user.json", "w") as f:
        json.dump(user, f)
    return "User information saved successfully."

def load_settings():
    try:
        with open("settings.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"temperature": 0.7, "max_tokens": 150}

def save_settings(temperature, max_tokens):
    settings = {"temperature": temperature, "max_tokens": max_tokens}
    with open("settings.json", "w") as f:
        json.dump(settings, f)
    return "Settings saved successfully."

def chat(message, history, model, temperature, max_tokens):
    character = load_character()
    user = load_user()

    system_message = f"You are {character['name']}, a {character['age']}-year-old {character['gender']}. {character['description']} Your personality traits include: {character['personality_traits']}. You are responding to {user['name']}, a {user['age']}-year-old with interests in {user['interests']}."

    messages = [{"role": "system", "content": system_message}]
    for h in history:
        messages.append({"role": "user", "content": h[0]})
        messages.append({"role": "assistant", "content": h[1]})
    
    messages.append({"role": "user", "content": message})

    response = requests.post(
        API_URL,
        headers={"Content-Type": "application/json"},
        json={
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
    )

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.status_code} - {response.text}"

with gr.Blocks() as demo:
    with gr.Tab("Chat"):
        chatbot = gr.Chatbot()
        msg = gr.Textbox()
        clear = gr.Button("Clear")

        model = gr.Dropdown(choices=get_models(), label="Model")
        temperature = gr.Slider(minimum=0, maximum=1, value=0.7, step=0.1, label="Temperature")
        max_tokens = gr.Slider(minimum=1, maximum=2048, value=150, step=1, label="Max Tokens")

    with gr.Tab("Character"):
        name = gr.Textbox(label="Name")
        age = gr.Textbox(label="Age")
        gender = gr.Textbox(label="Gender")
        personality_traits = gr.Textbox(label="Personality Traits")
        description = gr.Textbox(label="Character Description")
        save_char = gr.Button("Save Character")
        char_status = gr.Textbox(label="Status", interactive=False)

    with gr.Tab("User"):
        user_name = gr.Textbox(label="Name")
        user_age = gr.Textbox(label="Age")
        user_interests = gr.Textbox(label="Interests")
        save_user_btn = gr.Button("Save User")
        user_status = gr.Textbox(label="Status", interactive=False)

    with gr.Tab("Settings"):
        save_settings_btn = gr.Button("Save Settings")
        settings_status = gr.Textbox(label="Status", interactive=False)

    def respond(message, chat_history, model, temperature, max_tokens):
        bot_message = chat(message, chat_history, model, temperature, max_tokens)
        chat_history.append((message, bot_message))
        return "", chat_history

    msg.submit(respond, [msg, chatbot, model, temperature, max_tokens], [msg, chatbot])
    clear.click(lambda: None, None, chatbot, queue=False)

    save_char.click(save_character, [name, age, gender, personality_traits, description], char_status)
    save_user_btn.click(save_user, [user_name, user_age, user_interests], user_status)
    save_settings_btn.click(save_settings, [temperature, max_tokens], settings_status)

    def load_character_fields():
        char = load_character()
        return char["name"], char["age"], char["gender"], char["personality_traits"], char["description"]

    def load_user_fields():
        user = load_user()
        return user["name"], user["age"], user["interests"]

    def load_settings_fields():
        settings = load_settings()
        return settings["temperature"], settings["max_tokens"]

    demo.load(load_character_fields, outputs=[name, age, gender, personality_traits, description])
    demo.load(load_user_fields, outputs=[user_name, user_age, user_interests])
    demo.load(load_settings_fields, outputs=[temperature, max_tokens])

demo.launch()