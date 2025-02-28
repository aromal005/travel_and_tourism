import google.generativeai as genai

# Replace with your actual API key
genai.configure(api_key="AIzaSyD_fP4qbXME-0EH-x3S3ULaxA4RMBdtd8g")

# try:
#     model = genai.GenerativeModel("gemini-pro")  # Use "gemini-pro" instead of "gemini-pro-1.0"
#     response = model.generate_content("Hello, how are you?")
#     print(response.text)
# except Exception as e:
#     print("Error:", str(e))

models = genai.list_models()
for model in models:
    print(model.name)
