import os
import shutil
from glob import glob
import gradio as gr
from .common_gui import (
    get_any_file_path,
    get_folder_path,
    set_pretrained_model_name_or_path_input,
)

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

def get_sd_models():
    output = [""]
    out_dir = "/home/workspace/2_bucket/checkpoints/Stable-diffusion/"
    for root, dirs, files in os.walk(out_dir, followlinks=True):
        for file in files:
            if file.split(".")[-1]=='safetensors' or file.split(".")[-1]=='ckpt':
                output.append(os.path.relpath(os.path.join(root, file), out_dir))

    return output


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

class SourceModel:
    def __init__(
        self,
        save_model_as_choices=[
            #'same as source model',
            #'ckpt',
            #'diffusers',
            #'diffusers_safetensors',
            'safetensors',
        ],
        headless=False,
    ):
        self.headless = headless
        self.save_model_as_choices = save_model_as_choices

        with gr.Tab('1. Source model'):
            # Define the input elements
        
            with gr.Row():
                self.pretrained_model_name_or_path = gr.Dropdown(
                label="Source Checkpoint",
                choices=sorted(get_sd_models()),
            )
                with gr.Row():
                    create_refresh_button(
                        self.pretrained_model_name_or_path,
                        get_sd_models,
                        lambda: {"choices": sorted(
                            get_sd_models())},
                        "refresh_sd_models",
                    )
                    self.model_list = gr.Dropdown(
                        label='Model Quick Pick',
                        choices=[
                            'custom',
                            # 'stabilityai/stable-diffusion-xl-base-0.9',
                            # 'stabilityai/stable-diffusion-xl-refiner-0.9',
                            #'stabilityai/stable-diffusion-2-1-base/blob/main/v2-1_512-ema-pruned',
                            #'stabilityai/stable-diffusion-2-1-base',
                            #'stabilityai/stable-diffusion-2-base',
                            #'stabilityai/stable-diffusion-2-1/blob/main/v2-1_768-ema-pruned',
                            #'stabilityai/stable-diffusion-2-1',
                            #'stabilityai/stable-diffusion-2',
                            #'runwayml/stable-diffusion-v1-5',
                            #'CompVis/stable-diffusion-v1-4',
                        ],
                        value='custom',
                    )
                    self.save_model_as = gr.Dropdown(
                        label='Save trained model as',
                        choices=save_model_as_choices,
                        value='safetensors',
                    )



                #self.pretrained_model_name_or_path_file = gr.Button(
                #    document_symbol,
                #    elem_id='open_folder_small',
                #    visible=(False and not headless),
                #)
                #self.pretrained_model_name_or_path_file.click(
                #    get_any_file_path,
                #    inputs=self.pretrained_model_name_or_path,
                #    outputs=self.pretrained_model_name_or_path,
                #    show_progress=False,
                #)
                #self.pretrained_model_name_or_path_folder = gr.Button(
                #    folder_symbol,
                #    elem_id='open_folder_small',
                #    visible=(False and not headless),
                #)
                #self.pretrained_model_name_or_path_folder.click(
                #    get_folder_path,
                #    inputs=self.pretrained_model_name_or_path,
                #    outputs=self.pretrained_model_name_or_path,
                #    show_progress=False,
                #)
            with gr.Row():
                self.v2 = gr.Checkbox(label='v2', value=False, visible=True)
                self.v_parameterization = gr.Checkbox(
                    label='v_parameterization', value=False, visible=True
                )
                self.sdxl_checkbox = gr.Checkbox(
                    label='SDXL Model', value=True, visible=True, interactive=False
                )

            self.model_list.change(
                set_pretrained_model_name_or_path_input,
                inputs=[
                    self.model_list,
                    self.pretrained_model_name_or_path,
                    #self.pretrained_model_name_or_path_file,
                    #self.pretrained_model_name_or_path_folder,
                    self.v2,
                    self.v_parameterization,
                    self.sdxl_checkbox,
                ],
                outputs=[
                    self.model_list,
                    self.pretrained_model_name_or_path,
                    #self.pretrained_model_name_or_path_file,
                    #self.pretrained_model_name_or_path_folder,
                    self.v2,
                    self.v_parameterization,
                    self.sdxl_checkbox,
                ],
                show_progress=False,
            )
