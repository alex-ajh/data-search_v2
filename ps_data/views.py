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

@login_required
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

            if query_cmd == [] or query_cmd == {}:
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

                # Record search event
                if request.user.is_authenticated and not use_mock_data:
                    from .models import SearchRecord
                    try:
                        SearchRecord.objects.create(
                            keyword=keyword,
                            user=request.user,
                            department=group_name,
                            result_count=search_count,
                            search_time=search_time
                        )
                    except Exception as e:
                        print(f"Failed to record search: {e}")

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


def download_folder_opener(request, filename):
    """View to download folder opener files"""
    import os
    from django.http import FileResponse, Http404
    from django.conf import settings

    # Define allowed files
    allowed_files = {
        'FolderOpener.ps1': 'FolderOpener.ps1',
        'install.reg': 'install.reg',
        'uninstall.reg': 'uninstall.reg'
    }

    # Check if filename is allowed
    if filename not in allowed_files:
        raise Http404("File not found")

    # Get the file path from project root
    file_path = os.path.join(settings.BASE_DIR.parent, allowed_files[filename])

    # Check if file exists
    if not os.path.exists(file_path):
        raise Http404("File not found")

    # Return file as download
    response = FileResponse(open(file_path, 'rb'))
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response


@login_required
def visit_stats(request):
    """View to display visit statistics"""
    from .models import VisitCount

    group_name = ''

    # Set demo group if user is not authenticated or doesn't have groups
    if hasattr(request.user, 'groups') and request.user.groups.exists():
        group_name = request.user.groups.all()[0].name
        if not group_name in group_list:
            group_name = ''
    else:
        # Use demo group for UI testing
        group_name = 'DEMO'

    # Get all visit counts ordered by count (descending)
    visit_counts = VisitCount.objects.all().order_by('-count')

    # Get total visits across all pages
    total_visits = VisitCount.get_total_visits()

    # Get page count
    page_count = visit_counts.count()

    context = {
        'visit_counts': visit_counts,
        'total_visits': total_visits,
        'page_count': page_count,
        'group_name': group_name
    }

    return render(request, 'ps_data/visit_stats.html', context)


@login_required
def visit_chart_data(request):
    """API endpoint to provide monthly visit data for charts"""
    from django.http import JsonResponse
    from .models import VisitRecord
    from datetime import datetime, timedelta
    from django.utils import timezone
    import calendar

    # Get monthly statistics for the last 12 months
    monthly_stats = VisitRecord.get_monthly_stats(months=12)

    # Prepare data for Chart.js
    labels = []
    data = []

    # Create a dict for easy lookup
    stats_dict = {stat['month'].strftime('%Y-%m'): stat['count'] for stat in monthly_stats}

    # Generate last 12 months
    end_date = timezone.now()
    for i in range(11, -1, -1):
        target_date = end_date - timedelta(days=i * 30)
        month_key = target_date.strftime('%Y-%m')
        month_label = target_date.strftime('%b %Y')  # e.g., "Jan 2024"

        labels.append(month_label)
        data.append(stats_dict.get(month_key, 0))

    return JsonResponse({
        'labels': labels,
        'data': data
    })


@login_required
def search_stats(request):
    """View to display search statistics"""
    from .models import SearchRecord
    from django.db.models import Count, Sum, Avg

    group_name = ''

    # Set demo group if user is not authenticated or doesn't have groups
    if hasattr(request.user, 'groups') and request.user.groups.exists():
        group_name = request.user.groups.all()[0].name
        if not group_name in group_list:
            group_name = ''
    else:
        # Use demo group for UI testing
        group_name = 'DEMO'

    # Get total search count
    total_searches = SearchRecord.get_total_searches()

    # Get user's search count
    user_searches = SearchRecord.get_user_search_count(request.user)

    # Get department search count
    department_searches = SearchRecord.get_department_search_count(group_name) if group_name else 0

    # Get top keywords (overall)
    top_keywords = SearchRecord.get_top_keywords(limit=10)

    # Get user's top keywords
    user_top_keywords = SearchRecord.get_top_keywords(limit=10, user=request.user)

    # Get recent searches
    recent_searches = SearchRecord.objects.filter(user=request.user).order_by('-searched_at')[:10]

    # Get aggregated statistics
    stats = SearchRecord.objects.aggregate(
        total_results=Sum('result_count'),
        avg_results=Avg('result_count'),
        avg_time=Avg('search_time')
    )

    # Get user statistics
    user_stats = SearchRecord.objects.filter(user=request.user).aggregate(
        total_results=Sum('result_count'),
        avg_results=Avg('result_count'),
        avg_time=Avg('search_time')
    )

    context = {
        'total_searches': total_searches,
        'user_searches': user_searches,
        'department_searches': department_searches,
        'top_keywords': top_keywords,
        'user_top_keywords': user_top_keywords,
        'recent_searches': recent_searches,
        'stats': stats,
        'user_stats': user_stats,
        'group_name': group_name
    }

    return render(request, 'ps_data/search_stats.html', context)


@login_required
def search_chart_data(request):
    """API endpoint to provide monthly search data for charts"""
    from django.http import JsonResponse
    from .models import SearchRecord
    from datetime import datetime, timedelta
    from django.utils import timezone

    # Get filter parameter (all, user, or department)
    filter_type = request.GET.get('filter', 'user')

    # Get monthly statistics based on filter
    if filter_type == 'all':
        monthly_stats = SearchRecord.get_monthly_stats(months=12)
    elif filter_type == 'user':
        monthly_stats = SearchRecord.get_monthly_stats(months=12, user=request.user)
    else:  # department
        group_name = ''
        if hasattr(request.user, 'groups') and request.user.groups.exists():
            group_name = request.user.groups.all()[0].name
        monthly_stats = SearchRecord.get_monthly_stats(months=12, department=group_name)

    # Prepare data for Chart.js
    labels = []
    data = []

    # Create a dict for easy lookup
    stats_dict = {stat['month'].strftime('%Y-%m'): stat['count'] for stat in monthly_stats}

    # Generate last 12 months
    end_date = timezone.now()
    for i in range(11, -1, -1):
        target_date = end_date - timedelta(days=i * 30)
        month_key = target_date.strftime('%Y-%m')
        month_label = target_date.strftime('%b %Y')  # e.g., "Jan 2024"

        labels.append(month_label)
        data.append(stats_dict.get(month_key, 0))

    return JsonResponse({
        'labels': labels,
        'data': data
    })