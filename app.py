import streamlit as st
import requests
from typing import Optional, Set
import io
import os
from PIL import Image
from bs4 import BeautifulSoup
import re

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

def get_celebrity_info(name: str) -> Optional[dict]:
    """Search for celebrity/well-known personality information and image."""
    try:
        # Clean name for search
        clean_name = re.sub(r'[^\w\s]', '', name).strip().lower()
        
        # Celebrity database with placeholder images
        celebrity_db = {
            'jennifer aniston': {
                'real_name': 'Jennifer Aniston',
                'profession': 'Actress',
                'known_for': 'Friends, The Morning Show',
                'image_url': 'https://picsum.photos/seed/jennifer-aniston/200/200'
            },
            'brad pitt': {
                'real_name': 'Brad Pitt',
                'profession': 'Actor',
                'known_for': 'Fight Club, Once Upon a Time in Hollywood',
                'image_url': 'https://picsum.photos/seed/brad-pitt/200/200'
            },
            'tom cruise': {
                'real_name': 'Tom Cruise',
                'profession': 'Actor',
                'known_for': 'Mission Impossible, Top Gun',
                'image_url': 'https://picsum.photos/seed/tom-cruise/200/200'
            },
            'angelina jolie': {
                'real_name': 'Angelina Jolie',
                'profession': 'Actress',
                'known_for': 'Tomb Raider, Maleficent',
                'image_url': 'https://picsum.photos/seed/angelina-jolie/200/200'
            },
            'leonardo dicaprio': {
                'real_name': 'Leonardo DiCaprio',
                'profession': 'Actor',
                'known_for': 'Titanic, Inception, The Wolf of Wall Street',
                'image_url': 'https://picsum.photos/seed/leonardo-dicaprio/200/200'
            },
            'scarlett johansson': {
                'real_name': 'Scarlett Johansson',
                'profession': 'Actress',
                'known_for': 'Black Widow, Lost in Translation',
                'image_url': 'https://picsum.photos/seed/scarlett-johansson/200/200'
            },
            'robert downey jr': {
                'real_name': 'Robert Downey Jr.',
                'profession': 'Actor',
                'known_for': 'Iron Man, Sherlock Holmes',
                'image_url': 'https://picsum.photos/seed/robert-downey/200/200'
            },
            'chris evans': {
                'real_name': 'Chris Evans',
                'profession': 'Actor',
                'known_for': 'Captain America, Knives Out',
                'image_url': 'https://picsum.photos/seed/chris-evans/200/200'
            },
            'emma stone': {
                'real_name': 'Emma Stone',
                'profession': 'Actress',
                'known_for': 'La La Land, The Amazing Spider-Man',
                'image_url': 'https://picsum.photos/seed/emma-stone/200/200'
            },
            'ryan reynolds': {
                'real_name': 'Ryan Reynolds',
                'profession': 'Actor',
                'known_for': 'Deadpool, The Proposal',
                'image_url': 'https://picsum.photos/seed/ryan-reynolds/200/200'
            },
            'dwayne johnson': {
                'real_name': 'Dwayne Johnson',
                'profession': 'Actor, Former Wrestler',
                'known_for': 'Jumanji, Fast & Furious',
                'image_url': 'https://picsum.photos/seed/dwayne-johnson/200/200'
            },
            'will smith': {
                'real_name': 'Will Smith',
                'profession': 'Actor, Rapper',
                'known_for': 'Men in Black, The Pursuit of Happyness',
                'image_url': 'https://picsum.photos/seed/will-smith/200/200'
            },
            'julia roberts': {
                'real_name': 'Julia Roberts',
                'profession': 'Actress',
                'known_for': 'Pretty Woman, Erin Brockovich',
                'image_url': 'https://picsum.photos/seed/julia-roberts/200/200'
            },
            'george clooney': {
                'real_name': 'George Clooney',
                'profession': 'Actor, Director',
                'known_for': 'Ocean\'s Eleven, Gravity',
                'image_url': 'https://picsum.photos/seed/george-clooney/200/200'
            },
            'meryl streep': {
                'real_name': 'Meryl Streep',
                'profession': 'Actress',
                'known_for': 'The Devil Wears Prada, Sophie\'s Choice',
                'image_url': 'https://picsum.photos/seed/meryl-streep/200/200'
            },
            'tom hanks': {
                'real_name': 'Tom Hanks',
                'profession': 'Actor',
                'known_for': 'Forrest Gump, Cast Away',
                'image_url': 'https://picsum.photos/seed/tom-hanks/200/200'
            },
            'sandra bullock': {
                'real_name': 'Sandra Bullock',
                'profession': 'Actress',
                'known_for': 'The Blind Side, Gravity',
                'image_url': 'https://picsum.photos/seed/sandra-bullock/200/200'
            },
            'keanu reeves': {
                'real_name': 'Keanu Reeves',
                'profession': 'Actor',
                'known_for': 'The Matrix, John Wick',
                'image_url': 'https://picsum.photos/seed/keanu-reeves/200/200'
            },
            'natalie portman': {
                'real_name': 'Natalie Portman',
                'profession': 'Actress',
                'known_for': 'Black Swan, Star Wars',
                'image_url': 'https://picsum.photos/seed/natalie-portman/200/200'
            }
        }
        
        # Check if name matches any celebrity
        if clean_name in celebrity_db:
            celebrity = celebrity_db[clean_name]
            
            # Download image
            img_response = requests.get(celebrity['image_url'], timeout=5)
            if img_response.status_code == 200:
                img = Image.open(io.BytesIO(img_response.content))
                return {
                    'name': celebrity['real_name'],
                    'profession': celebrity['profession'],
                    'known_for': celebrity['known_for'],
                    'image': img,
                    'found': True
                }
        
        return None
        
    except Exception as e:
        return None

def call_fdnc_api(phone_number: str) -> Optional[str]:
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
                        
                        # Display matched names with highlighting and celebrity info
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
                            
                            # Display name with highlighting
                            st.markdown(f"• {highlighted_name}", unsafe_allow_html=True)
                            
                            # Search for celebrity information
                            with st.spinner(f"Searching for celebrity info for {name}..."):
                                celebrity_info = get_celebrity_info(name)
                                
                                if celebrity_info and celebrity_info['found']:
                                    st.markdown(f"### 🌟 Celebrity Match Found!")
                                    
                                    # Create two columns for image and info
                                    col1, col2 = st.columns([1, 2])
                                    
                                    with col1:
                                        # Display image
                                        st.image(celebrity_info['image'], caption=celebrity_info['name'], width=200)
                                    
                                    with col2:
                                        st.markdown(f"**🎭 Name:** {celebrity_info['name']}")
                                        st.markdown(f"**🎬 Profession:** {celebrity_info['profession']}")
                                        st.markdown(f"**⭐ Known For:** {celebrity_info['known_for']}")
                                        st.markdown("*Celebrity information from database*")
                                    
                                    st.markdown("---")
                                else:
                                    st.info(f"No celebrity information found for '{name}'")
                                    st.markdown("---")
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
