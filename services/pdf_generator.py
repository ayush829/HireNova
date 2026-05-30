import re
import os
from urllib.parse import urlparse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def markdown_to_html_tags(text: str) -> str:
    """
    Translates basic markdown (bold **text**, italic *text*, links [text](url)) 
    and extracts raw URLs / emails, turning them into ReportLab-compatible XML tags (<b>, <i>, <a>).
    Automatically ensures all links have absolute protocols (https://, mailto:) so they are clickable.
    """
    if not text:
        return ""
        
    # 1. Escape XML tags that might interfere, except what we explicitly allow
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    
    # 2. Standardize markdown bold **word** -> <b>word</b>
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    
    # 3. Standardize markdown italic *word* -> <i>word</i>
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    
    # 4. Master Link Parser Callback
    def link_parser_callback(match):
        full_match = match.group(0)
        
        # A. HTML tag (like <b> or &lt;) - return as is
        if full_match.startswith('<') and full_match.endswith('>'):
            return full_match
            
        # B. Markdown link [Label](URL)
        if full_match.startswith('[') and '](' in full_match:
            m = re.match(r'\[([^\]]+)\]\(([^)]+)\)', full_match)
            if m:
                label = m.group(1).strip()
                url = m.group(2).strip()
                
                # Handle common truncated domains to be extra resilient
                url_lower = url.lower()
                if "github" in url_lower and "github.com" not in url_lower:
                    url = url.replace("github", "github.com")
                elif "linkedin" in url_lower and "linkedin.com" not in url_lower:
                    url = url.replace("linkedin", "linkedin.com")
                elif "leetcode" in url_lower and "leetcode.com" not in url_lower:
                    url = url.replace("leetcode", "leetcode.com")
                
                # Sanitize and ensure absolute URL
                if not (url.startswith("http://") or url.startswith("https://") or url.startswith("mailto:")):
                    if "@" in url:
                        url = f"mailto:{url}"
                    else:
                        url = f"https://{url}"
                return f'<a href="{url}" color="#2563eb"><b>{label}</b></a>'
                
        # C. Email address
        if "@" in full_match and not (full_match.startswith("http://") or full_match.startswith("https://")):
            email = full_match.strip()
            return f'<a href="mailto:{email}" color="#2563eb"><b>{email}</b></a>'
            
        # D. Raw URL (HTTP/HTTPS/WWW or domain URLs like github.com/username)
        url = full_match.strip()
        href_url = url
        
        # Handle common truncated domains to be extra resilient
        url_lower = href_url.lower()
        if "github" in url_lower and "github.com" not in url_lower:
            href_url = href_url.replace("github", "github.com")
        elif "linkedin" in url_lower and "linkedin.com" not in url_lower:
            href_url = href_url.replace("linkedin", "linkedin.com")
        elif "leetcode" in url_lower and "leetcode.com" not in url_lower:
            href_url = href_url.replace("leetcode", "leetcode.com")
            
        if href_url.startswith("www."):
            href_url = f"https://{href_url}"
        elif not href_url.startswith("http://") and not href_url.startswith("https://"):
            href_url = f"https://{href_url}"
            
        # Dynamically extract domain name to display as clean label (Step 7)
        try:
            domain = urlparse(href_url).netloc
            domain = domain.replace("www.", "")
            label = domain.split(".")[0].capitalize()
            # If domain parsing results in nothing, fallback
            if not label:
                label = "Website"
        except Exception:
            label = "Website"
            
        return f'<a href="{href_url}" color="#2563eb"><b>{label}</b></a>'

    # Master regex to match:
    # - HTML tags: <[^>]+>
    # - Markdown links: \[([^\]]+)\]\(([^)]+)\)
    # - Raw absolute URLs: https?://[^\s<()]+
    # - Raw WWW URLs: www\.[^\s<()]+
    # - Raw code/profile domains: (?:github|linkedin)\.com/[^\s<()]+
    # - Email addresses: [a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}
    master_pattern = r'(<[^>]+>|\[[^\]]+\]\([^)]+\)|https?://[^\s<()]+|www\.[^\s<()]+|(?:github|linkedin)\.com/[^\s<()]+|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
    
    text = re.sub(master_pattern, link_parser_callback, text)
    
    # 5. Put back escaped angle brackets for our generated HTML tags
    text = text.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
    text = text.replace("&lt;i&gt;", "<i>").replace("&lt;/i&gt;", "</i>")
    
    return text

