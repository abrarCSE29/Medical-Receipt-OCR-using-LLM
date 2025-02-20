import os
import re
import mimetypes
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
from dotenv import load_dotenv
from datetime import datetime

# Load API key from .env file
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Define the image folder path
IMAGE_FOLDER = r"D:\Softograph\OCR_cn_medical_dataset\Text-Detection-with-LLM-main\images"

# Function to upload image with MIME type detection
def upload_image(file_path):
    # Guess MIME type based on file extension
    mime_type, _ = mimetypes.guess_type(file_path)

    if mime_type is None:
        mime_type = "application/octet-stream"  # Default MIME type if unknown

    # Upload the file
    sample_file = genai.upload_file(path=file_path, display_name=os.path.basename(file_path))
    
    print(f"Uploaded file '{sample_file.display_name}' as: {sample_file.uri} with MIME type: {mime_type}")
    return sample_file

# Configure the model
generation_config = {
    "temperature": 0,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
    
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=generation_config,
    system_instruction="You have extract information from the medical test report image that is in chinese. Follow the below steps:\n\nstep 1: Analyze the image.\nstep 2 : From the image get the report title\nstep 3 : From the table in the IMAGE, get \"test_name\", \"value\", \"unit\" and \"range\" .Remove unnecessary characters. Enclose them in a test_results array\n \n step 4: Some images may have poor lighting condition. work accordingly. step 5: Show the output translated into english and in json format specified.")

# Function to process all .jpg images in the folder
def process_all_images():
    # Create the Responses directory if it doesn't exist
    response_directory = "D:\Softograph\OCR_cn_medical_dataset\Text-Detection-with-LLM-main\Responses"
    os.makedirs(response_directory, exist_ok=True)

    # Get all .jpg images from the folder
    image_paths = sorted(
        [
            os.path.join(IMAGE_FOLDER, file)
            for file in os.listdir(IMAGE_FOLDER)
            if file.lower().endswith(".jpg")
        ],
        key=lambda x: os.path.basename(x) 
    )

    image_paths.sort()

    print(f"Found {len(image_paths)} image(s) to process.")
    for image in enumerate(image_paths):
        print(image)

    for i, image_path in enumerate(image_paths):
        print(f"Processing {image_path}...")

        response = model.generate_content(["This is the image", upload_image(image_path)])

        # Generate timestamp

        pattern = r"^(.*)\.jpg$"
        print(image_path)
        image_name = re.search(r"([^\\\/]+)\.jpg$", image_path).group(1)
    
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")  # Format: YYYY-MM-DD_HH-MM-SS
        log_response_path = os.path.join(response_directory, f"{image_name}.json")

        # Save response to a text file
        with open(log_response_path, "w",errors='ignore') as file:
            file.write(response.text)

        print(f"Response saved to: {log_response_path}")

    print("All images processed successfully.")

# Run the function
if __name__ == "__main__":
    process_all_images()
