import streamlit as st
import requests
from typing import Optional, Set
import io
import os

def create_sample_names_file() -> str:
    """Create a sample names file on the backend."""
    sample_names = [
        "John Smith",
        "Jane Doe", 
        "Michael Johnson",
        "Emily Davis",
        "Robert Wilson",
        "Sarah Brown",
        "David Miller",
        "Lisa Anderson",
        "James Taylor",
        "Mary Thomas"
    ]
    
    file_path = "names.txt"
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            for name in sample_names:
                f.write(name + '\n')
        return file_path
    except Exception as e:
        st.error(f"Error creating sample file: {str(e)}")
        return None

def load_names_from_backend_file() -> Optional[Set[str]]:
    """Load names from backend text file into a set for efficient searching."""
    file_path = "names.txt"
    
    # Check if file exists
    if not os.path.exists(file_path):
        st.error(f"❌ File '{file_path}' not found!")
        return None
    
    try:
        names = set()
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                name = line.strip()
                if name:  # Only add non-empty lines
                    names.add(name.lower())  # Store in lowercase for case-insensitive search
                    
                # Show progress for large files
                if line_num % 1000 == 0:
                    print(f"Loaded {line_num} names...")
                    
        print(f"Total names loaded: {len(names)}")
        return names
    except Exception as e:
        st.error(f"Error loading names file: {str(e)}")
        return None

