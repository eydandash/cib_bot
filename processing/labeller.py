from typing import List, Tuple

# Define a function that takes in the ar_pdf_links and for each one chunks it to a year, using the / position fromt the printed out list, the quarter, whether it is standalone or consolidated, and the date
def extract_path_keywords_ar(pdf_links: List[str]) -> List[Tuple[str, str, str, str, str]]:
    """
    Extract metadata from Arabic PDF links including year, language, quarter, statement type, and URL.
    
    Args:
        pdf_links: List of PDF URLs from the CIB Arabic website
        
    Returns:
        List of tuples containing (year, language, quarter, cs_sa, link) for each PDF
    """
    parsed_links = []
    language = 'ar'

    for link in pdf_links:
        parts = link.split('/')
        year_language = parts[11].split('-')
        year = year_language[0]
        concatenated = ''.join(parts[11:]).lower()
        if 'q1' in concatenated or 'march' in concatenated:
            quarter = 'Q1'
        elif 'q2' in concatenated or 'june' in concatenated:
            quarter = 'Q2'
        elif 'q3' in concatenated or 'september' in concatenated:
            quarter = 'Q3'
        elif 'q4' in concatenated or 'december' in concatenated:
            quarter = 'Q4'
        else:
            quarter = 'Unknown'

        if 'consolidat' in concatenated or 'cs' in concatenated or 'condensed' in concatenated:
            cs_sa = 'consolidated'
        elif 'standalone' in concatenated or 'sa' in concatenated or 'separate' in concatenated:
            cs_sa = 'standalone'
        else:
            cs_sa = 'Unknown'
        parsed_links.append((year, language, quarter, cs_sa, link))
    
    # Print first 3 samples
    print("Arabic PDF metadata samples:")
    for i, sample in enumerate(parsed_links[:3]):
        print(f"Sample {i+1}: {sample}")
    
    return parsed_links

# Define a function that takes in the ar_pdf_links and for each one chunks it to a year, using the / position fromt the printed out list, the quarter, whether it is standalone or consolidated, and the date
def extract_path_keywords_en(pdf_links: List[str]) -> List[Tuple[str, str, str, str, str]]:
    """
    Extract metadata from English PDF links including year, language, quarter, statement type, and URL.
    
    Args:
        pdf_links: List of PDF URLs from the CIB English website
        
    Returns:
        List of tuples containing (year, language, quarter, cs_sa, link) for each PDF
    """
    parsed_links = []
    language = 'en'

    for link in pdf_links:
        parts = link.split('/')
        year = parts[10]
        concatenated = ''.join(parts[11:]).lower()
        if 'q1' in concatenated or 'march' in concatenated:
            quarter = 'Q1'
        elif 'q2' in concatenated or 'june' in concatenated:
            quarter = 'Q2'
        elif 'q3' in concatenated or 'september' in concatenated:
            quarter = 'Q3'
        elif 'q4' in concatenated or 'december' in concatenated:
            quarter = 'Q4'
        else:
            quarter = 'Unknown'

        if 'consolidat' in concatenated or 'cs' in concatenated or 'condensed' in concatenated:
            cs_sa = 'consolidated'
        elif 'standalone' in concatenated or 'sa' in concatenated or 'separate' in concatenated:
            cs_sa = 'standalone'
        else:
            cs_sa = 'Unknown'
        parsed_links.append((year, language, quarter, cs_sa, link))
    
    # Print first 3 samples
    print("English PDF metadata samples:")
    for i, sample in enumerate(parsed_links[:3]):
        print(f"Sample {i+1}: {sample}")
    
    return parsed_links
