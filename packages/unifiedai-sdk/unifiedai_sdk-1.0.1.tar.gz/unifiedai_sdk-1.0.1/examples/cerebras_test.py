from cerebras.cloud.sdk import Cerebras

client = Cerebras(api_key="csk-8mv8mtcrkkc3fmvrm2knm9we3ntxjf5cjyymymn92f8p84mj")

# Fetch available models
models = client.models.list()

for m in models.data:
    print(m.id, m.owned_by)

client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[{"role": "user", "content": "Hello sir"}]
)

print(completion.choices[0].message.content)


# from huggingface_hub import InferenceClient

# client = InferenceClient(
#     provider="cerebras",
#     api_key="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",
# )

# completion = client.chat.completions.create(
#     model="openai/gpt-oss-120b",
#     messages=[{"role": "user", "content": "Hello sir"}]
# )
# print(completion.choices[0].message.content)
