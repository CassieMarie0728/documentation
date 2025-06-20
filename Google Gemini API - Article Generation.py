# @title # Google Gemini API Article Generator

# @markdown This Google Colab notebook provides a comprehensive environment to generate long-form articles (targeting at least 1800 words) using the Google Gemini API. It handles all necessary setup, user input for topic, tone, and style, allows for uploading reference documents, and incorporates iterative generation to meet the desired word count.

# @markdown **Instructions:**
# @markdown 1.  Run each code cell sequentially by clicking the play button next to it.
# @markdown 2.  Follow the prompts for API key setup, inputting article details, and uploading reference files.
# @markdown 3.  The final generated article will be displayed at the end.

# -----------------------------------------------------------------------------
# STEP 1: Install Necessary Python Packages and Import Libraries
# -----------------------------------------------------------------------------
# We need `google-generativeai` to interact with the Gemini API.
# `ipywidgets` and `IPython.display` are for creating interactive user inputs and displaying rich content.
# `google.colab.files` is for file uploads.
# `nest_asyncio` is often needed in Colab environments when mixing asyncio with
# event loops, which can happen with some libraries used by `google-generativeai`.
# `PyPDF2` for robust PDF document processing.

import sys

print("Installing required packages...")
try:
    # Suppress installation output for cleaner notebook
    !{sys.executable} -m pip install google-generativeai ipywidgets nest_asyncio PyPDF2 --quiet
    print("Packages installed successfully.")
except Exception as e:
    print(f"Error installing packages: {e}")
    print("Please check your internet connection or try again.")
    # Exit or raise an error if critical packages fail to install
    sys.exit(1)

# Import necessary libraries after installation
import google.generativeai as genai
import ipywidgets as widgets
from IPython.display import display, Markdown, HTML, clear_output
from google.colab import userdata, files
import nest_asyncio
import PyPDF2
import io # For handling binary data from file uploads

# Apply nest_asyncio for compatibility in Colab. This resolves potential asyncio runtime errors.
nest_asyncio.apply()

# @title ## STEP 2: Set Up Google Gemini API Key

# @markdown To use the Google Gemini API, you need an API key. We recommend storing it securely as a Colab Secret.

# @markdown **How to set up your API Key as a Colab Secret:**
# @markdown 1.  Click on the "🔑" (key) icon in the left sidebar of your Colab notebook.
# @markdown 2.  Click "Add a new secret".
# @markdown 3.  For the "Name" field, enter `GEMINI_API_KEY`.
# @markdown 4.  For the "Value" field, paste your actual Gemini API key.
# @markdown 5.  Make sure to enable "Notebook access" for this secret.
# @markdown 6.  Once added, you can close the "Secrets" tab.

# @markdown The code below will attempt to retrieve this secret. If it fails, it will prompt you to enter the key manually (less secure but functional).

# @markdown **Obtain your Gemini API Key:** If you don't have one, visit [Google AI Studio](https://aistudio.google.com/app/apikey) to create one.

# Configure the Google Gemini API
API_KEY = None
model = None # Initialize model to None

try:
    # Attempt to retrieve API key from Colab secrets
    API_KEY = userdata.get('GEMINI_API_KEY')
    if not API_KEY:
        print("API Key not found in Colab secrets.")
        # Fallback to manual input if secret is not set
        API_KEY = input("Please enter your Google Gemini API Key: ").strip()
        if not API_KEY:
            raise ValueError("API Key cannot be empty.")
    
    # Configure the generative AI library with the API key
    genai.configure(api_key=API_KEY)
    print("Google Gemini API configured successfully.")

    # Test a small model call to ensure authentication works
    try:
        # Initialize a temporary model to make a small test query
        model_test = genai.GenerativeModel('gemini-pro')
        # Send a minimal request to check connectivity and API key validity
        _ = model_test.generate_content("Hello", generation_config=genai.GenerationConfig(max_output_tokens=10))
        print("API key validated: Connection to Gemini API successful.")
        
        # Initialize the main GenerativeModel for article generation
        model = genai.GenerativeModel('gemini-pro')

    except Exception as e:
        print(f"API Key validation failed. Please check your key and ensure it has access to 'gemini-pro': {e}")
        API_KEY = None # Invalidate key if test fails
        print("Further operations requiring the Gemini API will not proceed.")
        # sys.exit(1) # Do not exit, just mark model as None

