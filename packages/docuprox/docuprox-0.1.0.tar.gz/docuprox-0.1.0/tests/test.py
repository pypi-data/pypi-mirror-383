from docuprox import Docuprox
import base64
import dotenv 

dotenv.load_dotenv()  # Load environment variables from .env file

# Initialize with your API key (or use environment variable DOCUPROX_API_KEY)
docu = Docuprox()

# Example 1: Process a file
try:
    result = docu.processfile("sample_image.png", "2bfe2633-b6fe-43d5-b626-2b329fef0b31")
    print("File Result:", result)
except Exception as e:
    print("Error:", e)

# Example 2: Process base64 data
try:
    with open("sample_image.png", "rb") as f:
        b64_data = base64.b64encode(f.read()).decode('utf-8')
    
    result = docu.processbase64(b64_data, "2bfe2633-b6fe-43d5-b626-2b329fef0b31")
    print("Base64 Result:", result)
except Exception as e:
    print("Error:", e)
