from unifiedai import UnifiedAI

client = UnifiedAI(provider="cerebras", model="llama3")
resp = client.chat.completions.create(messages=[{"role": "user", "content": "Hello"}])
print(resp.choices[0].message["content"])
