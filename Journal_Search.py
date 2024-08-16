import streamlit as st
from scholarly import scholarly
import re

def format_citation_apa(citation):
    authors = citation.get('author', [])
    year = citation.get('pub_year', 'n.d.')
    title = citation.get('title', '')
    journal = citation.get('journal', '')
    volume = citation.get('volume', '')
    issue = citation.get('number', '')
    pages = citation.get('pages', '')

    # Format authors
    formatted_authors = []
    for author in authors:
        names = author.split()
        formatted_author = f"{names[-1]}, {' '.join(names[:-1])}."
        formatted_authors.append(formatted_author)
    
    if len(formatted_authors) > 1:
        if len(formatted_authors) == 2:
            author_str = " & ".join(formatted_authors)
        else:
            author_str = ", ".join(formatted_authors[:-1]) + ", & " + formatted_authors[-1]
    else:
        author_str = formatted_authors[0]
    
    # Format citation
    citation_str = f"{author_str} ({year}). {title}. {journal}."
    return citation_str



def search_scholar(query, limit, year_start, year_end):
    search_query = scholarly.search_pubs(query)
    results = []
    for i in range(limit * 3):  # Meningkatkan jumlah hasil yang diperiksa
        try:
            article = next(search_query)
            pub_year = article['bib'].get('pub_year', 'NA')
            
            # Handle cases where year is not a valid integer
            try:
                year = int(pub_year)
            except ValueError:
                year = 0  # Use 0 or any value that will not fit the filter
            
            title = article['bib'].get('title', '').lower()
            abstract = article.get('bib', {}).get('abstract', '').lower()
            
            # Check if query is in title or abstract
            query_words = query.lower().split()
            if year_start <= year <= year_end and all(word in title + " " + abstract for word in query_words):
                results.append({
                    'title': article['bib']['title'],
                    'author': ", ".join(article['bib']['author']),
                    'abstract': article.get('bib', {}).get('abstract', 'No abstract available'),
                    'url': article.get('eprint_url', 'No URL available'),
                    'link': article.get('pub_url', 'No URL available'),
                    'citation': format_citation_apa(article['bib'])
                })
                if len(results) >= limit:
                    break
        except StopIteration:
            break
    return results


# Set the page configuration for the app
st.set_page_config(page_title="Scholar Search", page_icon="📚", layout="wide")

# Display the title of the app
st.title("🔍 Scholar Search: Your Gateway to Academic Knowledge")

# Display the author's name
st.markdown("*Author* : ***M Ulin Nuha Abduh***")

# Add custom CSS style to increase the font size
st.markdown("""
    <style>
    .big-font {
        font-size:20px !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Display a big-font message using HTML tags
st.markdown('<p class="big-font">Discover. Learn. Cite.</p>', unsafe_allow_html=True)

# Display a welcome message
st.write("Welcome to Scholar Search, your one-stop solution for academic research.")

# Create three columns for the layout
col1, col2, col3 = st.columns(3)

# Display content in the first column
with col1:
    st.subheader("🚀 Quick Search")
    st.write("Find relevant academic papers in seconds.")

# Display content in the second column
with col2:
    st.subheader("📊 Comprehensive Results")
    st.write("Get detailed information including abstracts and citations.")

# Display content in the third column
with col3:
    st.subheader("🗓️ Time-Saving")
    st.write("Filter by year to focus on recent or historical research.")

# Add a horizontal line
st.markdown("---")

# Display instructions on how to use the app
st.write("""
    ### How to use:
    1. Enter your search keywords in the sidebar
    2. Adjust the number of results and year range as needed
    3. Click the 'Search' button to find relevant academic papers
    4. Explore the results, read abstracts, and access full papers
""")

# Display an image in the sidebar
st.sidebar.image("https://img.icons8.com/?size=100&id=qtErPBbpMdwO&format=png&color=000000")

# Add a horizontal line
st.write("---")

# Sidebar input
st.sidebar.title("Search Parameters")

# Get the search query from the user
query = st.sidebar.text_input("Enter keywords to search in title and abstract:")

# Get the number of results to display from the user
limit = st.sidebar.number_input("Enter the number of results to display:", min_value=1, max_value=100, value=10)

# Display a message about the result limit
st.sidebar.write("Limit 100 results")

# Get the start year from the user
year_start = st.sidebar.number_input("Start Year", min_value=1900, max_value=2100, value=2000)

# Get the end year from the user
year_end = st.sidebar.number_input("End Year", min_value=1900, max_value=2100, value=2024)

# Add a search button
search_button = st.sidebar.button("Search")

# Initialize the session state to store search results
if 'search_results' not in st.session_state:
    st.session_state.search_results = None



# Check if the search button is clicked
if search_button:
    # Check if the query is not empty
    if query:
        # Show a spinner with the message "Searching..."
        with st.spinner('Searching...'):
            # Call the search_scholar function to search for scholarly articles
            # Pass the query, limit, year_start, and year_end as parameters
            # Store the search results in the session state variable "search_results"
            st.session_state.search_results = search_scholar(query, limit, year_start, year_end)
    else:
        # Show a warning message if the query is empty
        st.warning("Please enter search keywords.")

# Check if there are search results in the session state variable "search_results"
if st.session_state.search_results is not None:
    # Display the search query
    st.write(f"Search Results for: {query}")
    # Get the search results from the session state variable
    results = st.session_state.search_results
    # Check if there are results
    if results:
        # Iterate over the results
        for idx, result in enumerate(results):
            # Display the title of the result
            st.success(f"### {idx + 1}. {result['title']}")
            # Display the authors of the result
            st.write(f"**Authors:** {result['author']}")
            
            # Highlight keywords in the abstract
            abstract = result['abstract']
            # Split the query into individual words
            for word in query.split():
                # Use regular expressions to find and replace the words in the abstract with bolded versions
                abstract = re.sub(f'(?i){re.escape(word)}', lambda m: f"**{m.group()}**", abstract)
            
            # Display the abstract with highlighted keywords
            st.write(f"**Abstract:** ... {abstract} ...")
            
            # Create two columns for displaying the journal access and preview links
            cols = st.columns([1, 1])
            with cols[0]:
                # Check if the result has a journal access link
                if result['link'] != 'No URL available':
                    # Display a markdown link to access the journal
                    st.markdown(f"[Access Journal]({result['link']})")
            with cols[1]:
                # Check if the result has a journal preview link
                if result['url'] != 'No URL available':
                    # Display a markdown link to preview the journal
                    st.markdown(f"[Preview Journal]({result['url']})")
            
            # Display the citation of the result
            st.info(f'''**Citation :**\n
                    {result['citation']}
                    ''')
            
            # Add a horizontal line to separate the results
            st.write("---")
    else:
        # Display a message if no results are found
        st.write("No results found.")

