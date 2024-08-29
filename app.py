import gradio as gr
import openai

# Configure OpenAI to use the local LM Studio server
openai.api_base = "http://localhost:1234/v1"
openai.api_key = "not-needed"

def predict(message, history):
    history_openai_format = []
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

gr.ChatInterface(predict).launch()