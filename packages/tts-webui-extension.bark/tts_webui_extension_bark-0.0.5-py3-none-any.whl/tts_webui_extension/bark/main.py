import gradio as gr
from .bark_tab import bark_ui
from .voices.voices_tab import voices_tab
from .settings_tab_bark import settings_tab_bark
from .vocos_tab_bark import vocos_tab_bark


def ui():
    with gr.Tabs():
        with gr.Tab("Generation"):
            bark_ui()

        voices_tab()
        with gr.Tab("Voice Clone"):
            try:
                from tts_webui_extension.bark_voice_clone.main import ui as voice_clone_ui

                voice_clone_ui()
            except ImportError:
                print("Bark Voice Clone not installed or failed to load.")
                gr.Markdown(
                    "Bark Voice Clone extension not installed or failed to load."
                )
                pass
        settings_tab_bark()
        vocos_tab_bark()


def extension__tts_generation_webui():
    ui()
    return {
        "package_name": "extension_bark",
        "name": "Bark",
        "requirements": "git+https://github.com/rsxdalv/extension_bark@main",
        "description": "Bark: A text-to-speech model",
        "extension_type": "interface",
        "extension_class": "text-to-speech",
        "author": "Suno",
        "extension_author": "rsxdalv",
        "license": "MIT",
        "website": "https://github.com/suno-ai/bark",
        "extension_website": "https://github.com/rsxdalv/extension_bark",
        "extension_platform_version": "0.0.1",
    }


if __name__ == "__main__":
    if "demo" in locals():
        locals()["demo"].close()
    with gr.Blocks() as demo:
        ui()
    demo.launch()
