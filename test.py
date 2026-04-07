
from gradio_client import Client
import os
from dotenv import load_dotenv
load_dotenv()
client = Client('zhengchong/CatVTON', hf_token=os.getenv('HF_TOKEN'))
print(client.view_api())
