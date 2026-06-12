import requests
from bs4 import BeautifulSoup
import json

url = 'https://www.goodreads.com/book/show/215361843-just-our-luck'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
           'Accept-Language': 'en-US,en;q=0.9'}
r = requests.get(url, headers=headers)
print('Status Code:', r.status_code)
soup = BeautifulSoup(r.text, 'html.parser')

next_data = soup.find('script', id='__NEXT_DATA__')
if next_data:
    data = json.loads(next_data.string)
    apollo_state = data.get('props', {}).get('pageProps', {}).get('apolloState', {})
    
    # Get the book URI from ROOT_QUERY
    root_query = apollo_state.get('ROOT_QUERY', {})
    book_ref = None
    for key, val in root_query.items():
        if key.startswith('getBookByLegacyId('):
            book_ref = val.get('__ref')
            break
            
    if not book_ref:
        print("Could not find getBookByLegacyId in ROOT_QUERY")
        # dump keys to see
        print(list(root_query.keys()))
    else:
        val = apollo_state.get(book_ref, {})
        title = val.get('title', 'N/A')
        rating = val.get('stats', {}).get('averageRating', 'N/A') if isinstance(val.get('stats'), dict) else 'N/A'
        ratings_count = val.get('stats', {}).get('ratingsCount', 'N/A') if isinstance(val.get('stats'), dict) else 'N/A'
        
        synopsis = 'N/A'
        desc = val.get('description')
        if isinstance(desc, dict) and 'html' in desc:
            synopsis = BeautifulSoup(desc['html'], 'html.parser').text
            
        publisher = 'N/A'
        details = val.get('details')
        if isinstance(details, dict):
            pub_ref = details.get('publisher', {})
            if isinstance(pub_ref, dict) and '__ref' in pub_ref:
                pub_obj = apollo_state.get(pub_ref['__ref'], {})
                publisher = pub_obj.get('name', 'N/A')
                
        author = 'N/A'
        primary_contributor_edge = val.get('primaryContributorEdge')
        if isinstance(primary_contributor_edge, dict):
            node_ref = primary_contributor_edge.get('node', {})
            if isinstance(node_ref, dict) and '__ref' in node_ref:
                author_obj = apollo_state.get(node_ref['__ref'], {})
                author = author_obj.get('name', 'N/A')
                
        series_name = 'N/A'
        series_link = 'N/A'
        series_connection = val.get('bookSeriesConnection')
        if isinstance(series_connection, dict):
            edges = series_connection.get('edges', [])
            if edges:
                first_edge = edges[0]
                series_ref = first_edge.get('node', {}).get('series', {})
                if isinstance(series_ref, dict) and '__ref' in series_ref:
                    series_obj = apollo_state.get(series_ref['__ref'], {})
                    series_name = series_obj.get('title', 'N/A')
                    s_url = series_obj.get('webUrl', 'N/A')
                    series_link = s_url

        print('Title:', title)
        print('Author:', author)
        print('Rating:', rating)
        print('Ratings Count:', ratings_count)
        print('Synopsis:', synopsis[:100] + '...' if synopsis != 'N/A' else 'N/A')
        print('Series Name:', series_name)
        print('Series Link:', series_link)
        print('Publisher:', publisher)
