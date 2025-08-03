"""
PDF parsing module for extracting text and structured data from financial documents.

This module provides functions to classify PDF pages and extract text with table formatting.
"""

from typing import List, Tuple, Dict, Any
import fitz
import pdfplumber
from pathlib import Path


def classify_pdf_pages(pdf_path: str) -> Tuple[List[int], List[int]]:
    """
    Classify PDF pages into text-based and image-based categories.
    
    Args:
        pdf_path (str): Path to the PDF file to analyze
        
    Returns:
        Tuple[List[int], List[int]]: A tuple containing:
            - text_pages: List of page indices (0-based) that contain extractable text
            - image_pages: List of page indices (0-based) that are image-based
            
    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        Exception: If there's an error opening or reading the PDF
        
    Example:
        >>> text_pages, image_pages = classify_pdf_pages("document.pdf")
        >>> print(f"Text pages: {text_pages}, Image pages: {image_pages}")
    """
    try:
        # Validate file exists
        if not Path(pdf_path).exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        doc = fitz.open(pdf_path)
        text_pages: List[int] = []
        image_pages: List[int] = []

        # Classify each page
        for i in range(len(doc)):
            page = doc[i]
            text = page.get_text("text")

            if text.strip():
                text_pages.append(i)
            else:
                image_pages.append(i)
        
        doc.close()
        
        return text_pages, image_pages
        
    except Exception as e:
        raise Exception(f"Error processing PDF {pdf_path}: {str(e)}")


def extract_structured_text(pdf_path: str, text_pages: List[int]) -> List[Dict[str, Any]]:
    """
    Extract structured text and tables from specified PDF pages in markdown format.
    
    Args:
        pdf_path (str): Path to the PDF file
        text_pages (List[int]): List of page indices (0-based) to extract text from
        
    Returns:
        List[Dict[str, Any]]: List of dictionaries containing structured page data.
            Each dictionary has:
            - 'page' (int): 1-based page number
            - 'markdown' (str): Extracted text and tables formatted as markdown
            
    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        Exception: If there's an error extracting text from the PDF
        
    Example:
        >>> text_pages = [0, 1, 2]
        >>> sections = extract_structured_text("document.pdf", text_pages)
        >>> for section in sections:
        ...     print(f"Page {section['page']}: {len(section['markdown'])} chars")
    """
    try:
        # Validate file exists
        if not Path(pdf_path).exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        markdown_sections: List[Dict[str, Any]] = []

        with pdfplumber.open(pdf_path) as pdf:
            for page_idx in text_pages:
                # Handle potential index out of range
                if page_idx >= len(pdf.pages):
                    continue
                    
                page = pdf.pages[page_idx]
                page_markdown = {
                    "page": page_idx + 1,  # Convert to 1-based page number
                    "markdown": f"\n## Page {page_idx + 1}\n"
                }

                # Extract text with better spacing preservation
                text = page.extract_text(x_tolerance=2, y_tolerance=2)
                if text:
                    # Don't strip the text to preserve spacing
                    page_markdown["markdown"] += f"\n{text}\n"

                # Extract and format tables
                tables = page.extract_tables()
                for table in tables:
                    if not table or not table[0]:
                        continue

                    # Create markdown table header
                    header = [cell if cell is not None else "" for cell in table[0]]
                    page_markdown["markdown"] += "\n\n| " + " | ".join(header) + " |\n"
                    page_markdown["markdown"] += "| " + " | ".join(["---"] * len(header)) + " |\n"

                    # Add table rows
                    for row in table[1:]:
                        safe_row = [cell if cell is not None else "" for cell in row]
                        page_markdown["markdown"] += "| " + " | ".join(safe_row) + " |\n"

                markdown_sections.append(page_markdown)

        return markdown_sections
        
    except Exception as e:
        raise Exception(f"Error extracting text from PDF {pdf_path}: {str(e)}")


def process_pdf_document(pdf_path: str, verbose: bool = True) -> Tuple[List[int], List[int], List[Dict[str, Any]], str]:
    """
    Complete PDF processing pipeline: classify pages and extract structured text.
    
    Args:
        pdf_path (str): Path to the PDF file to process
        verbose (bool): Whether to print processing information (default: True)
        
    Returns:
        Tuple containing:
            - text_pages: List of text-based page indices
            - image_pages: List of image-based page indices  
            - markdown_sections: List of structured text data from text pages
            - combined_results: String with filename header and all markdown content combined
            
    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        Exception: If there's an error processing the PDF
        
    Example:
        >>> text_pages, image_pages, sections, combined = process_pdf_document("document.pdf")
        >>> print(f"Found {len(text_pages)} text pages, {len(image_pages)} image pages")
    """
    try:
        if verbose:
            print(f"Processing PDF: {pdf_path}")
            
        # Step 1: Classify pages
        text_pages, image_pages = classify_pdf_pages(pdf_path)
        
        if verbose:
            print(f"Text-based pages: {text_pages}")
            print(f"Image-based pages: {image_pages}")
            
        # Step 2: Extract structured text from text pages
        markdown_sections = extract_structured_text(pdf_path, text_pages)
        
        if verbose:
            print(f"Extracted text from {len(markdown_sections)} pages")
        
        # Step 3: Create combined results with filename (preserve page headers)
        filename = Path(pdf_path).name
        combined_results = f"File: {filename}\n\n"
        for section in markdown_sections:
            # Keep the original content including page headers
            content = section['markdown'].strip()
            if content:
                combined_results += f"{content}\n\n"
        
        # Remove only trailing newlines, preserve internal spacing
        combined_results = combined_results.rstrip("\n")
            
        return text_pages, image_pages, markdown_sections, combined_results
        
    except Exception as e:
        raise Exception(f"Error in PDF processing pipeline for {pdf_path}: {str(e)}")
