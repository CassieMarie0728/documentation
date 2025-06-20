# @title # Mistral API Article Generator

# @markdown This Google Colab notebook provides a comprehensive environment to generate long-form articles (targeting at least 1800 words) using the Mistral API. It handles all necessary setup, user input for topic, tone, attitude, and style, allows for uploading reference documents, and incorporates iterative generation to meet the desired word count.

# @markdown **Instructions:**
# @markdown 1.  Run each code cell sequentially by clicking the play button next to it.
# @markdown 2.  Follow the prompts for API key setup, inputting article details, and uploading reference files.
# @markdown 3.  The final generated article will be displayed at the end.

# -----------------------------------------------------------------------------
# STEP 1: Install Necessary Python Packages and Import Libraries
# -----------------------------------------------------------------------------
# We need `requests` to interact with the Mistral API directly via HTTP.
# `ipywidgets` and `IPython.display` are for creating interactive user inputs and displaying rich content.
# `google.colab.files` is for file uploads.
# `PyPDF2` for robust PDF document processing.

import sys

print("Installing required packages...")
try:
    # Suppress installation output for cleaner notebook
    !{sys.executable} -m pip install requests ipywidgets PyPDF2 --quiet
    print("Packages installed successfully.")
except Exception as e:
    print(f"Error installing packages: {e}")
    print("Please check your internet connection or try again.")
    # Exit or raise an error if critical packages fail to install
    sys.exit(1)

# Import necessary libraries after installation
import requests
import ipywidgets as widgets
from IPython.display import display, Markdown, HTML, clear_output
from google.colab import userdata, files
import PyPDF2
import io # For handling binary data from file uploads
import json # For handling JSON responses from API

# Define the Mistral API endpoint and default model
MISTRAL_API_BASE_URL = "https://api.mistral.ai/v1"
MISTRAL_MODEL = "mistral-medium-latest" # You can change this to "mistral-large-latest", "mixtral-8x7b-instruct-v0.1", etc.

# @title ## STEP 2: Set Up Mistral API Key

# @markdown To use the Mistral API, you need an API key. We recommend storing it securely as a Colab Secret.

# @markdown **How to set up your API Key as a Colab Secret:**
# @markdown 1.  Click on the "🔑" (key) icon in the left sidebar of your Colab notebook.
# @markdown 2.  Click "Add a new secret".
# @markdown 3.  For the "Name" field, enter `MISTRAL_API_KEY`.
# @markdown 4.  For the "Value" field, paste your actual Mistral API key.
# @markdown 5.  Make sure to enable "Notebook access" for this secret.
# @markdown 6.  Once added, you can close the "Secrets" tab.

# @markdown The code below will attempt to retrieve this secret. If it fails, it will prompt you to enter the key manually (less secure but functional).

# @markdown **Obtain your Mistral API Key:** If you don't have one, visit [Mistral AI Platform](https://console.mistral.ai/api-keys) to create one.

MISTRAL_API_KEY = None

try:
    # Attempt to retrieve API key from Colab secrets
    MISTRAL_API_KEY = userdata.get('MISTRAL_API_KEY')
    if not MISTRAL_API_KEY:
        print("API Key not found in Colab secrets.")
        # Fallback to manual input if secret is not set
        MISTRAL_API_KEY = input("Please enter your Mistral API Key: ").strip()
        if not MISTRAL_API_KEY:
            raise ValueError("Mistral API Key cannot be empty.")
    
    print("Mistral API Key loaded successfully.")

    # Test a small model call to ensure authentication works
    try:
        test_url = f"{MISTRAL_API_BASE_URL}/chat/completions"
        test_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {MISTRAL_API_KEY}"
        }
        test_data = {
            "model": MISTRAL_MODEL,
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10
        }
        
        response = requests.post(test_url, headers=test_headers, json=test_data)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        
        if response.json().get('choices'):
            print("API key validated: Connection to Mistral API successful.")
        else:
            print("API key validation failed: Empty response or unexpected format.")
            MISTRAL_API_KEY = None

    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error validating API key: {errh}")
        print("Please check your API key's validity and permissions.")
        MISTRAL_API_KEY = None
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting to Mistral API: {errc}")
        print("Please check your internet connection.")
        MISTRAL_API_KEY = None
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error validating API key: {errt}")
        MISTRAL_API_KEY = None
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred validating API key: {err}")
        MISTRAL_API_KEY = None
    except Exception as e:
        print(f"An error occurred during API key validation: {e}")
        MISTRAL_API_KEY = None

except Exception as e:
    print(f"Error setting up Mistral API Key: {e}")
    print("Please ensure your API key is correct and try again.")
    MISTRAL_API_KEY = None

# @title ## STEP 3: Specify Article Details

# @markdown Use the interactive widgets below to define the core aspects of your article.

