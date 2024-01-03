import importlib
import os
from PIL import Image
import gradio as gr
from omegaconf import OmegaConf

config = OmegaConf.load("config/annotator.yaml")

package_annotator = "processor"


def process_image(cls: str, fg: Image.Image, bg: Image.Image, *kwargs):
    if fg.size != bg.size:
        fg = fg.resize(bg.size)
    module_imp = importlib.import_module(package_annotator)
    model = getattr(module_imp, cls)
    image_processor = model()
    result = image_processor(fg, bg, *kwargs)
    if type(result) == tuple:
        return result
    return [result]


def process(cls):
    def process_fc(img, res, *args):
        return process_image(cls, img, res, *args)

    return process_fc


block = gr.Blocks().queue()
examples = [[os.path.join(os.path.dirname(__file__), "example/product.png"),
             os.path.join(os.path.dirname(__file__), "example/bg.png")]]
with block:
    for key in config.keys():
        cls, input_element = config[key]["process"], config[key].get("input")
        input_append = []
        with gr.Tab(key):
            with gr.Row():
                gr.Markdown("## " + key)
            with gr.Row():
                with gr.Column():
                    input_image = gr.Image(label="foreground", source='upload', type="pil", image_mode="RGBA")
                    bg_image = gr.Image(label="background", source='upload', type="pil", image_mode="RGBA")
                    if input_element is not None:
                        for item in input_element:
                            input_append.append(getattr(gr, item["attr"])(**item["args"]))
                    run_button = gr.Button(label="Run")
                    gr.Examples(examples, [input_image, bg_image])
                with gr.Column():
                    gallery = gr.Gallery(label="Generated images", show_label=False).style(height="auto")

            run_button.click(fn=process(cls),
                             inputs=[input_image, bg_image] + input_append,
                             outputs=[gallery])

block.launch()
