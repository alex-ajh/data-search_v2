from django.http.request import QueryDict
from pymongo import MongoClient
from django.shortcuts import render
from ps_data.forms import SearchForm
from . import utils
from . import helper
from django.contrib.auth.decorators import login_required
from .decorators import group_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import timeit 

group_list = [
              'ATC', 
              'BDSG', 
              'GA', 
              'GCS', 
              'GM', 
              'GS', 
              'IBU',
              'MF', 
              'NRD',
              'OMD',
              'ORD', 
              'PM', 
              'RBU',
              'RND',
              'SRD'
            ]

def login(request): 
    return render(request, 'ps_data/login.html')

def index(request):
    search_list = ''
    search_status = ''
    search_count = 0
    group_name = ''
    page = request.GET.get('page', 1)
    search_time = 0
    paginated_results = None
    use_mock_data = False  # Flag to use mock data when MongoDB is unavailable

    # Set demo group if user is not authenticated or doesn't have groups
    if hasattr(request.user, 'groups') and request.user.groups.exists():
        group_name = request.user.groups.all()[0].name
        if not group_name in group_list:
            group_name = ''
    else:
        # Use demo group for UI testing
        group_name = 'DEMO'

    if request.method == 'POST' or 'keyword' in request.GET:
        if request.method == 'POST':
            search_form = SearchForm(request.POST)
        else:
            search_form = SearchForm(request.GET)

        if search_form.is_valid():
            keyword = str(search_form.cleaned_data['keyword'])
            print(f"group: {group_name}")
            print(f"keyword: {keyword}")

            # Try to log search (skip if file doesn't exist)
            try:
                helper.search_log(group_name)
            except:
                pass

            query_cmd = helper.generate_query_v2(keyword, group_name)

            if query_cmd == []:
                search_status = "invalid keyword"
            else:
                s_search = timeit.default_timer()

                try:
                    # Try MongoDB connection
                    client = MongoClient('localhost', 27017, serverSelectionTimeoutMS=1000)
                    client.server_info()  # Force connection check
                    search_db = client['index_park']
                    collection = search_db['file_park']
                    search_list = list(collection.find(query_cmd).limit(500))
                    search_count = len(search_list)
                    search_status = "search completed"
                except Exception as e:
                    # If MongoDB fails, use mock data for UI testing
                    print(f"MongoDB connection failed: {e}")
                    print("Using mock data for UI demonstration...")
                    use_mock_data = True

                    # Generate mock data based on keyword
                    search_list = []
                    mock_extensions = ['.pdf', '.docx', '.xlsx', '.pptx', '.txt', '.jpg', '.png']
                    mock_paths = ['C:/Documents/', 'C:/Projects/', 'C:/Data/', 'Z:/Shared/', 'Y:/Archive/']

                    # Generate sample files
                    for i in range(1, 51):  # Generate 50 mock results
                        if not keyword or keyword.lower() in f"file_{i}".lower() or keyword.lower() in f"document_{i}".lower():
                            search_list.append({
                                'file': f'{keyword}_document_{i}{mock_extensions[i % len(mock_extensions)]}' if keyword else f'sample_file_{i}{mock_extensions[i % len(mock_extensions)]}',
                                'path': f'{mock_paths[i % len(mock_paths)]}{group_name}/2024/{keyword if keyword else "files"}/',
                                'modified_date': 1627776000 + (i * 86400),  # Increment dates
                                'capacity': 1024 * 1024 * (i % 100 + 1),  # 1-100 MB
                                'dept': group_name
                            })

                    search_count = len(search_list)
                    search_status = "search completed (Mock Data - MongoDB 연결 없음)"

                e_search = timeit.default_timer()
                search_time = round(e_search - s_search, 2)
                print(f"search time : {search_time}")

                # Pagination
                paginator = Paginator(search_list, 20)  # Show 20 results per page
                try:
                    paginated_results = paginator.page(page)
                except PageNotAnInteger:
                    paginated_results = paginator.page(1)
                except EmptyPage:
                    paginated_results = paginator.page(paginator.num_pages)

        else:
            search_status = "invalid form"
    else:
        search_form = SearchForm(initial={'keyword': ''})
        search_status = "request method is Get"

    context = {
        'form': search_form,
        "search_list" : paginated_results if paginated_results else search_list,
        "search_count" : search_count,
        "search_status" : search_status,
        "search_time": search_time,
        "group_name" : group_name,
        "keyword": request.GET.get('keyword', '') or request.POST.get('keyword', ''),
        "use_mock_data": use_mock_data  # Pass flag to template
    }
    return render(request, 'ps_data/index.html', context)

def help(request):

    group_name = ''

    # Set demo group if user is not authenticated or doesn't have groups
    if hasattr(request.user, 'groups') and request.user.groups.exists():
        group_name = request.user.groups.all()[0].name
        if not group_name in group_list:
            group_name = ''
    else:
        # Use demo group for UI testing
        group_name = 'DEMO' 

    context = { 
            "group_name" : group_name 
        }

    return render(request, 'ps_data/help.html', context)