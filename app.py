import streamlit as st
import requests

st.set_page_config(page_title="FDNC + Name Checker", layout="centered")

st.title("🔍 FDNC & Name Search Tool")

# ---------------------------
# Upload TXT File (Names DB)
# ---------------------------
st.sidebar.header("📂 Upload Name File")

uploaded_file = st.sidebar.file_uploader(
    "Upload Name.txt file (one name per line)",
    type=["txt"]
)

names_list = []

if uploaded_file is not None:
    content = uploaded_file.read().decode("utf-8")
    names_list = [line.strip().lower() for line in content.splitlines() if line.strip()]
    st.sidebar.success(f"File uploaded ✅ ({len(names_list)} names loaded)")

# ---------------------------
# Mode Selection
# ---------------------------
mode = st.selectbox("Select Search Type", ["FDNC Number Search", "Name Search"])

# ---------------------------
# NAME SEARCH
# ---------------------------
if mode == "Name Search":
    st.subheader("👤 Name Lookup")

    if not names_list:
        st.warning("Please upload Name.txt file first from sidebar")
    else:
        name_input = st.text_input("Enter Name")

        if st.button("Search Name"):
            if name_input.strip() == "":
                st.error("Please enter a name")
            else:
                search_name = name_input.strip().lower()

                if search_name in names_list:
                    st.success("✅ Match Found")
                else:
                    st.error("❌ No Result Found")

# ---------------------------
# NUMBER SEARCH (FDNC API)
# ---------------------------
elif mode == "FDNC Number Search":
    st.subheader("📞 Number Lookup (FDNC)")

    number = st.text_input("Enter Phone Number")

    if st.button("Check Number"):
        if number.strip() == "":
            st.error("Please enter a number")
        else:
            try:
                API_KEY = "nmngtEbbgaK8eR64H8Zt"

                url = f"https://api.blacklistalliance.net/lookup?key={API_KEY}&ver=v3&resp=raw&phone={number}"

                response = requests.get(url)

                if response.status_code == 200:
                    data = response.text

                    if data.strip():
                        st.success("✅ FDNC Response Received")
                        st.code(data)
                    else:
                        st.error("❌ No Record Found")
                else:
                    st.error(f"API Error: {response.status_code}")

            except Exception as e:
                st.error(f"Error: {e}")