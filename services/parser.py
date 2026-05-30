import pdfplumber
from docx import Document
import io

def extract_pdf_hyperlinks(page) -> list:
    """
    Extracts underlying hyperlink annotations and their visible text from a PDF page safely.
    """
    links = []
    if not hasattr(page, 'hyperlinks') or not page.hyperlinks:
        return links
        
    for link in page.hyperlinks:
        uri = link.get('uri')
        if not uri:
            continue
            
        # Get bounding box coordinates safely
        x0 = link.get('x0')
        top = link.get('top')
        x1 = link.get('x1')
        bottom = link.get('bottom')
        
        anchor_text = ""
        if None not in (x0, top, x1, bottom):
            try:
                # Try to crop the page to get the text inside the bounding box
                # Expand coordinates by 2 points to ensure full text is captured
                cropped = page.crop((x0 - 2, top - 2, x1 + 2, bottom + 2), strict=False)
                anchor_text = cropped.extract_text() or ""
            except Exception:
                pass
                
        if not anchor_text.strip():
            # If no visible text is inside the bounding box, try using the URI's domain as a label
            anchor_text = "Link"
            
        links.append((anchor_text.strip(), uri.strip()))
    return links

def read_pdf(file) -> str:
    """
    Extracts text and hyperlink annotations from a PDF file using pdfplumber.
    Supports file paths or file-like objects (like Streamlit uploads).
    """
    text = ""
    links = []
    try:
        # Check if the input is already a file-like object or a path
        if isinstance(file, (str, bytes)):
            pdf_source = file
        else:
            # For Streamlit UploadedFile, read as bytes and wrap in BytesIO
            pdf_source = io.BytesIO(file.read())
            # Reset file pointer after reading so other operations can use it
            file.seek(0)
            
        with pdfplumber.open(pdf_source) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                
                # Extract page links
                page_links = extract_pdf_hyperlinks(page)
                links.extend(page_links)
    except Exception as e:
        return f"Error reading PDF file: {str(e)}"
    
    # Clean parsed text
    cleaned_text = text.strip()
    
    # Append structured hyperlinks list at the end
    if links:
        # Avoid duplicate links
        unique_links = []
        seen = set()
        for label, url in links:
            key = (label.lower(), url.lower())
            if key not in seen:
                seen.add(key)
                unique_links.append((label, url))
                
        cleaned_text += "\n\n=== EXTRACTED HYPERLINKS ===\n"
        for label, url in unique_links:
            cleaned_text += f'- "{label}": {url}\n'
            
    return cleaned_text

def read_docx(file) -> str:
    """
    Extracts text and hyperlinks from a DOCX file using python-docx.
    Supports file paths or file-like objects (like Streamlit uploads).
    """
    try:
        if isinstance(file, (str, bytes)):
            doc = Document(file)
        else:
            # Wrap the upload bytes in BytesIO
            doc = Document(io.BytesIO(file.read()))
            # Reset file pointer
            file.seek(0)
            
        text = "\n".join([p.text for p in doc.paragraphs])
        
        # Also extract table text to be comprehensive
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    text += f"\n{cell.text}"
                    
        # Extract Docx Hyperlinks
        links = []
        for para in doc.paragraphs:
            if hasattr(para, 'hyperlinks') and para.hyperlinks:
                for link in para.hyperlinks:
                    if link.text and link.address:
                        links.append((link.text.strip(), link.address.strip()))
                        
        cleaned_text = text.strip()
        
        if links:
            # Avoid duplicate links
            unique_links = []
            seen = set()
            for label, url in links:
                key = (label.lower(), url.lower())
                if key not in seen:
                    seen.add(key)
                    unique_links.append((label, url))
                    
            cleaned_text += "\n\n=== EXTRACTED HYPERLINKS ===\n"
            for label, url in unique_links:
                cleaned_text += f'- "{label}": {url}\n'
                
        return cleaned_text
    except Exception as e:
        return f"Error reading DOCX file: {str(e)}"
