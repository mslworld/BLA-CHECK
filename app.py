import streamlit as st
import requests
from typing import Optional, Set
import io

def load_names_from_file(uploaded_file) -> Optional[Set[str]]:
    """Load names from uploaded text file into a set for efficient searching."""
    try:
        if uploaded_file is not None:
            # Read file content
            stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
            names = set()
            
            # Read each line and add to set (strip whitespace)
            for line in stringio:
                name = line.strip()
                if name:  # Only add non-empty lines
                    names.add(name.lower())  # Store in lowercase for case-insensitive search
            
            return names
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None

def search_name(names_set: Set[str], search_term: str) -> bool:
    """Perform case-insensitive exact match search."""
    if not search_term.strip():
        return False
    
    # Convert search term to lowercase for case-insensitive comparison
    search_term_lower = search_term.strip().lower()
    return search_term_lower in names_set

def call_fdnc_api(phone_number: str) -> Optional[str]:
    """Call the FDNC API with the given phone number."""
    try:
        if not phone_number.strip():
            return None
        
        # Clean phone number (remove spaces, dashes, etc.)
        clean_phone = ''.join(c for c in phone_number if c.isdigit())
        
        if not clean_phone:
            return None
        
        api_url = f"https://api.blacklistalliance.net/lookup?key=nmngtEbbgaK8eR64H8Zt&ver=v3&resp=raw&phone={clean_phone}"
        
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        
        return response.text.strip()
        
    except requests.exceptions.RequestException as e:
        st.error(f"API call failed: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error processing API response: {str(e)}")
        return None

def main():
    st.set_page_config(
        page_title="Name & FDNC Search",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title("🔍 Name & FDNC Search Application")
    
    # Initialize session state
    if 'names_set' not in st.session_state:
        st.session_state.names_set = None
    if 'file_uploaded' not in st.session_state:
        st.session_state.file_uploaded = False
    
    # Sidebar for file upload
    with st.sidebar:
        st.header("📁 File Upload")
        uploaded_file = st.file_uploader(
            "Upload a .txt file with names (one per line)",
            type=['txt'],
            help="Upload a text file containing names, with each name on a separate line."
        )
        
        if uploaded_file is not None:
            if not st.session_state.file_uploaded or uploaded_file != st.session_state.get('last_file'):
                with st.spinner("Loading names..."):
                    names = load_names_from_file(uploaded_file)
                    if names:
                        st.session_state.names_set = names
                        st.session_state.file_uploaded = True
                        st.session_state.last_file = uploaded_file
                        st.success(f"✅ Loaded {len(names)} names successfully!")
                    else:
                        st.session_state.file_uploaded = False
                        st.error("❌ Failed to load names from file.")
        
        # Display file status
        if st.session_state.file_uploaded:
            st.info(f"📊 {len(st.session_state.names_set)} names loaded")
            if st.button("Clear File"):
                st.session_state.names_set = None
                st.session_state.file_uploaded = False
                st.session_state.last_file = None
                st.rerun()
    
    # Main content area
    st.header("Search Mode")
    
    # Mode selection
    search_mode = st.selectbox(
        "Select search mode:",
        ["Name Search", "FDNC Number Search"],
        index=0,
        help="Choose between searching names in the uploaded file or looking up FDNC records."
    )
    
    if search_mode == "Name Search":
        st.subheader("👤 Name Search")
        
        # Check if file is uploaded
        if not st.session_state.file_uploaded:
            st.warning("⚠️ Please upload a .txt file first to enable name search.")
            return
        
        # Name search interface
        search_name_input = st.text_input(
            "Enter name to search:",
            placeholder="Type a name...",
            help="Enter the exact name to search for (case-insensitive)"
        )
        
        if st.button("Search Name", type="primary"):
            if search_name_input.strip():
                with st.spinner("Searching..."):
                    is_found = search_name(st.session_state.names_set, search_name_input)
                    
                    if is_found:
                        st.success("✅ Match Found")
                        st.balloons()
                    else:
                        st.error("❌ No Result Found")
            else:
                st.warning("⚠️ Please enter a name to search.")
    
    elif search_mode == "FDNC Number Search":
        st.subheader("📞 FDNC Number Search")
        
        # FDNC search interface
        phone_input = st.text_input(
            "Enter phone number:",
            placeholder="Enter phone number (e.g., 1234567890)",
            help="Enter the phone number to lookup in the FDNC database"
        )
        
        if st.button("Search FDNC", type="primary"):
            if phone_input.strip():
                with st.spinner("Searching FDNC database..."):
                    api_response = call_fdnc_api(phone_input)
                    
                    if api_response is not None:
                        if api_response:
                            st.success("✅ FDNC Record Found")
                            st.subheader("Raw Response:")
                            st.code(api_response, language="text")
                        else:
                            st.error("❌ No Record Found")
                    else:
                        st.error("❌ Failed to get response from FDNC API")
            else:
                st.warning("⚠️ Please enter a phone number to search.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray; font-size: small;'>"
        "Name & FDNC Search Application • Built with Streamlit"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
