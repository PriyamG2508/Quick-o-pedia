# Quick-o-Pedia AI

Quick-o-Pedia AI is a sophisticated Streamlit web application designed to enhance your learning and research process. This tool allows for the seamless extraction of content from any Wikipedia page, offering an interactive experience through an AI-powered chat interface and the convenience of downloading cleaned text for offline access. At its core, it leverages a Retrieval-Augmented Generation (RAG) model to deliver precise, context-aware answers to your queries, transforming static information into a dynamic and engaging learning tool.

## Features

  - **Clean Text Extraction**: Employs advanced scraping techniques to extract and sanitize text from any Wikipedia page, providing you with clean, readable content.
  - **AI-Powered Chat Interface**: Engage in a dialogue with an intelligent AI assistant capable of answering your questions based on the scraped Wikipedia content.
  - **RAG-Based Question Answering**: Utilizes a state-of-the-art Retrieval-Augmented Generation (RAG) model, powered by LangChain and ChromaDB, for highly accurate and contextually relevant responses.
  - **Content Preview and Download**: Offers the flexibility to preview the scraped content within the application and download the complete text as a `.txt` file for offline use.
  - **Elegant Dark-Themed UI**: A visually appealing and user-friendly interface designed for a comfortable and intuitive user experience.

## How to Use

1.  **Enter a Wikipedia Page Name**: In the designated text input field, type the name of the Wikipedia page you wish to explore (e.g., "Artificial Intelligence," "The History of Cinema").
2.  **Initiate Scraping**: Click the "Scrape Page" button to begin the process of fetching and cleaning the content from the specified Wikipedia page.
3.  **AI System Initialization**: Allow a few moments for the backend to initialize the RAG-based chat system.
4.  **Engage with the AI**: Once the system is ready, you can start asking questions about the content through the chat interface.
5.  **Access and Download Content**: Navigate to the "Content" tab to view the full text, or switch to the "Download" tab to save the content as a text file.

## Installation and Setup

To run this application locally, please follow these steps:

1.  **Clone the Repository**:

    ```bash
    git clone https://github.com/priyamg2508/quick-o-pedia.git
    cd quick-o-pedia
    ```

2.  **Set Up a Virtual Environment**:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**:
    Create a `.env` file in the root directory of the project and add your Groq API key as follows:

    ```
    GROQ_API_KEY="YOUR_GROQ_API_KEY"
    ```

5.  **Launch the Application**:

    ```bash
    streamlit run app.py
    ```

## Technologies Used

  - **Streamlit**: For building the interactive web application interface.
  - **LangChain**: As the framework for developing the RAG chain and managing the language model.
  - **Groq**: To leverage the high-performance Llama 3 language model for chat functionalities.
  - **ChromaDB**: As the vector store for the Retrieval-Augmented Generation system.
  - **Sentence-Transformers**: For generating the embeddings required for the vector store.
  - **Beautiful Soup**: For robust and efficient web scraping of Wikipedia content.
  - **Requests**: For handling HTTP requests to retrieve data from Wikipedia.
