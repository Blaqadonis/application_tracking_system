from dotenv import load_dotenv
load_dotenv()

import os
import io
import base64
from PIL import Image
import pdf2image
import google.generativeai as genai
import gradio as gr

# Configure Google API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content([input, pdf_content[0], prompt])
    return response.text

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        ## Convert the PDF to image directly from bytes
        images = pdf2image.convert_from_bytes(uploaded_file)

        first_page = images[0]

        # Convert to bytes
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()  # encode to base64
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

def process_resume(input_text, uploaded_file, prompt):
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(prompt, pdf_content, input_text)
        return response
    else:
        return "Please upload the resume"

# Define prompts
input_prompt1 = """
 You are an experienced Technical Human Resource Manager, your task is to review the provided resume against the job description. 
 Please share your professional evaluation on whether the candidate's profile aligns with the role. 
 Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are an skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality, 
your task is to evaluate the resume against the provided job description. Give me the percentage of match if the resume matches
the job description. First the output should come as percentage and then keywords missing and last final thoughts.
"""

# Gradio Interface
iface = gr.Interface(
    fn=process_resume,
    inputs=[
        gr.Textbox(label="Job Description: "),
        gr.File(label="Upload your resume (PDF)...", type="binary"),
        gr.Radio(choices=[input_prompt1, input_prompt3], label="Select Prompt")
    ],
    outputs="text",
    title="🅱🅻🅰🆀's Resume Expert",
    description="How fit are you for careers in Big Data?"
)

if __name__ == "__main__":
    iface.launch(share=True, debug=True)