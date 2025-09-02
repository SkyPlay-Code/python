from google import genai

client = genai.Client(api_key="AIzaSyDZIpa8sya6wPRlNuzh1TJx07-k-rXPDY8")

myfile = client.files.upload(file='signal-2025-05-13-004036.aac')
prompt = 'Generate a transcript of the audio clip in hinglish.'

response = client.models.generate_content(
  model='gemini-2.0-flash',
  contents=[prompt, myfile]
)

print(response.text)