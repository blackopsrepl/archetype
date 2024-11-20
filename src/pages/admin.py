import streamlit as st
import os
import shutil


def list_files(dir):
    return [
        f
        for f in os.listdir(dir)
        if os.path.isfile(os.path.join(dir, f)) and f.endswith(".md")
    ]


def read_md_file(path):
    with open(path, "r") as file:
        return file.read()


st.title("Admin Dashboard")

dir_path = "./chat-history"
if not os.path.exists(dir_path):
    os.mkdir(dir_path)

all_files = list_files(dir_path)
selected_file = st.selectbox("Choose a file", ["Select"] + all_files)

if selected_file != "Select":
    filepath = os.path.join(dir_path, selected_file)

    st.markdown("---")
    st.markdown(read_md_file(filepath), unsafe_allow_html=True)

    if st.button("Delete"):
        os.remove(filepath)
        st.success(f"Deleted {selected_file}")

    new_name = st.text_input("New name", "")
    if new_name:
        if st.button("Rename"):
            new_path = os.path.join(dir_path, new_name)
            shutil.move(filepath, new_path)
            st.success(f"Renamed to {new_name}")

if st.button("Reload"):
    st.experimental_rerun()
