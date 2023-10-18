from googletrans import Translator

translator = Translator(service_urls=['translate.google.com'])

def translate_text(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == 'text':
                if isinstance(value, str):  # Check if the value is a string
                    translated_text = translator.translate(value, src='en', dest='pl')
                    data[key] = translated_text.text
            elif isinstance(value, (dict, list)):
                translate_text(value)
    elif isinstance(data, list):
        for item in data:
            translate_text(item)

    return translate_text
