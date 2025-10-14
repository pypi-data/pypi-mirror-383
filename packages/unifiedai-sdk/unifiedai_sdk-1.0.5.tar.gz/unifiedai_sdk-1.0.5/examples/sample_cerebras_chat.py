import os
from cerebras.cloud.sdk import Cerebras

client = Cerebras(api_key=os.getenv("CEREBRAS_API_KEY"))

response = client.chat.completions.create(
    model="qwen-3-32b",
    messages=[{"role": "user", "content": "Hello"}],
    stream=False,
)

print(response.model_dump_json(indent=2))