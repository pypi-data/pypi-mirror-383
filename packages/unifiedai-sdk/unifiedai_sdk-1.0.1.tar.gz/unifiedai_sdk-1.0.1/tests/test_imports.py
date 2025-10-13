def test_import_and_client():
    from unified_ai import OpenAI

    client = OpenAI(provider="cerebras", model="llama3")
    assert hasattr(client, "chat")
    assert hasattr(client.chat, "completions")
