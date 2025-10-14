from unifiedai import UnifiedAI

client = UnifiedAI(credentials={"api_key": os.getenv("CEREBRAS_API_KEY", "")})
resp = client.chat.completions.create(
    messages=[{"role": "user", "content": "Hello"}],
    providers=["cerebras", "bedrock"],
    model="llama3",
)
print(resp)