# Initialize global variables for article details. These will store user inputs.
ARTICLE_TOPIC = None
ARTICLE_TONE = None
ARTICLE_ATTITUDE = None
ARTICLE_STYLE = None

# Create interactive widgets for user input
topic_input = widgets.Textarea(
    value='',
    placeholder='E.g., The Impact of Quantum Computing on Cybersecurity, Sustainable Urban Development',
    description='Article Topic:',
    disabled=False,
    rows=3,
    layout=widgets.Layout(width='80%')
)

# Dropdown for article tone options
tone_options = [
    'Informative', 'Persuasive', 'Friendly', 'Formal', 'Humorous', 'Analytical',
    'Critical', 'Objective', 'Subjective', 'Inspirational', 'Technical',
    'Poetic', 'Narrative', 'Journalistic'
]
tone_input = widgets.Dropdown(
    options=tone_options,
    value='Informative',
    description='Tone:',
    disabled=False,
)

# Dropdown for article attitude options
attitude_options = [
    'Neutral', 'Optimistic', 'Pessimistic', 'Enthusiastic', 'Skeptical',
    'Authoritative', 'Cautious', 'Hopeful', 'Empathetic', 'Doubtful'
]
attitude_input = widgets.Dropdown(
    options=attitude_options,
    value='Neutral',
    description='Attitude:',
    disabled=False,
)

# Dropdown for writing style options
style_options = [
    'Academic', 'Conversational', 'Technical', 'Blog Post', 'Scientific',
    'Literary', 'Marketing', 'Instructional', 'Storytelling', 'Debate',
    'Expository', 'Descriptive'
]
style_input = widgets.Dropdown(
    options=style_options,
    value='Conversational',
    description='Writing Style:',
    disabled=False,
)

# Display widgets to the user
print("Please provide the details for your article:")
display(topic_input, tone_input, attitude_input, style_input)

# Button to confirm inputs and proceed
confirm_button = widgets.Button(description="Confirm Article Details")
output_details = widgets.Output() # Output widget to show messages

def on_confirm_details_clicked(b):
    """Callback function when the 'Confirm Article Details' button is clicked."""
    with output_details:
        clear_output() # Clear previous output in this section
        global ARTICLE_TOPIC, ARTICLE_TONE, ARTICLE_ATTITUDE, ARTICLE_STYLE
        ARTICLE_TOPIC = topic_input.value.strip()
        ARTICLE_TONE = tone_input.value
        ARTICLE_ATTITUDE = attitude_input.value
        ARTICLE_STYLE = style_input.value

        # Validate that the topic is not empty
        if not ARTICLE_TOPIC:
            print("Error: Article Topic cannot be empty. Please provide a topic.")
            ARTICLE_TOPIC = None
            return

        print(f"Article Topic: '{ARTICLE_TOPIC}'")
        print(f"Article Tone: '{ARTICLE_TONE}'")
        print(f"Article Attitude: '{ARTICLE_ATTITUDE}'")
        print(f"Article Style: '{ARTICLE_STYLE}'")
        print("\nArticle details confirmed. You can now proceed to upload reference documents (optional).")

# Attach the callback function to the button's click event
confirm_button.on_click(on_confirm_details_clicked)
display(confirm_button, output_details) # Display the button and its output area

# @title ## STEP 4: Upload Reference Documents (Optional)

# @markdown You can upload text files (.txt, .md) or PDF files (.pdf) that the Mistral model can use as reference material. The content of these files will be incorporated into the prompt to guide the article generation.

# @markdown *   **Supported formats:** .txt, .md, .pdf
# @markdown *   You can upload multiple files.

# Global variable to store combined reference material from uploaded documents
REFERENCE_MATERIAL = ""

def read_text_file(uploaded_file_content):
    """Reads content from a text-based file (e.g., .txt, .md) with UTF-8 and Latin-1 fallback."""
    try:
        return uploaded_file_content.decode('utf-8')
    except UnicodeDecodeError:
        try:
            return uploaded_file_content.decode('latin-1') # Fallback for other encodings
        except Exception as e:
            print(f"Could not decode text file: {e}")
            return None

def read_pdf_file(uploaded_file_content):
    """Reads content from a PDF file using PyPDF2."""
    try:
        # PyPDF2 expects a file-like object, so we use io.BytesIO
        pdf_file = io.BytesIO(uploaded_file_content)
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        # Iterate through all pages and extract text
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text() + "\n" # Add a newline between page contents
        return text
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return None

upload_button = widgets.Button(description="Upload Reference Documents")
output_upload = widgets.Output() # Output widget for upload messages

