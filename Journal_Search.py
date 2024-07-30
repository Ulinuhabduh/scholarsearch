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
        formatted_author = f"{names[-1]}, {' '.join(names[:-1])}"
        formatted_authors.append(formatted_author)

    if len(formatted_authors) > 1:
        author_str = ", ".join(formatted_authors[:-1]) + ", & " + formatted_authors[-1]
    else:
        author_str = formatted_authors[0]

    citation_str = f"{author_str} ({year}). {title}. {journal}"
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

st.set_page_config(page_title="Scholar Search", page_icon="📚", layout="wide")

st.title("🔍 Scholar Search: Your Gateway to Academic Knowledge")

st.markdown("""
    <style>
    .big-font {
        font-size:20px !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="big-font">Discover. Learn. Cite.</p>', unsafe_allow_html=True)

st.write("Welcome to Scholar Search, your one-stop solution for academic research.")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🚀 Quick Search")
    st.write("Find relevant academic papers in seconds.")

with col2:
    st.subheader("📊 Comprehensive Results")
    st.write("Get detailed information including abstracts and citations.")

with col3:
    st.subheader("🗓️ Time-Saving")
    st.write("Filter by year to focus on recent or historical research.")

st.markdown("---")

st.write("""
    ### How to use:
    1. Enter your search keywords in the sidebar
    2. Adjust the number of results and year range as needed
    3. Click the 'Search' button to find relevant academic papers
    4. Explore the results, read abstracts, and access full papers
""")

st.sidebar.image("https://img.icons8.com/?size=100&id=qtErPBbpMdwO&format=png&color=000000")
st.write("---")

# Sidebar input
st.sidebar.title("Search Parameters")
query = st.sidebar.text_input("Enter keywords to search in title and abstract:")
limit = st.sidebar.number_input("Enter the number of results to display:", min_value=1, max_value=100, value=10)

st.sidebar.write("Limit 100 results")
year_start = st.sidebar.number_input("Start Year", min_value=1900, max_value=2100, value=2000)
year_end = st.sidebar.number_input("End Year", min_value=1900, max_value=2100, value=2024)

# Tambahkan tombol pencarian
search_button = st.sidebar.button("Search")

# Inisialisasi session state untuk menyimpan hasil pencarian
if 'search_results' not in st.session_state:
    st.session_state.search_results = None

# Lakukan pencarian ketika tombol ditekan
if search_button:
    if query:
        with st.spinner('Searching...'):
            st.session_state.search_results = search_scholar(query, limit, year_start, year_end)
    else:
        st.warning("Please enter search keywords.")

# Tampilkan hasil pencarian
if st.session_state.search_results is not None:
    st.write(f"Search Results for: {query}")
    results = st.session_state.search_results
    if results:
        for idx, result in enumerate(results):
            st.success(f"### {idx + 1}. {result['title']}")
            st.write(f"**Authors:** {result['author']}")
            
            # Highlight keywords in abstract
            abstract = result['abstract']
            for word in query.split():
                abstract = re.sub(f'(?i){re.escape(word)}', lambda m: f"**{m.group()}**", abstract)
            
            st.write(f"**Abstract:** ... {abstract} ...")
            
            cols = st.columns([1, 1])
            with cols[0]:
                if result['link'] != 'No URL available':
                    st.markdown(f"[Access Journal]({result['link']})")
            with cols[1]:
                if result['url'] != 'No URL available':
                    st.markdown(f"[Preview Journal]({result['url']})")
            st.text_area("Citation", value=result['citation'], height=100)
            st.write("---")
    else:
        st.write("No results found.")