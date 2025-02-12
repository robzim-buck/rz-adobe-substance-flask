#test adobe substance
import dotenv
import os
import io
import json
import requests
from pprint import pprint as pp
dotenv.load_dotenv('.env')
from PIL import Image as pil_image
import base64
import os
import traceback
from pathlib import Path
from pprint import pprint as pp
from time import sleep
from uuid import uuid4
import requests
import time


ADOBE_SUBSTANCE_API_KEY = os.getenv('ADOBE_SUBSTANCE_API_KEY')

ADOBE_CLIENT_ID = os.getenv('ADOBE_CLIENT_ID')


ADOBE_SUBSTANCE_CLIENT_ID = os.getenv('ADOBE_SUBSTANCE_CLIENT_ID')
ADOBE_SUBSTANCE_CLIENT_SECRET = os.getenv('ADOBE_SUBSTANCE_CLIENT_SECRET')



def authenticate():
  res = None
  try:
    res = requests.post(
    url="https://ims-na1.adobelogin.com/ims/token/v3",
    headers={
      "Content-Type": "application/x-www-form-urlencoded"
    },
    data={
      "grant_type": "client_credentials",
      "client_id": ADOBE_SUBSTANCE_CLIENT_ID,
      "client_secret": ADOBE_SUBSTANCE_CLIENT_SECRET,
      "scope": "openid, AdobeID, read_organizations, email, substance3d_api.jobs.create, firefly_api, profile, substance3d_api.spaces.create"
    },
    )
    res.raise_for_status()
    return res.json().get("access_token")
  except Exception as _e:
    print(f"exception {_e} authenticating")
    print(res.text)



ADOBE_SUBSTANCE_URL = 'https://s3d.adobe.io'

ADOBE_SUBSTANCE_API_KEY = authenticate()

ADOBE_SUBSTANCE_HEADERS={
  'X-API-Key': ADOBE_CLIENT_ID,
  'Accept': 'application/json',
  'Authorization': f'Bearer {ADOBE_SUBSTANCE_API_KEY}',
  'Content-Type': 'application/json'
}


def download_item(url:str=None):
    res = requests.get(url=url,
                  headers=ADOBE_SUBSTANCE_HEADERS)
    content = res.content
    return content


def upload_model(model:str=None):
    requests.post(url=ADOBE_SUBSTANCE_URL,
                  headers=ADOBE_SUBSTANCE_HEADERS,
                  json=model)



def create_model(prompt:object=None):
    res = requests.post(url='https://s3d.adobe.io/v1beta/3dscenes/compose',
                  headers=ADOBE_SUBSTANCE_HEADERS,
                  json=prompt)
    js = res.json()
    pp(js)
    return js



def render_model(model:str=None):
    two_cyl = 'https://github.com/KhronosGroup/glTF-Sample-Models/blob/main/2.0/2CylinderEngine/glTF-Binary/2CylinderEngine.glb'
    # water_bottle = '"https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/WaterBottle/glTF-Binary/WaterBottle.glb"'
    sample_model = {
  "scene": {
    "modelFile": "2CylinderEngine.glb"
  },
  "sources": [
    {
      "url": {
        "url": two_cyl
      }
    }
  ]
  }
    
    if model is None:
      model=sample_model

    res = requests.post(url='https://s3d.adobe.io/v1beta/3dmodels/render',
                  headers=ADOBE_SUBSTANCE_HEADERS,
                  json=model)
    js = res.json()

    # pp(js)
    return js


def check_status(url:str=None):
  res = requests.get(url=url,
                  headers=ADOBE_SUBSTANCE_HEADERS)
  js = res.json()
  pp(js)
  return js



def main():
  im = test_image()
  pp(im)
  return
  # tk = authenticate()
  # pp(tk)


  # res = create_model()
  # pp(res)




  prompt = {
  "cameraName": "main_camera",
  "heroAsset": "bottle",
  "prompt": "cat sitting on a bench in front of the sixtine chapel.  focal length 50mm",
  "sources": [
    {
      "url": {
        "url": "https://cdn.substance3d.com/v2/files/public/compositing_table_bottle.glb"
      }
    }
    ]
    }
  mymodel = create_model(prompt=prompt)
  pp(mymodel)



def make_api_call(url, data, *args, **kwargs):
  response = None
  try:
    response = requests.post(
    url=url,
    headers={
    "X-API-Key": ADOBE_SUBSTANCE_CLIENT_ID,
    "Authorization": f"Bearer {ADOBE_SUBSTANCE_API_KEY}",
    "Content-Type": "application/json"
    },
    json=data,
    *args,
    **kwargs
    )
    response.raise_for_status()
    return response.json()
  except Exception as _E:
    print(f"exception {_E} making api call")
    print(response.content)
    return response


