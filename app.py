import gradio as gr
import requests
import json
from functools import partial
import asyncio
import aiohttp
import traceback

# Constants
API_URL = "http://localhost:1234/v1/chat/completions"
MODELS_URL = "http://localhost:1234/v1/models"
CHARACTER_FILE = "character.json"
USER_FILE = "user.json"
SETTINGS_FILE = "settings.json"
SCENARIO_FILE = "scenario.json"

# File operations
def load_json(filename, default):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return default

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f)
    return f"Data saved successfully to {filename}."

# Updated load functions
def load_character():
    data = load_json(CHARACTER_FILE, {
        "name": "", "age": "", "gender": "", "occupation": "",
        "background": "", "personality_traits": "", "likes": "",
        "dislikes": "", "goals": "", "fears": "", "speaking_style": "",
        "appearance": ""
    })
    return (
        data["name"], data["age"], data["gender"], data["occupation"],
        data["background"], data["personality_traits"], data["likes"],
        data["dislikes"], data["goals"], data["fears"], data["speaking_style"],
        data["appearance"]
    )

def load_user():
    data = load_json(USER_FILE, {
        "name": "", "age": "", "gender": "", "occupation": "",
        "interests": "", "background": "", "personality": "", "goals": ""
    })
    return (
        data["name"], data["age"], data["gender"], data["occupation"],
        data["interests"], data["background"], data["personality"], data["goals"]
    )

def load_settings():
    data = load_json(SETTINGS_FILE, {"temperature": 0.7, "max_tokens": 150})
    return data["temperature"], data["max_tokens"]

def load_scenario():
    data = load_json(SCENARIO_FILE, {"location": "", "time": "", "context": "", "objectives": ""})
    return data["location"], data["time"], data["context"], data["objectives"]

# Save functions remain the same
save_character = partial(save_json, CHARACTER_FILE)
save_user = partial(save_json, USER_FILE)
save_settings = partial(save_json, SETTINGS_FILE)
save_scenario = partial(save_json, SCENARIO_FILE)

def generate_system_message():
    character = load_json(CHARACTER_FILE, {})
    user = load_json(USER_FILE, {})
    scenario = load_json(SCENARIO_FILE, {})
    
    return f"""Roleplay Guidelines:

Character: You are {character.get('name', '')}, a {character.get('age', '')}-year-old {character.get('gender', '')} who works as a {character.get('occupation', '')}.
Background: {character.get('background', '')}
Personality: {character.get('personality_traits', '')}
Likes: {character.get('likes', '')}
Dislikes: {character.get('dislikes', '')}
Goals: {character.get('goals', '')}
Fears: {character.get('fears', '')}
Speaking Style: {character.get('speaking_style', '')}
Appearance: {character.get('appearance', '')}

User: You are interacting with {user.get('name', '')}, a {user.get('age', '')}-year-old {user.get('gender', '')} who works as a {user.get('occupation', '')}.
User's Interests: {user.get('interests', '')}
User's Background: {user.get('background', '')}
User's Personality: {user.get('personality', '')}
User's Goals: {user.get('goals', '')}

Scenario:
Location: {scenario.get('location', '')}
Time: {scenario.get('time', '')}
Context: {scenario.get('context', '')}
Objectives: {scenario.get('objectives', '')}

Guidelines:
1. Always stay in character as {character.get('name', '')}.
2. Use your defined speaking style and personality traits in all responses.
3. Incorporate your background, likes, dislikes, goals, and fears into the conversation when relevant.
4. React to the user's messages based on your character's personality and the given scenario.
5. Use the scenario details to add depth and context to your responses.
6. Adapt your responses based on the user's background, interests, and goals when appropriate.
7. Never break character or acknowledge that you are an AI language model.
8. If asked to do something that goes against your character's personality or the scenario, respond as your character would in that situation.

Remember, you are roleplaying as a real person in a specific scenario. Make the interaction as realistic and immersive as possible."""

# Updated async functions for API calls
async def async_get_models():
    async with aiohttp.ClientSession() as session:
        async with session.get(MODELS_URL) as response:
            if response.status == 200:
                models = await response.json()
                model_list = [model["id"] for model in models["data"]]
                # Add a default model if it's not in the list
                default_model = "Lewdiculous/Lumimaid-v0.2-8B-GGUF-IQ-Imatrix/Lumimaid-v0.2-8B-Q4_K_S-imat.gguf"
                if default_model not in model_list:
                    model_list.append(default_model)
                return model_list
            return ["Error fetching models"]

