import openai
from app.api.api_v1.endpoints.settings import get_setting_list
from app.api.api_v1.endpoints.articles import generate_value

# Set up OpenAI API credentials
def set_openai_credentials(api_key):
    openai.api_key = api_key

# Get the setting list and retrieve the API key
setting_list = get_setting_list()
setting = setting_list[0]  # Assuming there is only one setting
api_key = setting.api_key

# Set the OpenAI API credentials using the retrieved API key
set_openai_credentials(api_key)

# Define your item
item = {
    'prompt_parsed_text': ''  # Placeholder for prompt_parsed_text
}

# Generate prompt_parsed_text using the retrieved API key
generate_value(item, {})  # This updates the 'prompt_parsed_text' in 'item'

# Access the parsed prompt text
prompt_parsed_text = item['prompt_parsed_text']
print(prompt_parsed_text)

# Use the parsed prompt text with OpenAI API
response = openai.Completion.create(
    engine='davinci',
    prompt=prompt_parsed_text,
    max_tokens=100,
    temperature=0.8
)

# Print the generated completion
generate_response = response.choices[0].text.strip()
