import json

from unifiedai import UnifiedAI

"""Synchronous example of listing models."""
print("=== Synchronous Model Listing ===\n")

# List all models from all providers
client = UnifiedAI()
all_models = client.models.list(provider="bedrock")
print(f"Bedrock models: {len(all_models.data)} found")
print(json.dumps(all_models.model_dump(), indent=2))

print("\n" + "=" * 50 + "\n")

# List models from specific provider
cerebras_models = client.models.list(provider="cerebras")
print(f"Cerebras models: {len(cerebras_models.data)} found")
print(json.dumps(cerebras_models.model_dump(), indent=2))
