from rag_function import rag
import streamlit as st
from chatbot_app import answer_question, qachatbot
from chatbot_app_conv_function import chatbot_conv

# Streamlit app
st.title("Financial GPT")

# set initial message
if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello there, how can I help you"}
    ]

if "messages" in st.session_state.keys():
    # display messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])


# get user input
user_prompt = st.chat_input()

if user_prompt is not None:
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.write(user_prompt)

if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Loading..."):
            answer, related_q1, related_q2, related_q3 = chatbot_conv(user_prompt)
            st.write(answer)
            st.write("Some follow up questions you might be interested in:")
            st.write(related_q1)
            st.write(related_q2)
            st.write(related_q3)
            
            # button_related_q1 = st.button(related_q1)
            # button_related_q2 = st.button(related_q2)
            # button_related_q3 = st.button(related_q3)
            # if button_related_q1:
            #     st.session_state.messages.append({"role": "user", "content": related_q1})
            #     with st.chat_message("user"):
            #         st.write(related_q1)
            # elif button_related_q2:
            #     st.session_state.messages.append({"role": "user", "content": related_q2})
            #     with st.chat_message("user"):
            #         st.write(related_q2)
            # elif button_related_q3:
            #     st.session_state.messages.append({"role": "user", "content": related_q3})
            #     with st.chat_message("user"):
            #         st.write(related_q3)
            # else:
            #     pass
    new_ai_message = {"role": "user", "content": answer}
    st.session_state.messages.append(new_ai_message)