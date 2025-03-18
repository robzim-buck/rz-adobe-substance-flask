import time
import os
import io
import gradio as gr
from rz_adobe_substance_func import create_model, check_status, download_item
from PIL import Image as pil_image
from pprint import pprint as pp



def create(user_prompt:str=None,  focal_length_in_mm:int=50, seed:int=99999, filename:str=None):
    print(user_prompt)
    prompt = {
    "sources": [
        {
        "url": {
            "url": "https://cdn.substance3d.com/v2/files/public/compositing_table_bottle.glb"
        }
        }
    ],
    "heroAsset": "bottle",
    "cameraName": "main_camera",
    "prompt": f"{user_prompt}.  focal length {focal_length_in_mm} mm",
    "seeds": [int(seed)]
    }
    pp(prompt)
    mymodel = create_model(prompt=prompt)
    url = mymodel['url']
    status_dict = check_status(url=url)
    try:
        if 'failed' == status_dict['status']:
            raise Exception(f"Job failed: {status_dict}")

        while 'succeeded' != status_dict['status']:
            print("Swait 5 sec")
            time.sleep(5)
            print("Checking status in create")
            try:
              status_dict = check_status(url=url)
              gr.Info(status_dict['status'], duration=3)
            except Exception as e:
              print(f'exception {e} getting ')
              return "Failed.  Try Again."
            # status_dict = check_status(url=url)
            if 'failed' in status_dict['status']:
                raise Exception(f"Job failed: {status_dict}")
        print("Done!")
        print(f"Created {status_dict['result']['outputSpace']['files'][-1]['name']}")
        file_url = status_dict['result']['outputSpace']['files'][-1]['url']
        item = download_item(url=file_url)
        img = pil_image.open(io.BytesIO(item))
        dashed_prompt = prompt['prompt'].replace(" ", "_")
        dashed_prompt_with_seed = dashed_prompt + f"_seed_{seed}"
        dashed_prompt_with_seed = dashed_prompt_with_seed[:128]
        image_name_from_prompt = f"{dashed_prompt_with_seed}.png"
        if filename and filename is not None:
            image_name_from_prompt = f"{filename}.png"
        # image_name = 'zoop.png'
        img.save(image_name_from_prompt, "PNG")
        return image_name_from_prompt
        # return 'success.  Please Refesh the Screen!'
    except Exception as _e:
        print(f'exception {_e} getting results')



def get_stuff(theprompt:str=None, focal_length:int=None, seed:int=None, filename:str=None):
    gr.Info("Running Prompt Create")
    myimg_name = create(user_prompt=theprompt, focal_length_in_mm=focal_length, seed=seed, filename=filename)
    my_image =gr.Image(value=myimg_name)
    # copy_result = shutil.copy('zoop.png', myimg_name)
    # print(copy_result)
    return my_image


cam_defs = {
      "focal": 10,
      "transform": {
        "azimuthAltitude": {
          "azimuth": 90, "altitude": 90,
          "lookAt": [0, 0, 0],
          "radius": 1
        }
      }
}




def load_mesh(mesh_file_name):
    return mesh_file_name

demo = gr.Interface(
    title="Buck Glowworm Sample",
    description="This is a sample of the Buck Glowworm project.  It will take a prompt and create an image.",
    fn=get_stuff,
    inputs=[
            # gr.Model3D(),
            # gr.Checkbox(value=True, label="Secret1 Checkbox"),
            # gr.Checkbox(value=True, label="Secret2 Checkbox"),
            # gr.Checkbox(value=True, label="Secret3 Checkbox"),
            gr.Text(label="Enter a Prompt"),
            gr.Text(label="Focal Length in mm"),
            gr.Text(label="Seed Integer for Render Randomness"),
            gr.Text(label="Enter a File Name or Leave Blank to Name with First 128 Chars of Prompt")
            # gr.Slider(value=15, minimum=0, maximum=100, step=1, label="Camera Focal Length"),
            # gr.JSON(value=cam_defs, label= "Camera Definition"),
            # gr.FileExplorer(glob="*.txt", label="Select A File To Upload")
            ],
    outputs = gr.Image(),
    # examples=[
    #     [os.path.join(os.path.abspath(''), "files/Bunny.obj")],
    #     [os.path.join(os.path.abspath(''), "files/Duck.glb")],
    #     [os.path.join(os.path.abspath(''), "files/Fox.gltf")],
    #     [os.path.join(os.path.abspath(''), "files/face.obj")],
    #     [os.path.join(os.path.abspath(''), "files/sofia.stl")],
    #     ["https://huggingface.co/datasets/dylanebert/3dgs/resolve/main/bonsai/bonsai-7k-mini.splat"],
    #     ["https://huggingface.co/datasets/dylanebert/3dgs/resolve/main/luigi/luigi.ply"],
    # ]
)

if __name__ == "__main__":
    demo.launch()

