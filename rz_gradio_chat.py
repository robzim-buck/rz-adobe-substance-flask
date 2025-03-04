import time
import io
import shutil
import gradio as gr
from rz_adobe_substance_func import create_model, check_status, download_item
from PIL import Image as pil_image
from pprint import pprint as pp



def greet(name, intensity):
    return "Hello, " + name + "!" * int(intensity)




# def create(user_prompt:str=None):
#     # user_prompt = request.args.get('user_prompt')
#     print(user_prompt)
#     prompt = {
#     "cameraName": "main_camera",
#     "heroAsset": "bottle",
#     "prompt": f'"{user_prompt}"',
#     "sources": [
#     {
#         "url": {
#         "url": "https://cdn.substance3d.com/v2/files/public/compositing_table_bottle.glb"
#         }
#     }
#     ]
#     }
#     pp(prompt)
#     mymodel = create_model(prompt=prompt)
#     url = mymodel['url']
#     status_dict = check_status(url=url)
#     try:
#         if 'failed' == status_dict['status']:
#             raise Exception(f"Job failed: {status_dict}")

#         while 'succeeded' != status_dict['status']:
#             print("Swait 5 sec")
#             time.sleep(5)
#             print("Checking status in create")
#             try:
#               status_dict = check_status(url=url)
#               gr.Info(status_dict['status'], duration=3)
#             except Exception as e:
#               print(f'exception {e} getting ')
#               return "Failed.  Try Again."
#             # status_dict = check_status(url=url)
#             if 'failed' in status_dict['status']:
#                 raise Exception(f"Job failed: {status_dict}")
#         print("Done!")
#         print(f"Created {status_dict['result']['outputSpace']['files'][-1]['name']}")
#         file_url = status_dict['result']['outputSpace']['files'][-1]['url']
#         item = download_item(url=file_url)
#         img = pil_image.open(io.BytesIO(item))
#         img.save("zoop.png", "PNG")
#         return 'success.  Please Refesh the Screen!'
#     except Exception as _e:
#         print(f'exception {_e} getting results')



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
    theprompt = args[0]
    print(theprompt)
    create(user_prompt=theprompt)
    image_name = f'{theprompt.replace(" ", "_")}.png'
    myimg = gr.Image("zoop.png")
    copy_result = shutil.copy('zoop.png', image_name)
    print(copy_result)
    return myimg






demo = gr.Interface(
    title="Buck Glowworm Sample",
    description="Enter a prompt for a composite run with the sample model.",
    fn=get_stuff,
    show_progress='full',
    inputs=["text"],
    outputs=["image"],
)

demo.launch(server_port=7860, server_name='0.0.0.0')
