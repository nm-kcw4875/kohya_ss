import gradio as gr
from easygui import msgbox
import subprocess
import os
from .common_gui import get_folder_path, add_pre_postfix
from library.custom_logging import setup_logging


folder_symbol = '\U0001f4c2'  # 📂
refresh_symbol = '\U0001f504'  # 🔄
save_style_symbol = '\U0001f4be'  # 💾
document_symbol = '\U0001F4C4'   # 📄

# Set up logging
log = setup_logging()

PYTHON = 'python3' if os.name == 'posix' else './venv/Scripts/python.exe'


class ToolButton(gr.Button, gr.components.FormComponent):
    """Small button with single emoji as text, fits inside gradio forms"""

    def __init__(self, **kwargs):
        super().__init__(variant="tool", **kwargs)

    def get_block_name(self):
        return "button"

def get_image_dir():
    output = [""]
    out_dir = "/home/workspace/local_bucket/datasets/"
    if os.path.exists(out_dir):
        for item in os.listdir(out_dir):
            if os.path.isdir(os.path.join(out_dir, item)):
                output.append(os.path.join(out_dir, item))
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

def caption_images(
    train_data_dir,
    caption_file_ext,
    batch_size,
    num_beams,
    top_p,
    max_length,
    min_length,
    beam_search,
    prefix,
    postfix,
):
    # Check if the image folder is provided
    if train_data_dir == '':
        msgbox('Image folder is missing...')
        return

    # Check if the caption file extension is provided
    if caption_file_ext == '':
        msgbox('Please provide an extension for the caption files.')
        return

    log.info(f'Captioning files in {train_data_dir}...')

    # Construct the command to run
    run_cmd = f'{PYTHON} "finetune/make_captions.py"'
    run_cmd += f' --batch_size="{int(batch_size)}"'
    run_cmd += f' --num_beams="{int(num_beams)}"'
    run_cmd += f' --top_p="{top_p}"'
    run_cmd += f' --max_length="{int(max_length)}"'
    run_cmd += f' --min_length="{int(min_length)}"'
    if beam_search:
        run_cmd += f' --beam_search'
    if caption_file_ext != '':
        run_cmd += f' --caption_extension="{caption_file_ext}"'
    run_cmd += f' "{train_data_dir}"'
    run_cmd += f' --caption_weights="https://storage.googleapis.com/sfr-vision-language-research/BLIP/models/model_large_caption.pth"'

    log.info(run_cmd)

    # Run the command
    if os.name == 'posix':
        os.system(run_cmd)
    else:
        subprocess.run(run_cmd)

    # Add prefix and postfix
    add_pre_postfix(
        folder=train_data_dir,
        caption_file_ext=caption_file_ext,
        prefix=prefix,
        postfix=postfix,
    )

    log.info('...captioning done')


###
# Gradio UI
###


def gradio_blip_caption_gui_tab(headless=False):
    with gr.Tab('BLIP Captioning'):
        gr.Markdown(
            'This utility uses BLIP to caption files for each image in a folder.'
        )
        with gr.Row():
            train_data_dir = gr.Dropdown(
                label="Training images",
                choices=sorted(get_image_dir()),
            )
            with gr.Row(min_length=10):
                create_refresh_button(
                    train_data_dir,
                    get_image_dir,
                    lambda: {"choices": sorted(
                        get_image_dir())},
                    "refresh_sd_models",
                )
            # train_data_dir = gr.Textbox(
            #     label='Image folder to caption',
            #     placeholder='Directory containing the images to caption',
            #     interactive=True,
            # )
            #button_train_data_dir_input = gr.Button(
            #    '📂', elem_id='open_folder_small', visible=(not headless)
            #)
            #button_train_data_dir_input.click(
            #    get_folder_path,
            #    outputs=train_data_dir,
            #    show_progress=False,
            #)
        with gr.Row():
            caption_file_ext = gr.Textbox(
                label='Caption file extension',
                placeholder='Extension for caption file, e.g., .caption, .txt',
                value='.txt',
                interactive=False,
            )

            prefix = gr.Textbox(
                label='Prefix to add to BLIP caption',
                placeholder='(Optional)',
                interactive=True,
            )

            postfix = gr.Textbox(
                label='Postfix to add to BLIP caption',
                placeholder='(Optional)',
                interactive=True,
            )

            batch_size = gr.Number(
                value=1, label='Batch size', interactive=True
            )

        with gr.Row():
            beam_search = gr.Checkbox(
                label='Use beam search', interactive=True, value=True
            )
            num_beams = gr.Number(
                value=1, label='Number of beams', interactive=True
            )
            top_p = gr.Number(value=0.9, label='Top p', interactive=True)
            max_length = gr.Number(
                value=75, label='Max length', interactive=True
            )
            min_length = gr.Number(
                value=5, label='Min length', interactive=True
            )

        caption_button = gr.Button('Caption images')

        caption_button.click(
            caption_images,
            inputs=[
                train_data_dir,
                caption_file_ext,
                batch_size,
                num_beams,
                top_p,
                max_length,
                min_length,
                beam_search,
                prefix,
                postfix,
            ],
            show_progress=False,
        )
