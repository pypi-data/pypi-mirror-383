from litellm import completion
import json

def run_litellm(system_prompt: str, json_text: str, model_name: str = "gpt-4o-mini"):
    """
    Takes a system prompt and a JSON string as input,
    sends them to a LiteLLM model, and returns the response text.
    """

    # Try to load JSON to ensure it's valid
    try:
        json_data = json.loads(json_text)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON text provided")

    # Format content for the model
    user_message = f"Here is the metadata:\n{json.dumps(json_data, indent=2)}"

    # Generate completion
    response = completion(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    )

    # Extract response text
    return response['choices'][0]['message']['content']