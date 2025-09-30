from django.http.request import QueryDict
from pymongo import MongoClient
from django.shortcuts import render
from ps_data.forms import SearchForm
from . import utils 
from . import helper 
from django.contrib.auth.decorators import login_required
from .decorators import group_required
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

@login_required
def index(request):  
    search_list = '' 
    search_status = ''
    search_count = ''
    group_name = '' 

    if request.user.groups.exists(): 
        group_name = request.user.groups.all()[0].name 
        if not group_name in group_list: 
            group_name = '' 
    
    if request.method == 'POST':
        search_form = SearchForm(request.POST)
        
        if search_form.is_valid() and group_name != '':        
            keyword = str(search_form.cleaned_data['keyword'])  
            print(f"group: {group_name}")
            print(f"keyword: {keyword}") 
            helper.search_log(group_name) 
            # helper.validate_keyword(keyword)
            query_cmd = helper.generate_query_v2(keyword, group_name) 
            # print(f"query: {query_cmd}")
            # _ , collection = utils.get_db_handle()             
            if query_cmd == []: 
                search_status = "invalid keyword"
            else: 
                s_search = timeit.default_timer() 
                
                client = MongoClient('localhost', 27017)
                search_db = client['index_park']
                collection = search_db['file_park']                
                search_list = collection.find(query_cmd) 
                search_status = "search completed" 
                
                e_search = timeit.default_timer() 

                print(f"search time : {e_search - s_search }")

                
                
        else: 
            search_status = "invalid form"
    else:
        search_form = SearchForm(initial={'keyword': ''})
        search_status = "request method is Get"

    context = { 
        'form': search_form, 
        "search_list" : search_list, 
        "search_count" : search_count, 
        "search_status" : search_status, 
        "group_name" : group_name 
    }
    return render(request, 'ps_data/index.html', context)

@login_required
def help(request):  

    group_name = '' 

    if request.user.groups.exists(): 
        group_name = request.user.groups.all()[0].name 
        if not group_name in group_list: 
            group_name = '' 

    context = { 
            "group_name" : group_name 
        }

    return render(request, 'ps_data/help.html', context)