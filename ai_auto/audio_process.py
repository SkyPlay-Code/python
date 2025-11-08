from google import genai

client = genai.Client(api_key="GEMINI_API_KEY")

myfile = client.files.upload(file='FILE_PATH')
prompt = 'Generate a transcript of the audio without timestamps'

response = client.models.generate_content(
  model='gemini-2.0-flash',
  contents=[prompt, myfile]
)

print(response.text)