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

def save_system_message(message):
    global system_message
    system_message = message
    with open("system_message.json", "w") as f:
        json.dump({"system_message": system_message}, f)
    return "System message saved successfully!"

def load_system_message():
    global system_message
    if os.path.exists("system_message.json"):
        with open("system_message.json", "r") as f:
            data = json.load(f)
            system_message = data.get("system_message", "You are a helpful assistant.")
    return system_message

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
            gr.Markdown("# Settings")
            system_message_input = gr.Textbox(label="System Message", lines=5, value=load_system_message())
            save_button = gr.Button("Save System Message")
            load_button = gr.Button("Load System Message")
            result = gr.Textbox(label="Result")

            save_button.click(save_system_message, inputs=system_message_input, outputs=result)
            load_button.click(load_system_message, outputs=system_message_input)

demo.launch()