async def async_chat(message, history, model, temperature, max_tokens):
    system_message = generate_system_message()
    messages = [{"role": "system", "content": system_message}]
    messages.extend([{"role": "user" if i % 2 == 0 else "assistant", "content": m} for h in history for i, m in enumerate(h)])
    messages.append({"role": "user", "content": message})

    async with aiohttp.ClientSession() as session:
        async with session.post(
            API_URL,
            headers={"Content-Type": "application/json"},
            json={
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        ) as response:
            if response.status == 200:
                result = await response.json()
                return result["choices"][0]["message"]["content"]
            return f"Error: {response.status} - {await response.text()}"

# Error handling function
def display_error(error):
    return f"An error occurred: {str(error)}\n\nPlease try again or contact support if the issue persists."

# Updated Gradio interface functions with error handling
async def respond(message, chat_history, model, temperature, max_tokens):
    try:
        bot_message = await async_chat(message, chat_history, model, temperature, max_tokens)
        chat_history.append((message, bot_message))
        return "", chat_history
    except Exception as e:
        error_message = display_error(e)
        chat_history.append((message, error_message))
        return "", chat_history

async def regenerate_last_response(chat_history, model, temperature, max_tokens):
    try:
        if chat_history:
            last_user_message = chat_history[-1][0]
            new_bot_message = await async_chat(last_user_message, chat_history[:-1], model, temperature, max_tokens)
            chat_history[-1] = (last_user_message, new_bot_message)
        return chat_history
    except Exception as e:
        error_message = display_error(e)
        chat_history.append(("Error during regeneration", error_message))
        return chat_history

# Gradio interface
with gr.Blocks() as demo:
    with gr.Tab("Chat"):
        chatbot = gr.Chatbot()
        msg = gr.Textbox()
        with gr.Row():
            clear = gr.Button("Clear")
            regen = gr.Button("Regen")

        model = gr.Dropdown(choices=[], label="Model", value="Lewdiculous/Lumimaid-v0.2-8B-GGUF-IQ-Imatrix/Lumimaid-v0.2-8B-Q4_K_S-imat.gguf")
        temperature = gr.Slider(minimum=0, maximum=1, value=0.7, step=0.1, label="Temperature")
        max_tokens = gr.Slider(minimum=1, maximum=2048, value=150, step=1, label="Max Tokens")

    with gr.Tab("Character"):
        name = gr.Textbox(label="Name")
        age = gr.Textbox(label="Age")
        gender = gr.Textbox(label="Gender")
        occupation = gr.Textbox(label="Occupation")
        background = gr.Textbox(label="Background")
        personality_traits = gr.Textbox(label="Personality Traits")
        likes = gr.Textbox(label="Likes")
        dislikes = gr.Textbox(label="Dislikes")
        goals = gr.Textbox(label="Goals")
        fears = gr.Textbox(label="Fears")
        speaking_style = gr.Textbox(label="Speaking Style")
        appearance = gr.Textbox(label="Appearance")
        save_char = gr.Button("Save Character")
        char_status = gr.Textbox(label="Status", interactive=False)

    with gr.Tab("User"):
        user_name = gr.Textbox(label="Name")
        user_age = gr.Textbox(label="Age")
        user_gender = gr.Textbox(label="Gender")
        user_occupation = gr.Textbox(label="Occupation")
        user_interests = gr.Textbox(label="Interests")
        user_background = gr.Textbox(label="Background")
        user_personality = gr.Textbox(label="Personality")
        user_goals = gr.Textbox(label="Goals")
        save_user_btn = gr.Button("Save User")
        user_status = gr.Textbox(label="Status", interactive=False)

    with gr.Tab("Scenario"):
        scenario_location = gr.Textbox(label="Location")
        scenario_time = gr.Textbox(label="Time")
        scenario_context = gr.Textbox(label="Context")
        scenario_objectives = gr.Textbox(label="Objectives")
        save_scenario_btn = gr.Button("Save Scenario")
        scenario_status = gr.Textbox(label="Status", interactive=False)

    with gr.Tab("Settings"):
        save_settings_btn = gr.Button("Save Settings")
        settings_status = gr.Textbox(label="Status", interactive=False)
        system_message_display = gr.TextArea(label="System Message", interactive=False)

    msg.submit(respond, [msg, chatbot, model, temperature, max_tokens], [msg, chatbot])
    clear.click(lambda: None, None, chatbot, queue=False)
    regen.click(regenerate_last_response, [chatbot, model, temperature, max_tokens], [chatbot])

    save_char.click(
        lambda *args: save_character(dict(zip(
            ["name", "age", "gender", "occupation", "background", "personality_traits", 
             "likes", "dislikes", "goals", "fears", "speaking_style", "appearance"], 
            args
        ))),
        [name, age, gender, occupation, background, personality_traits, 
         likes, dislikes, goals, fears, speaking_style, appearance],
        char_status
    )

    save_user_btn.click(
        lambda *args: save_user(dict(zip(
            ["name", "age", "gender", "occupation", "interests", "background", "personality", "goals"],
            args
        ))),
        [user_name, user_age, user_gender, user_occupation, user_interests, user_background, user_personality, user_goals],
        user_status
    )

    save_scenario_btn.click(
        lambda *args: save_scenario(dict(zip(
            ["location", "time", "context", "objectives"],
            args
        ))),
        [scenario_location, scenario_time, scenario_context, scenario_objectives],
        scenario_status
    )

    save_settings_btn.click(
        lambda t, m: save_settings({"temperature": t, "max_tokens": m}),
        [temperature, max_tokens],
        settings_status
    )

    demo.load(load_character, outputs=[name, age, gender, occupation, background, personality_traits, 
                                       likes, dislikes, goals, fears, speaking_style, appearance])
    demo.load(load_user, outputs=[user_name, user_age, user_gender, user_occupation, user_interests, 
                                  user_background, user_personality, user_goals])
    demo.load(load_scenario, outputs=[scenario_location, scenario_time, scenario_context, scenario_objectives])
    demo.load(load_settings, outputs=[temperature, max_tokens])
    demo.load(generate_system_message, outputs=[system_message_display])
    demo.load(async_get_models, outputs=[model])

if __name__ == "__main__":
    demo.launch()