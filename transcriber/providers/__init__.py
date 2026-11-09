def get_provider(name: str, model: str, api_key: str):
    if name == "gemini":
        from .gemini import GeminiProvider
        return GeminiProvider(model, api_key)
    raise ValueError(f"Unknown provider: {name}")