import streamlit as st
from service1_api import get_next_arrivals
from service2_semantic import ask_ttc_question
from service3_router import smart_ttc_assistant

page = st.sidebar.selectbox(
    "Choose Service",
    ["Real-Time Arrivals", "Ask TTC Questions","Smart TTC Assistant"]
)

if page == "Real-Time Arrivals":
    st.title("TTC Real-Time Arrivals")
    st.write("Enter a TTC Stop ID to get next arrivals")

    # Input
    stop_id = st.text_input("Stop ID", placeholder="e.g., 8213")

    # Button
    if st.button("Get Next Arrivals"):
        if stop_id:
            results = get_next_arrivals(stop_id)

            # Output
            for line in results:
                st.write(line)
        else:
            st.warning("Please enter a Stop ID")

elif page == "Ask TTC Questions":
    st.title("Ask TTC Questions")
    
    question = st.text_input("Ask about TTC", placeholder="You will get answers from the stored knowledge base.")

    if st.button("Ask"):
        if question:
            answer = ask_ttc_question(question)
            st.write(answer)
        else:
            st.warning("Please enter a question")

elif page == "Smart TTC Assistant":
    st.title("Smart TTC Assistant")
    st.write("Your assistant knows general information about the TTC system — how subways, buses, and streetcars work, fares and PRESTO rules, accessibility, service alerts, trip planning basics, route naming, night service, etiquette, and common rider questions.")
    user_input = st.text_input("Ask anything about TTC", placeholder='Next bus at stop 8213' or 'Tell me about Line 1')

    if st.button("Ask Assistant", key="assistant_btn"):
        if user_input:
            response = smart_ttc_assistant(user_input)

            if isinstance(response, dict):
                st.write(response["answer"])
                st.caption(f"Source: {response['source']}")
            else:
                st.write(response)
        else:
            st.warning("Please enter a question")

