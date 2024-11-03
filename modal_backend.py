# modal_backend.py
import modal

app = modal.App("stem")

# Create Modal image with required dependencies
image = (
    modal.Image.debian_slim()
    # Add NVIDIA CUDA repository and install CUDA
    .run_commands(
        "apt-get update && apt-get install -y wget",
        "wget https://developer.download.nvidia.com/compute/cuda/repos/debian11/x86_64/cuda-keyring_1.1-1_all.deb",
        "dpkg -i cuda-keyring_1.1-1_all.deb",
        "apt-get update",
        "apt-get install -y cuda-toolkit-12-1"  # Use 12.1 instead of 12.4
    )
    # Install basic dependencies
    .apt_install(
        "poppler-utils",
        "git"
    )
    # Install PyTorch with CUDA support
    .pip_install(
        "torch>=2.2.0",
        "numpy>=1.24.3",
        extra_index_url="https://download.pytorch.org/whl/cu121"  # Match CUDA version
    )
    # Install other dependencies
    .pip_install(
        "transformers>=4.37.2",
        "accelerate>=0.27.0",
        "pdf2image>=1.16.3",
        "python-dotenv>=1.0.0",
        "byaldi==0.0.2.post2"
    )
    # Install qwen-vl-utils separately
    .pip_install(
        "qwen-vl-utils"
    )
)

# Define environment parameters for the function
function_params = {
    "image": image,
    "gpu": "A10G",
    "timeout": 600,
    "secrets": [modal.Secret.from_name("HUGGINGFACE_TOKEN")]
}

@app.function(**function_params)
def process_pdf(pdf_file):
    # Import dependencies inside the function
    import os
    from pdf2image import convert_from_bytes
    from byaldi import RAGMultiModalModel
    import torch
    from transformers import AutoModelForCausalLM, AutoProcessor
    
    try:
        # Convert PDF to images
        images = convert_from_bytes(pdf_file.read())
        
        # Initialize ColPali model
        rag = RAGMultiModalModel.from_pretrained(
            "vidore/colpali",
            use_auth_token=os.environ["HUGGINGFACE_TOKEN"]
        )
        
        # Get relevant pages using ColPali
        relevant_pages = rag.search(
            "Find financial statements sections with balance sheet, income statement, or cash flow statement",
            images=images,
            k=3
        )
        
        # Initialize Qwen model
        model = AutoModelForCausalLM.from_pretrained(
            "Qwen/Qwen2-VL-2B-Instruct",
            trust_remote_code=True,
            torch_dtype=torch.float16,
            device_map="auto",
            use_auth_token=os.environ["HUGGINGFACE_TOKEN"]
        )
        
        processor = AutoProcessor.from_pretrained(
            "Qwen/Qwen2-VL-2B-Instruct",
            trust_remote_code=True,
            use_auth_token=os.environ["HUGGINGFACE_TOKEN"]
        )
        
        # Extract financial data using Qwen
        financial_data = {}
        for page in relevant_pages:
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
                            "text": """
                            Extract these financial metrics if present in the Russian financial statements:
                            - Total Debt (Общий долг)
                            - Cash (Денежные средства)
                            - EBITDA
                            - Interest Expense (Процентные расходы)
                            - Total Assets (Общие активы)
                            - Total Equity (Собственный капитал)
                            Return as JSON with metric names in English and values as numbers.
                            """
                        },
                    ]
                }
            ]
            
            # Process with Qwen
            inputs = processor(messages, return_tensors="pt").to("cuda")
            with torch.cuda.amp.autocast():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=500,
                    temperature=0.2,
                    do_sample=False
                )
            extracted = processor.batch_decode(outputs, skip_special_tokens=True)[0]
            
            try:
                import json
                extracted_data = json.loads(extracted)
                financial_data.update(extracted_data)
            except json.JSONDecodeError:
                print(f"Failed to parse JSON for page {page['page_num']}")
                continue
        
        return financial_data

    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return None

if __name__ == "__main__":
    app.deploy()