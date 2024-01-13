# This repository contains the code for the Financial Analyst chatbot for Mithril Security
By Hengyuan Zhang

The chatbot is built with streamlit, selenium, and the openai backend.

### Execution

#### Docker

If you have the docker image tagged `streamlit`, then run the command `docker run -p 8501:8501 streamlit`. Then, navigate to `localhost:8501` to use the chat.


To build the docker image from scratch, run `docker build -t streamlit .` in the root directory.

#### Python
Run `pip install requirements.txt`, followed by `streamlit run chatbot.py`

### What the app does

After the user enters a question, the app prompts GPT-4 to generate a query to search for relevant articles in the Financial Times. Then it uses selenium and archive.fo to scrape article content, finally feeding it through retrieval-augmented generation to GPT-4 to generate a response with context from the articles.


Articles are by default fetched for every user message, but this can be toggled manually for a quicker experience if the existing articles are sufficient to answer the question.