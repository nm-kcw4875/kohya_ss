import gradio as gr
from easygui import msgbox
import subprocess
from .common_gui import get_folder_path, add_pre_postfix
import os

from library.custom_logging import setup_logging

folder_symbol = '\U0001f4c2'  # 📂
refresh_symbol = '\U0001f504'  # 🔄
save_style_symbol = '\U0001f4be'  # 💾
document_symbol = '\U0001F4C4'   # 📄


# Set up logging
log = setup_logging()

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
    caption_extension,
    batch_size,
    general_threshold,
    character_threshold,
    replace_underscores,
    model,
    recursive,
    max_data_loader_n_workers,
    debug,
    undesired_tags,
    frequency_tags,
    prefix,
    postfix,
):
    # Check for images_dir_input
    if train_data_dir == '':
        msgbox('Image folder is missing...')
        return

    if caption_extension == '':
        msgbox('Please provide an extension for the caption files.')
        return

    log.info(f'Captioning files in {train_data_dir}...')
    run_cmd = f'accelerate launch "./finetune/tag_images_by_wd14_tagger.py"'
    run_cmd += f' --batch_size={int(batch_size)}'
    run_cmd += f' --general_threshold={general_threshold}'
    run_cmd += f' --character_threshold={character_threshold}'
    run_cmd += f' --caption_extension="{caption_extension}"'
    run_cmd += f' --model="{model}"'
    run_cmd += (
        f' --max_data_loader_n_workers="{int(max_data_loader_n_workers)}"'
    )

    if recursive:
        run_cmd += f' --recursive'
    if debug:
        run_cmd += f' --debug'
    if replace_underscores:
        run_cmd += f' --remove_underscore'
    if frequency_tags:
        run_cmd += f' --frequency_tags'

    if not undesired_tags == '':
        run_cmd += f' --undesired_tags="{undesired_tags}"'
    run_cmd += f' "{train_data_dir}"'

    log.info(run_cmd)

    # Run the command
    if os.name == 'posix':
        os.system(run_cmd)
    else:
        subprocess.run(run_cmd)

    # Add prefix and postfix
    add_pre_postfix(
        folder=train_data_dir,
        caption_file_ext=caption_extension,
        prefix=prefix,
        postfix=postfix,
    )

    log.info('...captioning done')


###
# Gradio UI
###


def gradio_wd14_caption_gui_tab(headless=False):
    with gr.Tab('WD14 Captioning'):
        gr.Markdown(
            'This utility will use WD14 to caption files for each images in a folder.'
        )

        # Input Settings
        # with gr.Section('Input Settings'):
        with gr.Row():
            train_data_dir = gr.Dropdown(
                label="Training images",
                choices=sorted(get_image_dir()),
            )
            with gr.Row():
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

                caption_extension = gr.Textbox(
                    label='Caption file extension',
                    placeholder='Extention for caption file. eg: .caption, .txt',
                    value='.txt',
                    interactive=False,
                )

        undesired_tags = gr.Textbox(
            label='Undesired tags',
            placeholder='(Optional) Separate `undesired_tags` with comma `(,)` if you want to remove multiple tags, e.g. `1girl,solo,smile`.',
            interactive=True,
        )

        with gr.Row():
            prefix = gr.Textbox(
                label='Prefix to add to WD14 caption',
                placeholder='(Optional)',
                interactive=True,
            )

            postfix = gr.Textbox(
                label='Postfix to add to WD14 caption',
                placeholder='(Optional)',
                interactive=True,
            )

        with gr.Row():
            replace_underscores = gr.Checkbox(
                label='Replace underscores in filenames with spaces',
                value=True,
                interactive=True,
            )
            recursive = gr.Checkbox(
                label='Recursive',
                value=False,
                info='Tag subfolders images as well',
            )

            debug = gr.Checkbox(
                label='Verbose logging',
                value=True,
                info='Debug while tagging, it will print your image file with general tags and character tags.',
            )
            frequency_tags = gr.Checkbox(
                label='Show tags frequency',
                value=True,
                info='Show frequency of tags for images.',
            )

        # Model Settings
        with gr.Row():
            model = gr.Dropdown(
                label='Model',
                choices=[
                    'SmilingWolf/wd-v1-4-convnext-tagger-v2',
                    'SmilingWolf/wd-v1-4-convnextv2-tagger-v2',
                    'SmilingWolf/wd-v1-4-vit-tagger-v2',
                    'SmilingWolf/wd-v1-4-swinv2-tagger-v2',
                ],
                value='SmilingWolf/wd-v1-4-convnextv2-tagger-v2',
            )

            general_threshold = gr.Slider(
                value=0.35,
                label='General threshold',
                info='Adjust `general_threshold` for pruning tags (less tags, less flexible)',
                minimum=0,
                maximum=1,
                step=0.05,
            )
            character_threshold = gr.Slider(
                value=0.35,
                label='Character threshold',
                info='useful if you want to train with character',
                minimum=0,
                maximum=1,
                step=0.05,
            )

        # Advanced Settings
        with gr.Row():
            batch_size = gr.Number(
                value=8, label='Batch size', interactive=True
            )

            max_data_loader_n_workers = gr.Number(
                value=2, label='Max dataloader workers', interactive=True
            )

        caption_button = gr.Button('Caption images')

        caption_button.click(
            caption_images,
            inputs=[
                train_data_dir,
                caption_extension,
                batch_size,
                general_threshold,
                character_threshold,
                replace_underscores,
                model,
                recursive,
                max_data_loader_n_workers,
                debug,
                undesired_tags,
                frequency_tags,
                prefix,
                postfix,
            ],
            show_progress=False,
        )
