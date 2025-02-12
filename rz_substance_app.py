import time
import io
from PIL import Image as pil_image
from flask import Flask, render_template, request, jsonify
from rz_adobe_substance_func import authenticate, ADOBE_CLIENT_ID, ADOBE_SUBSTANCE_API_KEY, \
    download_item, ADOBE_SUBSTANCE_CLIENT_SECRET, render_model, render_3d_scene, check_status,test_image, create_model
from pprint import pprint as pp

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
            status_dict = check_status(url=url)
            if 'failed' in status_dict['status']:
                raise Exception(f"Job failed: {status_dict}")
        print("Done!")
        print(f"Created {status_dict['result']['outputSpace']['files'][-1]['name']}")
        file_url = status_dict['result']['outputSpace']['files'][-1]['url']
        # pp(status_dict)
        # url = status_dict['result']['outputs'][-1]['image']['url']
        # url = status_dict['result']['outputSpace'][-1]['image']['url']


        item = download_item(url=file_url)
        img = pil_image.open(io.BytesIO(item))



        # img = test_image()
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
            status_dict = check_status(url=url)
            if 'failed' in status_dict['status']:
                raise Exception(f"Job failed: {status_dict}")
        print("Done!")
        print(f"Created {status_dict['result']['outputSpace']['files'][-1]['name']}")
        file_url = status_dict['result']['outputSpace']['files'][-1]['url']
        # pp(status_dict)
        # url = status_dict['result']['outputs'][-1]['image']['url']
        # url = status_dict['result']['outputSpace'][-1]['image']['url']


        item = download_item(url=file_url)
        img = pil_image.open(io.BytesIO(item))



        # img = test_image()
        img.save("static/rztest5.png", "PNG")
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
    app.run(host="0.0.0.0", port=6000)