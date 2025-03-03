import time
import io
import shutil
import gradio as gr
from rz_adobe_substance_func import create_model, check_status, download_item
from PIL import Image as pil_image
from pprint import pprint as pp



def greet(name, intensity):
    return "Hello, " + name + "!" * int(intensity)




def create(user_prompt:str=None):
    print(user_prompt)
    prompt = {
        # "scene": cam_defs,
    "cameraName": "main_camera",
    "heroAsset": "bottle",
    "prompt": f'"{user_prompt}"',
    "sources": [
    {
        "url": {
        "url": "https://cdn.substance3d.com/v2/files/public/compositing_table_bottle.glb"
        }
    }
    ]
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
        image_name_from_prompt = f"{dashed_prompt}.png"
        # image_name = 'zoop.png'
        img.save(image_name_from_prompt, "PNG")
        return image_name_from_prompt
        # return 'success.  Please Refesh the Screen!'
    except Exception as _e:
        print(f'exception {_e} getting results')



def get_stuff(*args, **kwargs):
    gr.Info("Running Prompt Create")
    print(args)
    print(kwargs)
    theprompt = args[1]
    focal_length = args[2]
    camera_specs = args[6]
    print(camera_specs)
    print(focal_length)
    print(theprompt)
    myimg_name = create(user_prompt=theprompt)
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



import gradio as gr
import os

def load_mesh(mesh_file_name):
    return mesh_file_name

demo = gr.Interface(fn=get_stuff,
    inputs=[gr.Model3D(),
            gr.Text(label="Enter a Prompt"),
            gr.Slider(value=15, minimum=0, maximum=100, step=1, label="Camera Focal Length"),
            gr.Checkbox(value=True, label="Secret1 Checkbox"),
            gr.Checkbox(value=True, label="Secret2 Checkbox"),
            gr.Checkbox(value=True, label="Secret3 Checkbox"),
            gr.JSON(value=cam_defs, label= "Camera Definition"),
            gr.FileExplorer(glob="*.txt", label="Select A File To Upload")
            ],
    outputs = gr.Image(),
    examples=[
        [os.path.join(os.path.abspath(''), "files/Bunny.obj")],
        [os.path.join(os.path.abspath(''), "files/Duck.glb")],
        [os.path.join(os.path.abspath(''), "files/Fox.gltf")],
        [os.path.join(os.path.abspath(''), "files/face.obj")],
        [os.path.join(os.path.abspath(''), "files/sofia.stl")],
        ["https://huggingface.co/datasets/dylanebert/3dgs/resolve/main/bonsai/bonsai-7k-mini.splat"],
        ["https://huggingface.co/datasets/dylanebert/3dgs/resolve/main/luigi/luigi.ply"],
    ]
)

if __name__ == "__main__":
    demo.launch()