def create_pdf(content: str, filename: str) -> bool:
    """
    Parses a markdown formatted resume string and builds a highly professional
    styled PDF document using ReportLab.
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # 0.5-inch margins for resume formatting (36 points)
        doc = SimpleDocTemplate(
            filename,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        
        styles = getSampleStyleSheet()
        
        # Define clean, professional color palette
        COLOR_PRIMARY = colors.HexColor("#0f172a")    # Slate 900 (Deep Navy/Black)
        COLOR_SECONDARY = colors.HexColor("#2563eb")  # Blue 600 (Accents)
        COLOR_BODY = colors.HexColor("#334155")       # Slate 700 (Dark Gray Body)
        COLOR_MUTED = colors.HexColor("#64748b")      # Slate 500 (Muted Metadata)
        
        # Custom Typography Styles
        style_title = ParagraphStyle(
            'ResumeTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=COLOR_PRIMARY,
            alignment=1,  # Centered
            spaceAfter=6
        )
        
        style_subtitle = ParagraphStyle(
            'ResumeSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=12,
            textColor=COLOR_MUTED,
            alignment=1,  # Centered
            spaceAfter=12
        )
        
        style_h1 = ParagraphStyle(
            'ResumeH1',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=16,
            textColor=COLOR_PRIMARY,
            spaceBefore=12,
            spaceAfter=4,
            keepWithNext=True
        )
        
        style_h2 = ParagraphStyle(
            'ResumeH2',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=14,
            textColor=COLOR_BODY,
            spaceBefore=6,
            spaceAfter=3,
            keepWithNext=True
        )
        
        style_body = ParagraphStyle(
            'ResumeBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13.5,
            textColor=COLOR_BODY,
            spaceAfter=5
        )
        
        style_bullet = ParagraphStyle(
            'ResumeBullet',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13.5,
            textColor=COLOR_BODY,
            leftIndent=15,
            firstLineIndent=-10,
            spaceAfter=3
        )
        
        elements = []
        lines = content.split('\n')
        
        is_bullet_mode = False
        
        for line in lines:
            trimmed = line.strip()
            if not trimmed:
                continue
                
            # Parse Resume Title (# Full Name)
            if trimmed.startswith('# '):
                name = trimmed[2:].strip()
                elements.append(Paragraph(markdown_to_html_tags(name), style_title))
                
            # Parse Resume Subtitle (Contact info below Title)
            elif trimmed.startswith('**') and trimmed.endswith('**') and len(elements) == 1:
                # If the line directly under the title is bold, treat as contact info
                contact_info = trimmed[2:-2].strip()
                elements.append(Paragraph(markdown_to_html_tags(contact_info), style_subtitle))
                
            # Check if this line looks like standard contact info (e.g. Email | Phone)
            elif any(indicator in trimmed.lower() for indicator in ['@', 'linkedin.com', 'github.com', ' | ']) and len(elements) <= 2:
                elements.append(Paragraph(markdown_to_html_tags(trimmed), style_subtitle))
                
            # Parse Section Headers (## Section)
            elif trimmed.startswith('## '):
                section_name = trimmed[3:].strip()
                
                # Add spacing before sections unless it is the very first section
                if len(elements) > 2:
                    elements.append(Spacer(1, 6))
                    
                elements.append(Paragraph(markdown_to_html_tags(section_name), style_h1))
                # Add a clean section divider line below Heading 1
                elements.append(HRFlowable(
                    width="100%", 
                    thickness=0.8, 
                    color=COLOR_SECONDARY, 
                    spaceBefore=2, 
                    spaceAfter=6
                ))
                
            # Parse Sub-Headers (### Role / Company / School)
            elif trimmed.startswith('### '):
                sub_section = trimmed[4:].strip()
                elements.append(Paragraph(markdown_to_html_tags(sub_section), style_h2))
                
            # Parse Bullet Points (- Bullet or * Bullet)
            elif trimmed.startswith('- ') or trimmed.startswith('* ') or trimmed.startswith('• '):
                bullet_content = trimmed[2:].strip()
                bullet_html = f"&bull; {markdown_to_html_tags(bullet_content)}"
                elements.append(Paragraph(bullet_html, style_bullet))
                
            # Regular text paragraph
            else:
                # Standard paragraph
                elements.append(Paragraph(markdown_to_html_tags(trimmed), style_body))
                
        # Build the document
        doc.build(elements)
        return True
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        # Fallback to simple reportlab document if advanced fails
        try:
            pdf = SimpleDocTemplate(filename, pagesize=letter)
            styles = getSampleStyleSheet()
            # Basic paragraph list
            elements = []
            for line in content.split('\n'):
                if line.strip():
                    elements.append(Paragraph(markdown_to_html_tags(line), styles["Normal"]))
                    elements.append(Spacer(1, 6))
            pdf.build(elements)
            return True
        except Exception as fallback_err:
            print(f"Fallback PDF generation also failed: {str(fallback_err)}")
            return False