def on_upload_clicked(b):
    """Callback function when the 'Upload Reference Documents' button is clicked."""
    global REFERENCE_MATERIAL
    REFERENCE_MATERIAL = "" # Reset reference material for new uploads or to clear previous
    with output_upload:
        clear_output() # Clear previous output in this section
        print("Please select your reference files to upload (txt, md, pdf):")
        try:
            # Use google.colab.files.upload() for the file picker
            uploaded = files.upload()
            
            if not uploaded:
                print("No files selected or uploaded.")
                return

            # Process each uploaded file
            for filename, content in uploaded.items():
                print(f"Processing '{filename}'...")
                file_extension = filename.split('.')[-1].lower() # Get file extension
                
                extracted_text = None
                if file_extension in ['txt', 'md']:
                    extracted_text = read_text_file(content)
                elif file_extension == 'pdf':
                    extracted_text = read_pdf_file(content)
                else:
                    print(f"Skipping unsupported file type: '{filename}' (only .txt, .md, .pdf are supported).")
                    continue
                
                if extracted_text:
                    # Append extracted text with clear delimiters for the LLM
                    REFERENCE_MATERIAL += f"\n--- Start of Reference Document: {filename} ---\n"
                    REFERENCE_MATERIAL += extracted_text
                    REFERENCE_MATERIAL += f"\n--- End of Reference Document: {filename} ---\n"
                    print(f"Successfully processed '{filename}'. Content length: {len(extracted_text)} characters.")
                else:
                    print(f"Failed to extract text from '{filename}'. It might be empty or corrupted.")
            
            if REFERENCE_MATERIAL:
                print("\nAll selected reference documents processed. Content will be used for article generation.")
                print(f"Total combined reference material length: {len(REFERENCE_MATERIAL)} characters.")
            else:
                print("No usable reference material was uploaded or extracted.")

        except Exception as e:
            print(f"An error occurred during file upload or processing: {e}")
            REFERENCE_MATERIAL = "" # Clear reference material if error occurs to prevent using partial data

# Attach the callback function to the button's click event
upload_button.on_click(on_upload_clicked)
display(upload_button, output_upload) # Display the button and its output area

# @title ## STEP 5: Generate the Long-Form Article

# @markdown This step uses the Mistral API to generate the article based on your inputs and reference material. The process may take a few moments. The notebook will attempt to generate an article of at least 1800 words, iteratively expanding it if necessary.

# Global variable to store the final generated article
GENERATED_ARTICLE = ""

def count_words(text):
    """Helper function to count words in a string."""
    if not text:
        return 0
    return len(text.split())

def call_mistral_api(messages, model=MISTRAL_MODEL, max_tokens=8192, temperature=0.7):
    """
    Helper function to make a call to the Mistral API.
    """
    if not MISTRAL_API_KEY:
        print("Error: Mistral API key is not set.")
        return None

    url = f"{MISTRAL_API_BASE_URL}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {MISTRAL_API_KEY}"
    }
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "random_seed": 42 # For reproducibility, optional
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=300) # 5-minute timeout
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        response_json = response.json()
        
        if response_json and response_json.get('choices'):
            # Return the content of the first message in choices
            return response_json['choices'][0]['message']['content']
        else:
            print(f"Mistral API returned an empty or malformed response: {response_json}")
            # Check for error details if available
            if response_json.get('error'):
                print(f"API Error Details: {response_json['error']}")
            return None

    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh} - Response: {response.text}")
        return None
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
        return None
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
        return None
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: Could not parse response from Mistral API: {e}")
        print(f"Raw response: {response.text}")
        return None