except Exception as e:
    print(f"Error configuring Google Gemini API: {e}")
    print("Please ensure your API key is correct and try again.")
    API_KEY = None
    # sys.exit(1) # Do not exit, just mark model as None

# @title ## STEP 3: Specify Article Details

# @markdown Use the interactive widgets below to define the core aspects of your article.

# Initialize global variables for article details. These will store user inputs.
ARTICLE_TOPIC = None
ARTICLE_TONE = None
ARTICLE_STYLE = None

# Create interactive widgets for user input
topic_input = widgets.Textarea(
    value='',
    placeholder='E.g., The Future of Artificial Intelligence in Healthcare, The History of Renewable Energy',
    description='Article Topic:',
    disabled=False,
    rows=3, # Provides more space for longer topics
    layout=widgets.Layout(width='80%') # Make the widget wider
)

# Dropdown for article tone options
tone_options = [
    'Informative', 'Persuasive', 'Friendly', 'Formal', 'Humorous',
    'Analytical', 'Critical', 'Objective', 'Subjective', 'Inspirational',
    'Technical', 'Poetic', 'Narrative'
]
tone_input = widgets.Dropdown(
    options=tone_options,
    value='Informative', # Default value
    description='Tone:',
    disabled=False,
)

# Dropdown for writing style options
style_options = [
    'Academic', 'Conversational', 'Technical', 'Journalistic', 'Blog Post',
    'Scientific', 'Literary', 'Marketing', 'Instructional', 'Storytelling'
]
style_input = widgets.Dropdown(
    options=style_options,
    value='Conversational', # Default value
    description='Writing Style:',
    disabled=False,
)

# Display widgets to the user
print("Please provide the details for your article:")
display(topic_input, tone_input, style_input)

# Button to confirm inputs and proceed
confirm_button = widgets.Button(description="Confirm Article Details")
output_details = widgets.Output() # Output widget to show messages

def on_confirm_details_clicked(b):
    """Callback function when the 'Confirm Article Details' button is clicked."""
    with output_details:
        clear_output() # Clear previous output in this section
        global ARTICLE_TOPIC, ARTICLE_TONE, ARTICLE_STYLE # Access global variables
        ARTICLE_TOPIC = topic_input.value.strip()
        ARTICLE_TONE = tone_input.value
        ARTICLE_STYLE = style_input.value

        # Validate that the topic is not empty
        if not ARTICLE_TOPIC:
            print("Error: Article Topic cannot be empty. Please provide a topic.")
            ARTICLE_TOPIC = None # Invalidate topic to prevent generation
            return

        print(f"Article Topic: '{ARTICLE_TOPIC}'")
        print(f"Article Tone: '{ARTICLE_TONE}'")
        print(f"Article Style: '{ARTICLE_STYLE}'")
        print("\nArticle details confirmed. You can now proceed to upload reference documents (optional).")

# Attach the callback function to the button's click event
confirm_button.on_click(on_confirm_details_clicked)
display(confirm_button, output_details) # Display the button and its output area

# @title ## STEP 4: Upload Reference Documents (Optional)

# @markdown You can upload text files (.txt, .md) or PDF files (.pdf) that the Gemini model can use as reference material. The content of these files will be incorporated into the prompt to guide the article generation.

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
                    continue # Skip to the next file
                
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

# @markdown This step uses the Google Gemini API to generate the article based on your inputs and reference material. The process may take a few moments. The notebook will attempt to generate an article of at least 1800 words, iteratively expanding it if necessary.

# Global variable to store the final generated article
GENERATED_ARTICLE = ""

def count_words(text):
    """Helper function to count words in a string."""
    if not text:
        return 0
    return len(text.split())

