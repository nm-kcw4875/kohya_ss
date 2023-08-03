import gradio as gr
from .common_gui import remove_doublequote
import os

folder_symbol = '\U0001f4c2'  # 📂
refresh_symbol = '\U0001f504'  # 🔄
save_style_symbol = '\U0001f4be'  # 💾
document_symbol = '\U0001F4C4'   # 📄

class ToolButton(gr.Button, gr.components.FormComponent):
    """Small button with single emoji as text, fits inside gradio forms"""

    def __init__(self, **kwargs):
        super().__init__(variant="tool", **kwargs)

    def get_block_name(self):
        return "button"


def get_preset_lists():
    output = [""]
    #out_dir = "../models/ai-based-generative-art-style-inference/"
    out_dir = "./presets/"

    if os.path.exists(out_dir):
        for item in os.listdir(out_dir):
            if item.split(".")[-1]=='json' :
                #output.append(os.path.join(out_dir, item))
                output.append(item)

    return output



def create_refresh_button(refresh_component, refresh_method, refreshed_args, elem_id):
    def refresh():
        refresh_method()
        args = refreshed_args() if callable(refreshed_args) else refreshed_args

        for k, v in args.items():
            setattr(refresh_component, k, v)

        return gr.update(**(args or {}))

    refresh_button = ToolButton(value=refresh_symbol, elem_id=elem_id)
    refresh_button.click(
        fn=refresh,
        inputs=[],
        outputs=[refresh_component]
    )
    #refresh_button.style(full_width=False)
    return refresh_button


class ConfigurationFile:
    def __init__(self, headless=False):
        self.headless = headless
        with gr.Accordion('Configuration file', open=False):
            with gr.Row():
                self.button_save_config = gr.Button('Save 💾', elem_id='open_folder')
                self.config_file_name = gr.Textbox(
                    label='',
                    placeholder="저장하고자 하는 프리셋 파일의 이름(ex. lora_0620.json)을 기입 후 Save 버튼을 누르세요",
                    interactive=True,
                )

            #with gr.Row():
            #    self.button_load_config = gr.Button('Load 💾', elem_id='open_folder')
            #    self.config_file_name_load = gr.Dropdown(
            #        label='',
            #        choices=sorted(get_preset_lists()),
            #    )
            #    create_refresh_button(
            #        self.config_file_name_load,
            #        get_preset_lists,
            #        lambda: {"choices": sorted(
            #            get_preset_lists())},
            #        "refresh preset list",
            #    )
                #config_file_name.change(
                #    remove_doublequote,
                #    inputs=[config_file_name],
                #    outputs=[config_file_name],
                #)


# class ConfigurationFile:
#     def __init__(self, headless=False):
#         self.headless = headless
#         with gr.Accordion('Configuration file', open=False):
#             with gr.Row():
#                 self.button_open_config = gr.Button(
#                     'Open 📂', elem_id='open_folder', visible=(not self.headless)
#                 )
#                 self.button_save_config = gr.Button(
#                     'Save 💾', elem_id='open_folder',
#                 )
#                 self.button_save_as_config = gr.Button(
#                     'Save as... 💾', elem_id='open_folder', visible=(not self.headless)
#                 )
#                 self.config_file_name = gr.Textbox(
#                     label='',
#                     placeholder="type the configuration file path or use the 'Open' button above to select it...",
#                     interactive=True,
#                 )
#                 self.button_load_config = gr.Button('Load 💾', elem_id='open_folder')
#                 self.config_file_name.blur(
#                     remove_doublequote,
#                     inputs=[self.config_file_name],
#                     outputs=[self.config_file_name],
#                 )
                
