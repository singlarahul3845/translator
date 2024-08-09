from flask import Flask, request, render_template_string
from deep_translator import GoogleTranslator
from bs4 import BeautifulSoup, NavigableString

app = Flask(__name__)

def translate_text_chunk(text, translator, max_length=5000):
    """Splits text into chunks and translates each chunk."""
    translated_chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_length, len(text))
        chunk = text[start:end]
        try:
            translated_chunk = translator.translate(chunk)
            translated_chunks.append(translated_chunk)
        except Exception as e:
            print(f"Error translating chunk: {e}")
            translated_chunks.append(chunk)  # Append original chunk if translation fails
        start = end
    return ''.join(translated_chunks)

def remove_shortcodes_and_translate(soup, target_language):
    translator = GoogleTranslator(source='auto', target=target_language)
    for element in soup.find_all(string=lambda text: isinstance(text, NavigableString)):
        stripped_text = element.strip()
        if stripped_text and not element.parent.name in ['code', 'pre']:  # Skip code blocks
            if '[' in stripped_text and ']' in stripped_text:  # This is likely a shortcode
                element.extract()
            else:
                translated_text = translate_text_chunk(stripped_text, translator)
                # Preserve the original formatting and replace the content with the translation
                element.replace_with(NavigableString(translated_text))

def translate_html_content(html_content):
    # Initialize a dictionary for storing translations
    translations = {}
    
    # Parse the HTML content with preserving formatting
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Languages to translate to
    languages = {
        'german': 'de',
        'french': 'fr',
        'arabic': 'ar',
        'korean': 'ko',
        'japanese': 'ja',
        'portuguese': 'pt',
        'spanish': 'es'
    }
    
    # Translate content for each language and store in the dictionary
    for language, code in languages.items():
        # Make a copy of the original soup object to avoid modifying the original content
        soup_copy = BeautifulSoup(str(soup), 'html.parser')
        remove_shortcodes_and_translate(soup_copy, code)
        translations[language] = soup_copy.decode(formatter="html")
    
    return translations

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        html_content = request.form.get("html_content")
        translations = translate_html_content(html_content)
        return render_template_string("""
            <h2>Translate HTML Content</h2>
            <form method="POST">
                <textarea name="html_content" rows="10" cols="100" placeholder="Enter HTML content here">{{ html_content }}</textarea><br><br>
                <input type="submit" value="Translate">
            </form>
            <h2>Translated HTML Content</h2>
            {% for language, translation in translations.items() %}
                <h3>{{ language.capitalize() }}:</h3>
                <textarea id="{{ language }}" rows="10" cols="100">{{ translation }}</textarea><br>
                <button onclick="copyToClipboard('{{ language }}')">Copy</button><br><br>
            {% endfor %}
            <a href="/">Translate another</a>
            <script>
                function copyToClipboard(elementId) {
                    var copyText = document.getElementById(elementId);
                    copyText.select();
                    copyText.setSelectionRange(0, 99999); // For mobile devices
                    document.execCommand("copy");
                    alert("Copied to clipboard: " + elementId);
                }
            </script>
        """, html_content=html_content, translations=translations)
    
    return render_template_string("""
        <h2>Translate HTML Content</h2>
        <form method="POST">
            <textarea name="html_content" rows="10" cols="100" placeholder="Enter HTML content here"></textarea><br><br>
            <input type="submit" value="Translate">
        </form>
    """)

if __name__ == "__main__":
    app.run(debug=True)
