import os
from pathlib import Path
from tempfile import TemporaryDirectory

from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

from eoi_analyzer import EOIAnalyzer
from eoi_analyzer.config import SUPPORTED_DOCUMENT_EXTENSIONS
from eoi_analyzer.results import BatchAnalysis, DocumentFailure
import markdown  # For markdown formatting

# Optionally, load environment variables from a .env file if using python-dotenv
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {extension.lstrip(".") for extension in SUPPORTED_DOCUMENT_EXTENSIONS}

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
        files = request.files.getlist('files') or request.files.getlist('file')
        if not files:
            return redirect(request.url)
        files = [file for file in files if file.filename]
        if not files:
            return redirect(request.url)

        analyzer = EOIAnalyzer(OPENAI_API_KEY)
        batch = BatchAnalysis()

        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        with TemporaryDirectory(dir=app.config['UPLOAD_FOLDER']) as upload_dir:

            for file in files:
                filename = secure_filename(file.filename)
                if not allowed_file(filename):
                    batch.failures.append(
                        DocumentFailure(
                            source_path=filename,
                            source_name=filename,
                            error="Unsupported file type.",
                        )
                    )
                    continue

                filepath = Path(upload_dir) / filename
                file.save(filepath)

                try:
                    batch.analyses.append(analyzer.analyze_document(filepath, include_letter=True))
                except Exception as exc:
                    batch.failures.append(
                        DocumentFailure(
                            source_path=str(filepath),
                            source_name=filename,
                            error=str(exc),
                        )
                    )

        return render_template('results.html', batch=batch)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
