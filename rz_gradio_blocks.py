import gradio as gr
from rz_gradio_chat import get_stuff
def update(name):
    return f"Welcome to Gradio, {name}!"

with gr.Blocks() as demo:
    gr.Markdown("**Buck** Adobe Glowworm Demo.")
    with gr.Row():
        inp = gr.Textbox(placeholder="Enter your prompt here.")
        out = gr.Image()
    btn = gr.Button("Run")
    btn.click(fn=get_stuff, inputs=inp, outputs=out)



demo.launch()
