from unifiedai import UnifiedAI

client = UnifiedAI()
resp = client.chat.completions.create(
    messages=[{"role": "user", "content": "Hello"}],
    providers=["cerebras", "bedrock"],
    model="llama3",
)
print(resp)