def search_name_with_details(names_set: Set[str], search_term: str) -> tuple:
    """Search names and return (found, matched_names, original_search)."""
    if not search_term.strip():
        return False, [], search_term.strip()
    
    search_term_lower = search_term.strip().lower()
    matched_names = []
    
    # Check for exact full name match first
    if search_term_lower in names_set:
        # Find the original case version from a temporary set
        for name in names_set:
            if name.lower() == search_term_lower:
                matched_names.append(name.title())  # Return in title case
                break
        return True, matched_names, search_term.strip()
    
    # Check for partial matches
    for name in names_set:
        if search_term_lower in name:
            matched_names.append(name.title())  # Return in title case
    
    return len(matched_names) > 0, matched_names, search_term.strip()

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
    if 'file_loaded' not in st.session_state:
        st.session_state.file_loaded = False
    
    # Load names from backend file automatically
    if not st.session_state.file_loaded:
        with st.spinner("Loading names from backend (this may take a moment for large files)..."):
            names = load_names_from_backend_file()
            if names:
                st.session_state.names_set = names
                st.session_state.file_loaded = True
                st.success(f"✅ Successfully loaded {len(names):,} names from backend file!")
                st.info(f"🔍 Search performance: O(1) for exact matches, very fast for partial matches")
            else:
                st.error("❌ Failed to load names from backend file.")
    
    # Sidebar for file information
    with st.sidebar:
        st.header("📁 File Information")
        
        # Display file status
        if st.session_state.file_loaded:
            total_names = len(st.session_state.names_set)
            st.info(f"📊 {total_names:,} names loaded from backend")
            st.info("📄 File: names.txt (backend)")
            st.success(f"⚡ Search optimized for {total_names:,}+ entries")
            
            if st.button("Reload Names"):
                st.session_state.file_loaded = False
                st.session_state.names_set = None
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
        
        # Check if names are loaded
        if not st.session_state.file_loaded:
            st.warning("⚠️ Names are not loaded from backend file.")
            return
        
        # Name search interface
        search_name_input = st.text_input(
            "Enter name to search:",
            placeholder="Type a name (first name, last name, or full name)...",
            help="Enter first name, last name, or full name. Search is case-insensitive and supports partial matches."
        )
        
        if st.button("Search Name", type="primary"):
            if search_name_input.strip():
                with st.spinner("Searching..."):
                    is_found, matched_names, original_search = search_name_with_details(st.session_state.names_set, search_name_input)
                    
                    if is_found:
                        st.success("✅ Match Found")
                        
                        # Display matched names with highlighting
                        st.markdown("### 📋 Matched Names:")
                        
                        for name in matched_names:
                            # Create highlighted version
                            name_lower = name.lower()
                            search_lower = original_search.lower()
                            
                            # Find and highlight matching parts
                            highlighted_name = name
                            start_idx = name_lower.find(search_lower)
                            
                            if start_idx != -1:
                                # Extract matching part and surrounding text
                                before = name[:start_idx]
                                match = name[start_idx:start_idx + len(original_search)]
                                after = name[start_idx + len(original_search):]
                                
                                # Create highlighted version
                                highlighted_name = f"{before}<mark style='background-color: yellow; color: black; font-weight: bold;'>{match}</mark>{after}"
                            
                            st.markdown(f"• {highlighted_name}", unsafe_allow_html=True)
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
                            st.markdown("---")
                            st.subheader("FDNC Status:")
                            
                            if api_response == "1":
                                st.markdown('<h3 style="color: red;">FDNC REGISTER</h3>', unsafe_allow_html=True)
                            elif api_response == "0":
                                st.markdown('<h3 style="color: green;">CLEAN</h3>', unsafe_allow_html=True)
                            else:
                                st.subheader("Raw Response:")
                                st.code(api_response, language="text")
                        else:
                            st.error("❌ No Record Found")
                    else:
                        st.error("❌ Failed to get response from FDNC API")
            else:
                st.warning("⚠️ Please enter a phone number to search.")
    
    # Google Search Section
    st.markdown("---")
    st.markdown("### 🔍 Google Search")
    
    # Add search input
    search_query = st.text_input("Enter your search query:", placeholder="Search anything on Google...")
    search_button = st.button("🔍 Search")
    
    if search_button and search_query:
        with st.spinner(f"Searching for '{search_query}'..."):
            try:
                # Use requests to get Google search results
                import requests
                from bs4 import BeautifulSoup
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                # Search Google
                google_url = f"https://www.google.com/search?q={search_query}"
                response = requests.get(google_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    st.markdown(f"### 🔍 Search Results for: '{search_query}'")
                    
                    # Find search results
                    search_results = []
                    
                    # Try different selectors for Google search results
                    selectors = [
                        'div.g',           # Standard Google results
                        'div.tF2Cxc',      # New Google results
                        'div.hlcw0c',      # Alternative selector
                        'div[data-ved]'    # Another alternative
                    ]
                    
                    for selector in selectors:
                        results = soup.select(selector)
                        if results:
                            search_results = results
                            break
                    
                    if search_results:
                        for i, result in enumerate(search_results[:10]):  # Show top 10 results
                            try:
                                # Extract title
                                title_elem = result.find('h3') or result.find('a')
                                title = title_elem.get_text().strip() if title_elem else "No Title"
                                
                                # Extract link
                                link_elem = result.find('a')
                                link = link_elem.get('href', '') if link_elem else ''
                                if link.startswith('/url?q='):
                                    link = link.split('/url?q=')[1].split('&')[0]
                                
                                # Extract description
                                desc_elem = result.find('span', {'data-ved': True}) or result.find('div', class_='VwiC3b')
                                description = desc_elem.get_text().strip() if desc_elem else "No Description"
                                
                                # Display result
                                st.markdown(f"### {i+1}. {title}")
                                if link:
                                    st.markdown(f"🔗 [Link]({link})")
                                st.markdown(f"📝 {description}")
                                st.markdown("---")
                                
                            except Exception as e:
                                continue
                    else:
                        # Fallback: Show raw search link
                        google_search_url = f"https://www.google.com/search?q={search_query}"
                        st.markdown(f"### 🔍 Search Results for: '{search_query}'")
                        st.markdown(f"🔗 [Click here to search on Google]({google_search_url})")
                        st.info("Google search results could not be loaded. Click the link above to search directly.")
                        
                        # Try to show iframe as alternative
                        st.markdown("### Alternative: Embedded Search")
                        st.markdown(
                            f"""
                            <iframe src="https://www.google.com/search?q={search_query}" 
                                    width="100%" 
                                    height="600" 
                                    frameborder="0">
                            </iframe>
                            """,
                            unsafe_allow_html=True
                        )
                else:
                    st.error("Failed to fetch search results")
                    
            except Exception as e:
                st.error(f"Search failed: {str(e)}")
                # Fallback to direct Google link
                google_search_url = f"https://www.google.com/search?q={search_query}"
                st.markdown(f"🔗 [Click here to search on Google]({google_search_url})")
    
    # Original Google CSE (as backup)
    st.markdown("### Or use Custom Search Engine:")
    st.markdown(
        """
        <script async src="https://cse.google.com/cse.js?cx=37c2351f685cd437d">
        </script>
        <div class="gcse-search"></div>
        """,
        unsafe_allow_html=True
    )
    
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
