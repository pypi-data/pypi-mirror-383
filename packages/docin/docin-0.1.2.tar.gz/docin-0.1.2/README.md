# README for docin OCR Tool

## Overview
**docin** is a lightweight document processing toolkit that combines OCR (Optical Character Recognition) and intelligent document analysis. It features two main components:

1. **OCR Engine**: Powered by the Mistral API, it extracts text and images from PDF and image files, converting them into clean, structured Markdown format.

2. **LangQuery**: An intelligent document analysis tool that uses LangChain and spaCy to extract structured information through natural language queries and visualize named entities.

---

## Features

### OCR Capabilities
- Automatically detects PDF or image input  
- Performs OCR using the Mistral API  
- Exports results as Markdown (.md)  
- Optionally includes extracted images  
- Displays real-time progress for multi-page documents  
- Prevents accidental overwriting of output files  

### Document Analysis
- Extract structured information using natural language queries
- Visualize named entities with interactive highlighting
- Customize prompts and examples for specific use cases
- Return results in JSON format for easy processing

---

## Requirements
- Python 3.8+  
- A valid Mistral API key  
- A LangChain-compatible language model (for document analysis)
- spaCy with 'en_core_web_sm' model (auto-installed)

---

## Installation
```bash
pip install docin
```

The spaCy model 'en_core_web_sm' will be automatically downloaded during installation.

---

## Usage

### OCR Processing
```python
from ocr import MistOcr

# Initialize with your Mistral API key
ocr = MistOcr(api_key='your_mistral_api_key')

# Run OCR on a PDF or image file
ocr.doc_to_md(
    filename='path/to/document.pdf',
    output_filename='output/result.md',
    include_image=False,        # Include embedded or saved images (optional)
    return_response=False      # Return OCR response (optional)
)
```

### Document Analysis with LangQuery
```python
from ocr.query import LangQuery

# Initialize with your LangChain model
query = LangQuery(llm=your_llm)

# Load and analyze a document
query.load_document("Your document text here")

# Extract information using natural language
response = query.query_document("Find all company names and locations")

# Visualize results (in Jupyter/IPython)
query.render(response)
```

You can customize the analysis by setting different examples:
```python
# Set custom examples for specific entity types
query.set_examples("""
{
    'companies': ['Example Corp', 'Tech Inc'],
    'dates': ['2023-01-01'],
    'locations': ['New York']
}
""")
```

---

## Output

### OCR Output
- Saves extracted text in a Markdown (.md) file  
- Creates an `images/` folder in the same directory for any extracted images  
- Displays progress during export  
- Returns an OCR response object when `return_response=True`  

### LangQuery Output
- Returns structured JSON with extracted entities
- Provides interactive entity highlighting in Jupyter/IPython
- Supports customizable response formats through examples

---

## Supported File Types
- PDF (.pdf)  
- Image formats: .jpg, .jpeg, .png, .bmp, .tiff  
- LangQuery works with any text content

---

## Error Handling
- Raises `ValueError` for unsupported file types  
- Prompts before overwriting existing files  
- Logs warnings for missing or invalid image data  
- Validates document loading for LangQuery
- Ensures proper model initialization

---

## Notes
- For OCR: Use high-resolution images (≥300 DPI) for best accuracy
- Supports multi-page PDFs and large documents
- Extracted images are saved with unique IDs in the `images/` directory
- LangQuery works best with well-structured text content
- Entity visualization requires Jupyter/IPython environment

---

## Example Output

### OCR Output
**Markdown file:**
```
# Page 1
Extracted text...

# Page 2
More extracted text...
```

**Images folder:**
```
images/
 ├── image_1.png
 ├── image_2.jpg
```

### LangQuery Output
**JSON Response:**
```json
{
    "companies": ["Acme Corp", "TechStart Inc"],
    "locations": ["New York", "San Francisco"],
    "dates": ["2023-01-15"]
}
```

**Visual Output:**
- Interactive highlighting of found entities in the document text
- Color-coded entity types for easy identification

---

## Author
Ime Inyang

## License
MIT

## Version
0.1.2