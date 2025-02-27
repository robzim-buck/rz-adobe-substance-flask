#test adobe substance
import dotenv
import os
import shutil
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

import time
import io
from PIL import Image as pil_image
from flask import Flask, render_template, request, jsonify
from pprint import pprint as pp
from rz_adobe_substance_func import render_model, make_api_call, poll_job_status, create_model, render_3d_model, check_status



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
      "scope": ["openid", "AdobeID", "firefly_api", "firefly_enterprise", "substance3d_api.spaces.create", "email", "read_organizations", "substance3d_api.jobs.create", "profile"]
    },
    )
    res.raise_for_status()
    return res.json().get("access_token")
  except Exception as _e:
    print(f"exception {_e} authenticating")
    print(res.text)



ADOBE_SUBSTANCE_URL = 'https://s3d.adobe.io'

# ADOBE_SUBSTANCE_BEARER_TOKEN = authenticate()
ADOBE_SUBSTANCE_BEARER_TOKEN = os.getenv('ADOBE_SUBSTANCE_ACCESS_TOKEN')

ADOBE_SUBSTANCE_HEADERS={
  'X-API-Key': ADOBE_CLIENT_ID,
  'Accept': 'application/json',
  'Authorization': f'Bearer {ADOBE_SUBSTANCE_BEARER_TOKEN}',
  'Content-Type': 'application/json'
}


def download_item(url:str=None):
  
    tk = authenticate()
    _headers={
      'X-API-Key': ADOBE_CLIENT_ID,
      'Accept': 'application/json',
      'Authorization': f'Bearer {tk}',
      'Content-Type': 'application/json'
    }

  
    res = requests.get(url=url,
                  headers=_headers)
    content = res.content
    return content


def upload_model(model:str=None):
    requests.post(url=ADOBE_SUBSTANCE_URL,
                  headers=ADOBE_SUBSTANCE_HEADERS,
                  json=model)





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



testurl = 'https://cdn.substance3d.com/v2/files/public/compositing_table_bottle.glb'
# oldurl = 'https://cdn.substance3d.com/v2/files/public/stepladder.usdz'


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



app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


# @app.route('/linux_python_chat', methods=['GET', 'POST'])
# def linux_python():
#     message = request.form['msg']
#     return ask_question(rag_chain=pdf_chain, question=message)


@app.route('/auth', methods=['POST'])
def auth():
    # return 'yolo!'
    res = authenticate()
    print(res)
    return res



@app.route('/create', methods=['POST'])
def create():
    user_prompt = request.args.get('user_prompt')
    print(user_prompt)
    prompt = {
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
            print("Swait 1 sec")
            time.sleep(1)
            print("Checking status in create")
            try:
              status_dict = check_status(url=url)
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
        img.save("static/rztest5.png", "PNG")
        return 'success.  Please Refesh the Screen!'
    except Exception as _e:
        print(f'exception {_e} getting results')




@app.route('/render', methods=['POST'])
def render():
    res = test_image()
    url = res['url']
    status_dict = check_status(url=url)
    try:
        if 'failed' == status_dict['status']:
            raise Exception(f"Job failed: {status_dict}")

        while 'succeeded' != status_dict['status']:
            print("Swait 1 sec")
            time.sleep(1)
            print("Checking status in render")
            try:
              status_dict = check_status(url=url)
            except Exception as e:
              print(f'exception {e} getting ')
              return "Failed.  Try Again."
            if 'failed' in status_dict['status']:
              # raise Exception(f"Job failed: {status_dict}")
              return "Failed.  Try Again."
        print("Done!")
        print(f"Created {status_dict['result']['outputSpace']['files'][-1]['name']}")
        file_url = status_dict['result']['outputSpace']['files'][-1]['url']
        item = download_item(url=file_url)
        img = pil_image.open(io.BytesIO(item))
        img.save("rztest5.png", "PNG")
        # shutil.move("rztest5.png", "static/rztest5.png")
        return 'success'
    except Exception as _e:
        print(f'exception {_e} getting results')


# @app.route('/chat', methods=['GET', 'POST'])
# def chat():
#     message = request.form['msg']
#     result = ask_question(rag_chain=json_chain, question=message)
#     # return json2html.json2html.convert(json = result)
#     return result


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)