def generate_article(topic, tone, style, reference_material, min_word_count=1800, max_attempts=3):
    """
    Generates a long-form article using the Google Gemini API, with iterative expansion
    to meet a minimum word count.
    """
    if model is None:
        return "Error: Gemini model not initialized. Please check API key setup in Step 2."

    current_article = ""
    attempt = 0
    
    # Generation configuration for the model.
    # max_output_tokens is crucial for longer responses. 8192 is a common max for Gemini Pro.
    # Temperature controls creativity (higher = more creative).
    generation_config = genai.GenerationConfig(
        temperature=0.7,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192, # Maximum tokens for the model's output
    )

    # Loop to iteratively generate and expand the article until min_word_count is met
    while count_words(current_article) < min_word_count and attempt < max_attempts:
        attempt += 1
        print(f"\n--- Generation Attempt {attempt}/{max_attempts} ---")

        prompt_parts = []
        # Include reference material if available
        if reference_material:
            prompt_parts.append(f"Refer to the following background information and incorporate relevant details naturally:\n\nReference Material:\n{reference_material}\n\n")

        if attempt == 1:
            # Initial prompt for the first generation attempt
            prompt_parts.append(f"""
            Write a detailed and comprehensive long-form article on the topic of "{topic}".
            The article should be written in a {tone} tone and a {style} style.
            It must be at least {min_word_count} words long.
            Ensure the article is well-structured with an introduction, multiple body paragraphs, and a strong conclusion.
            Break down complex ideas, provide specific examples, and maintain coherence throughout.
            Focus on delivering a high-quality, in-depth analysis of the topic.
            """)
        else:
            # Expansion prompt for subsequent attempts if the article is too short
            print(f"Current article word count: {count_words(current_article)}. Expanding to reach {min_word_count} words.")
            prompt_parts.append(f"""
            The following article on "{topic}" is currently {count_words(current_article)} words long.
            Please expand upon it to reach a total length of at least {min_word_count} words.
            Focus on adding more detail, deeper analysis, additional examples, or further relevant sub-sections to the existing content.
            Maintain the original {tone} tone and {style} style.
            Do NOT rewrite the entire article from scratch. Just expand and elaborate on the existing content to meet the length requirement while improving depth and clarity.

            Existing Article to expand:
            {current_article}
            """)
        
        full_prompt = "\n".join(prompt_parts).strip()
        
        try:
            print("Sending request to Gemini API...")
            # The context window for gemini-pro is 30,720 tokens, which should accommodate
            # both the prompt (including reference material and existing article) and the desired output.
            response = model.generate_content(full_prompt, generation_config=generation_config)
            
            # Check if the response contains text content
            if response.text:
                current_article = response.text # The model is asked to return the *expanded* full article
                print(f"Generated text length: {count_words(current_article)} words.")
                if count_words(current_article) < min_word_count:
                    print("Article is still too short. Attempting to expand further...")
                else:
                    print("Target word count reached or exceeded.")
            else:
                # Handle cases where the API returns an empty response (e.g., due to safety filters)
                print("Gemini API returned an empty response. This might be due to safety filters or an internal error.")
                if response.prompt_feedback and response.prompt_feedback.block_reason:
                    print(f"Blocked Reason: {response.prompt_feedback.block_reason}")
                    print("Please try adjusting your topic or content to avoid sensitive subjects.")
                current_article = "ERROR: Could not generate content. Please try adjusting your prompt or inputs."
                break # Exit loop on empty or blocked response

        except Exception as e:
            # Catch any other API related errors (e.g., network issues, invalid request)
            print(f"An error occurred during API call: {e}")
            current_article = "ERROR: Failed to generate article due to API error. Please check your inputs and API key."
            break # Exit loop on API error

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
        if not ARTICLE_TOPIC or not ARTICLE_TONE or not ARTICLE_STYLE:
            print("Error: Please confirm article details in STEP 3 before generating.")
            return
        if model is None:
            print("Error: Gemini API is not configured. Please check STEP 2 (API Key Setup).")
            return

        print("Starting article generation process...")
        # Call the main article generation function
        final_article_text = generate_article(
            topic=ARTICLE_TOPIC,
            tone=ARTICLE_TONE,
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
else:
    print("No article was generated. Please ensure previous steps were completed successfully and without errors.")
    print("Check the outputs of Step 5 for any error messages or warnings.")