source .venv/bin/activate
export GRADIO_SERVER_PORT=5000
export GRADIO_SERVER_NAME="0.0.0.0"
gradio rz_gradio_scratch.py
