from django.http.request import QueryDict
from pymongo import MongoClient
from django.shortcuts import render
from ps_data.forms import SearchForm
from . import utils 
from . import helper 
from django.contrib.auth.decorators import login_required

def login(request): 
    return render(request, 'ps_data/login.html')

@login_required
def index(request):  
    search_list = '' 
    search_status = ''
    search_count = '' 
    if request.method == 'POST':
        search_form = SearchForm(request.POST)
        
        if search_form.is_valid():        
            keyword = str(search_form.cleaned_data['keyword'])  
            print(f"keyword: {keyword}") 
            # helper.validate_keyword(keyword)
            query_cmd = helper.generate_query_v2(keyword) 
            # print(f"query: {query_cmd}")
            # _ , collection = utils.get_db_handle()             
            if query_cmd == []: 
                search_status = "invalid keyword"
            else: 
                client = MongoClient('localhost', 27017)
                search_db = client['index_nrd']
                collection = search_db['file_nrd']
                search_list = collection.find(query_cmd) 
                search_count = search_list.count() 
                search_status = "search completed"
        else: 
            search_status = "invalid form"
    else:
        search_form = SearchForm(initial={'keyword': ''})
        search_status = "request method is Get"

    context = { 
        'form': search_form, 
        "search_list" : search_list, 
        "search_count" : search_count, 
        "search_status" : search_status 
    }
    return render(request, 'ps_data/index.html', context)

def help(request):  

    return render(request, 'ps_data/help.html')