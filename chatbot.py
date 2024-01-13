from openai import OpenAI
import utils as ut
import streamlit as st
import codecs

st.title("AI Financial Times Chatbot for Mithril Security")

client = OpenAI(api_key=codecs.decode("fx-ZVcU4xyr3d0rpO1LTCbYG3OyoxSWT3l8L6HUVzdEQae6vamL", "rot_13"))

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4-1106-preview"

if "messages" not in st.session_state:
    st.session_state.messages = []
if "questions" not in st.session_state:
    st.session_state.questions = []
if "backend_thread" not in st.session_state:
    st.session_state.backend_thread = [
        {
        "role": "system",
        "content": ut.prompt
        },
    ]
if "fetch" not in st.session_state:
    st.session_state.fetch = True

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.questions.append(prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        ## Process the query, fetch FT articles, and prompt the agent
        ## Also display the links to the FT articles and update the status of fetching the articles
        rag = ""
        if st.session_state.fetch:
            with st.status("Finding up-to-date information [Click to view details]..."):

                st.write("Generating query...")
                query = client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=[
                        {"role":"system", "content":ut.prompt},
                        {"role":"user", "content":ut.generate_query_prompt(prompt, st.session_state.questions)}
                    ],
                    max_tokens=64,
                    stop=["\n"],
                    stream=False,
                ).choices[0].message.content.strip().replace('"', '')
                
                search_url = ut.get_ft_search_url(query)
                st.write(f"Searching the Financial Times for {query}...")
                ft_urls = ut.get_ft_urls(search_url)
                art_infos = []
                st.write("Fetching articles...")
                for art_info in ut.get_article_infos(ft_urls):
                    st.write(f"Fetched article: {art_info['title']}.")
                    art_infos.append(art_info)
                rag = ut.generate_article_rag(art_infos)
                st.write("Prompting the agent")

        backend_prompt = ut.generate_prompt(prompt, rag)

        st.session_state.backend_thread.append(
            {"role": "user", "content": backend_prompt}
        )
        print(backend_prompt)


        message_placeholder = st.empty()
        full_response = ""
        for response in client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.backend_thread
            ],
            stream=True,
        ):
            full_response += (response.choices[0].delta.content or "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.session_state.backend_thread.append({
        "role": "assistant",
        "content": full_response
    })

st.toggle("Toggle article fetching", value=st.session_state.fetch, on_change=lambda: st.session_state.update({"fetch": not st.session_state.fetch}))