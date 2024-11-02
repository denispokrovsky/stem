import modal
import os
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
from pdf2image import convert_from_bytes
from byaldi import RAGMultiModalModel
import torch

stub = modal.Stub("financial-analyzer")

# Create Modal image with required dependencies
image = modal.Image.debian_slim().pip_install(
    "transformers",
    "torch",
    "pdf2image",
    "byaldi",
    "qwen-vl-utils",
    "flash-attn",
    "python-dotenv"
)

@stub.function(
    image=image,
    gpu="A10G",
    timeout=600
)
def process_pdf(pdf_file):
    # Convert PDF to images
    images = convert_from_bytes(pdf_file.read())
    
    # Initialize ColPali model
    rag = RAGMultiModalModel.from_pretrained("vidore/colpali")
    
    # Initialize Qwen model
    model = Qwen2VLForConditionalGeneration.from_pretrained(
        "Qwen/Qwen2-VL-2B-Instruct",
        trust_remote_code=True,
        torch_dtype=torch.bfloat16
    ).cuda().eval()
    
    processor = AutoProcessor.from_pretrained(
        "Qwen/Qwen2-VL-2B-Instruct",
        trust_remote_code=True
    )
    
# Extract financial data using Qwen
    financial_data = {}
    for page in relevant_pages:
        # Prepare prompt for financial data extraction
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": images[page["page_num"]],
                    },
                    {
                        "type": "text",
                        "text": "Extract the following financial metrics if present: Total Debt, Cash, EBITDA, Interest Expense, Total Assets, Total Equity. Return as JSON."
                    },
                ]
            }
        ]
        
        # Process with Qwen
        inputs = processor(messages)
        outputs = model.generate(**inputs)
        extracted = processor.decode(outputs)
        
        # Update financial data dictionary
        financial_data.update(extracted)
    
    return financial_data