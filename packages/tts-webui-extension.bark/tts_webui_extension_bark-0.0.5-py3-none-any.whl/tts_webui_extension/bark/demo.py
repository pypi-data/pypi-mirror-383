import gradio as gr
from .main import ui

with gr.Blocks() as demo:
    ui()

demo.launch()
