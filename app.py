from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
from eoi_analyzer import EOIAnalyzer
import markdown  # For markdown formatting

# Optionally, load environment variables from a .env file if using python-dotenv
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

# Get OpenAI API key from environment variable
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("No OpenAI API key found. Please set the OPENAI_API_KEY environment variable.")

# Register a Jinja filter to convert markdown to HTML.
app.jinja_env.filters['markdown'] = lambda text: markdown.markdown(text)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if a file was submitted
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(filepath)

            analyzer = EOIAnalyzer(OPENAI_API_KEY)
            results = analyzer.analyze_pdf(filepath)

            # Optionally remove the file after processing
            os.remove(filepath)
            return render_template('results.html', results=results)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)