def poll_job_status(response):
  if response is None:
    raise Exception("No response object found")
  status_res = None
  while True:
    status_res = requests.get(
    url=response.get("url"),
    headers={
    "Content-Type": "application/json",
    "Authorization" : f"Bearer {ADOBE_SUBSTANCE_API_KEY}",
    "Accept": "application/json",
    }
    )
    status_res.raise_for_status()
    job_status = status_res.json().get("status")
    print(f"Job status: {job_status}")
    if job_status == "succeeded":
      return status_res.json()
    elif job_status == "failed":
      raise Exception(f"Job failed: {status_res.json()}")
    else:
      sleep(5)


def create_3d_scene(payload):
  res = make_api_call(
  url="https://s3d.adobe.io/v1beta/3dscenes/create",
  data=payload
  )
  res.raise_for_status()
  status_res = poll_job_status(res)
  return status_res


def render_3d_scene(payload):
  res = make_api_call(
  url="https://s3d.adobe.io/v1beta/3dscenes/render",
  data=payload
  )
  res.raise_for_status()
  status_res = poll_job_status(res)
  return status_res



def compose_3d_model(payload):
  res = make_api_call(
  url="https://s3d.adobe.io/v1beta/3dscenes/compose",
  data=payload
  )
  res.raise_for_status()
  status_res = poll_job_status(res)
  return status_res



def describe_scene(payload):
  describe_scene_res = make_api_call(
  url="https://s3d.adobe.io/v1beta/3dscenes/get-description",
  data=payload
  )
  describe_scene_res.raise_for_status()
  status_res = poll_job_status(describe_scene_res)
  return status_res
  # convert 3D model


def convert_model(payload):
  res = make_api_call(
  url="https://s3d.adobe.io/v1beta/3dmodels/convert",
  data=payload
  )
  res.raise_for_status()
  status_res = poll_job_status(res)


# render a 3D model
def render_3d_model(data):
  render_image_data = None
  status_res = ''
  try:
    # api call to the endpoint
    res = make_api_call(
    url="https://s3d.adobe.io/v1beta/3dmodels/render",
    data=data
    )
    # poll for the job status
    status_res = poll_job_status(res)
    pp(status_res)
    # get the image data
    render_image_data = requests.get(
    url=status_res.get("result").get("renderUrl"),
    headers={
    "Authorization" : f"Bearer {ADOBE_SUBSTANCE_API_KEY}",
    }
    ).content
    return status_res
  except Exception as _e:
    print(f"exception {_e} rendering 3d model")
    print(traceback.format_exc())
    return render_image_data

testurl = 'https://cdn.substance3d.com/v2/files/public/compositing_table_bottle.glb'
oldurl = 'https://cdn.substance3d.com/v2/files/public/stepladder.usdz'


def test_image():
  model_with_background_color = render_3d_model(
    data={
      "background": {
      "backgroundColor": [.384,.871,0,1], # it is not clear in the doc that the values have to be less than or equal to 1 for RGBA. https://rgbcolorpicker.com/0-1
      "showEnvironment": False,
      },
      "scene": {},
      "sources": [
        {
          "mountPoint": "/",
          "url": {
          "url": testurl
        }
        }
      ],
      }
    )
  # myimg = pil_image.Image(data=model_with_background_color, width=600)
  return model_with_background_color


if __name__ == '__main__':
  # main()




  res = render_model()
  pp(res)
  url = res['url']
  status_dict = check_status(url=url)
  try:
    if 'failed' == status_dict['status']:
      raise Exception(f"Job failed: {status_dict}")

    while 'succeeded' != status_dict['status']:
        print("Swait 1 sec")
        time.sleep(1)
        status_dict = check_status(url=url)
    print("Done!")
    print(f"Created {status_dict['result']['outputSpace']['files'][-1]['name']}")
    file_url = status_dict['result']['outputSpace']['files'][-1]['url']
    # pp(status_dict)
    # url = status_dict['result']['outputs'][-1]['image']['url']
    # url = status_dict['result']['outputSpace'][-1]['image']['url']


    item = download_item(url=file_url)
    img = pil_image.open(io.BytesIO(item))



    # img = test_image()
    img.save("rztest5.png", "PNG")
  except Exception as _e:
    print(f'exception {_e} getting results')