def generate_article(topic, tone, attitude, style, reference_material, min_word_count=1800, max_attempts=3):
    """
    Generates a long-form article using the Mistral API, with iterative expansion
    to meet a minimum word count.
    """
    if MISTRAL_API_KEY is None:
        return "Error: Mistral API key is not configured. Please check Step 2."

    current_article = ""
    attempt = 0
    
    # Mistral API uses chat message format
    # System role can be used for instructions, user for prompts.
    
    while count_words(current_article) < min_word_count and attempt < max_attempts:
        attempt += 1
        print(f"\n--- Generation Attempt {attempt}/{max_attempts} ---")

        messages = []
        
        # System message for general instructions
        system_prompt = f"""
        You are a highly skilled AI writer specializing in long-form content.
        Your task is to generate a comprehensive, detailed, and high-quality article.
        Maintain a {tone} tone, an {attitude} attitude, and a {style} writing style throughout the article.
        Ensure the article is well-structured with clear headings, subheadings, and logical flow.
        """
        messages.append({"role": "system", "content": system_prompt})

        # User message for content generation, including reference material and expansion logic
        user_prompt_parts = []

        if reference_material:
            user_prompt_parts.append(f"Here is some reference material. Integrate relevant information naturally, but do not just copy-paste. Synthesize and analyze it:\n\nReference Material:\n{reference_material}\n\n")

        if attempt == 1:
            # Initial prompt for the first generation attempt
            user_prompt_parts.append(f"""
            Write a detailed and comprehensive long-form article on the topic of "{topic}".
            The article must be at least {min_word_count} words long.
            It should include an introduction, multiple distinct body sections with appropriate headings, and a strong conclusion.
            Provide in-depth analysis, specific examples, and relevant details to fully explore the topic.
            """)
        else:
            # Expansion prompt for subsequent attempts if the article is too short
            print(f"Current article word count: {count_words(current_article)}. Expanding to reach {min_word_count} words.")
            user_prompt_parts.append(f"""
            The following article on "{topic}" is currently {count_words(current_article)} words long.
            Please expand upon it to reach a total length of at least {min_word_count} words.
            Do NOT rewrite the entire article from scratch. Instead, add more detail, deeper analysis, additional examples, or further relevant sub-sections to the existing content.
            Maintain the original {tone} tone, {attitude} attitude, and {style} style.
            Focus on increasing depth and clarity while seamlessly integrating new content.

            Existing Article to expand:
            {current_article}
            """)
        
        messages.append({"role": "user", "content": "\n".join(user_prompt_parts).strip()})
        
        try:
            print(f"Sending request to Mistral API with model '{MISTRAL_MODEL}'...")
            response_content = call_mistral_api(messages)
            
            if response_content:
                current_article = response_content # The model is asked to return the *expanded* full article
                print(f"Generated text length: {count_words(current_article)} words.")
                if count_words(current_article) < min_word_count:
                    print("Article is still too short. Attempting to expand further...")
                else:
                    print("Target word count reached or exceeded.")
            else:
                print("Mistral API returned an empty or errored response. Cannot proceed with generation.")
                current_article = "ERROR: Could not generate content. Please try adjusting your prompt or inputs."
                break # Exit loop on empty or blocked response

        except Exception as e:
            print(f"An unexpected error occurred during API call: {e}")
            current_article = "ERROR: Failed to generate article due to an unexpected error. Please check your inputs and API key."
            break

    # Final check and message after all attempts
    if count_words(current_article) < min_word_count:
        print(f"\nWarning: Could not reach the target word count of {min_word_count} words after {max_attempts} attempts.")
        print(f"Final article length: {count_words(current_article)} words.")
        print("You may try increasing 'max_attempts' (in the code), adjusting the prompt, or providing more detailed reference material.")
    else:
        print(f"\nArticle generation complete! Final word count: {count_words(current_article)} words.")
    
    return current_article

# Button to trigger article generation
generate_button = widgets.Button(description="Generate Article")
output_generation = widgets.Output() # Output widget for generation messages

def on_generate_clicked(b):
    """Callback function when the 'Generate Article' button is clicked."""
    with output_generation:
        clear_output() # Clear previous output
        # Pre-flight checks
        if not ARTICLE_TOPIC or not ARTICLE_TONE or not ARTICLE_ATTITUDE or not ARTICLE_STYLE:
            print("Error: Please confirm article details in STEP 3 before generating.")
            return
        if MISTRAL_API_KEY is None:
            print("Error: Mistral API is not configured. Please check STEP 2 (API Key Setup).")
            return

        print("Starting article generation process...")
        # Call the main article generation function
        final_article_text = generate_article(
            topic=ARTICLE_TOPIC,
            tone=ARTICLE_TONE,
            attitude=ARTICLE_ATTITUDE,
            style=ARTICLE_STYLE,
            reference_material=REFERENCE_MATERIAL
        )
        global GENERATED_ARTICLE
        GENERATED_ARTICLE = final_article_text # Store the result globally
        print("\n--- Generation Process Completed ---")
        print("The generated article is ready for display in the next step.")

# Attach the callback function to the button's click event
generate_button.on_click(on_generate_clicked)
display(generate_button, output_generation) # Display the button and its output area

# @title ## STEP 6: Display Generated Article

# @markdown Here is your generated long-form article.

# Display the final generated article
if GENERATED_ARTICLE:
    # Display the article using Markdown for better readability
    display(Markdown(GENERATED_ARTICLE))
    print(f"\n--- Article displayed successfully. Total words: {count_words(GENERATED_ARTICLE)} ---")

    # Optional: Provide a download link for the generated article
    try:
        # Create a BytesIO object to simulate a file for download
        article_bytes = GENERATED_ARTICLE.encode('utf-8')
        b64 = base64.b64encode(article_bytes).decode() # Encode to base64
        filename = f"generated_article_{ARTICLE_TOPIC.replace(' ', '_')[:50]}.md" # Create a filename

        # HTML link to download the file
        download_link = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">Download Generated Article (.md)</a>'
        display(HTML(download_link))
        print("Download link provided above.")
    except Exception as e:
        print(f"Could not create download link: {e}")

else:
    print("No article was generated. Please ensure previous steps were completed successfully and without errors.")
    print("Check the outputs of Step 5 for any error messages or warnings.")