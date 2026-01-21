import gradio as gr
from llm import chat

with gr.Blocks() as ui:
    chatbot = gr.Chatbot(height=500, type="messages")
    entry = gr.Textbox(label="Chatea con nuestro Agente de IA")
    clear = gr.Button("Clear")

    def do_entry(message, history):
        history = history or []
        history.append({"role": "user", "content": message})
        return "", history

    entry.submit(
        do_entry,
        inputs=[entry, chatbot],
        outputs=[entry, chatbot]
    ).then(
        chat,
        inputs=chatbot,
        outputs=chatbot
    )

    clear.click(
        lambda: [],
        inputs=None,
        outputs=chatbot,
        queue=False
    )

ui.launch(inbrowser=True)
