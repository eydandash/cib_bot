# Welcome to the CIB Financial Assistant! 📊

## Introduction 👋
This application is designed to help you explore and analyze the financial statements of the Commercial International Bank (CIB) in Egypt. Whether you're looking for specific figures, trends, or insights, this assistant is here to make your experience seamless and efficient.

## Features 🌟
- **Automated Data Retrieval:** The application uses web scraping to fetch financial statements directly from the CIB website.
- **PDF Processing:** Extracts text and tables from financial statement PDFs, leveraging OCR for image-based pages.
- **Contextual Search:** Enables you to ask specific questions about financial data, using advanced embeddings and vector search.
- **Language Model Integration:** Provides accurate answers by combining retrieved data with a powerful language model.

## How It Works 🛠️
1. **Web Scraping:** The application uses Selenium to scrape PDF links from the CIB website for both Arabic and English versions of financial statements.
2. **PDF Analysis:** Extracts text and tables from the PDFs, categorizing pages as text-based or image-based for efficient processing.
3. **Data Storage:** Stores extracted data in a vector database (Qdrant) for fast and contextual retrieval.
4. **Question Answering:** Combines retrieved data with a language model (Mistral/Ollama) to answer user queries accurately.
5. **Interactive Chat:** Provides a user-friendly interface for asking questions in English or Arabic.

## Get Started 📚
- **Documentation:** Learn more about the application and its features in the [Chainlit Documentation](https://docs.chainlit.io).
- **Community Support:** Join our [Chainlit Discord](https://discord.gg/k73SQ3FyUh) to connect with other developers.

## Customization 🛠️
To personalize this welcome screen, edit the `chainlit.md` file located at the root of your project. Want to remove the welcome screen? Simply leave this file empty.

## Happy Exploring! 💻😊
Dive into the world of financial data with ease and precision. Let’s uncover insights together!
