# eoi_analyzer
Go from EoI to product management plan using OpenAI

input: EoI pdf
output:
- Key software engineering goals
- Product management plan
- Potential risks
- Clarifying questions

## usage
1. clone this repo
2. go to the folder
   ```cd eoi_analyzer```
3. create a python virtual environment
   ```python3 -m venv venv```
4. activate the environment
   ```source venv/bin/activate```
6. install requirements
  ```pip install -r requirements.txt```
7. create a .env file with your OpenAI key
  ```OPENAI_API_KEY="<your-openai-api-key>"```
__NOTE__: It seems to work without API key as well. (check & verify)
9. run the app
  ```python app.py```

On your computer, go to http://127.0.0.1:5000
1. Choose the pdf
2. Press analyze
