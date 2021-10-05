import re
import os
import time
import timeit 
import datetime
from datetime import timedelta
from pymongo import MongoClient

def parse_keyword(keyword): 
    """
    - AND 검색 : Space
    - OR 검색 : Skip
    - 확장명 검색 : comma (ex: .pptx)
    - Directory 검색 : slash (ex: c:/a/)
    - 날짜 검색 : 예약어 sd: ed:
    - 용량 검색 : 예약어 size (ex: :>3 size:≥2)
    - Regex 검색  : Skip
    """
    keyword_parsed = {
                        "file_name" : [],
                        "extension" : None, 
                        "s_date" : None, 
                        "e_date" : None, 
                        "size_min" : None, 
                        "size_max" : None, 
                        "dir" : None
                     } 
    
    keyword_str = str(keyword) 
    
    if 'dir:' in keyword_str: 
        regex = re.compile(r"dir:((.*?)[/\\])+")
        result = regex.search(keyword_str) 
        result_group = result.group()
        path = result_group[4:]
        keyword_str = keyword_str.replace(result_group, '') 
        keyword_parsed['dir'] = path 
        print(f"path : {path}")

    keyword_split = keyword_str.split(' ') 
    
    for token in keyword_split: 
        if token == '': 
            pass 
        elif token[0] == '.': 
            keyword_parsed['extension'] = token[1:]
        elif 's_date:' in token: 
            s_date_length = len('s_date') 
            keyword_parsed['s_date'] = token[s_date_length+1:]  
        elif 'e_date:' in token: 
            e_data_length = len('e_date') 
            keyword_parsed['e_date'] = token[e_data_length+1:]  
        elif 'size:>' in token: 
            token_split = token.split('>')
            keyword_parsed['size_min'] = float(token_split[-1])  
        elif 'size:<' in token: 
            token_split = token.split('<')
            keyword_parsed['size_max'] = float(token_split[-1])          
        else: 
            keyword_parsed['file_name'].append(token) 
        
    # print(f"keyword parsing : {keyword_parsed}")
    return keyword_parsed 

def parse_keyword_v2(keyword): 
    keyword_str = str(keyword) 
    keyword_split = keyword_str.split(' ') 
    keyword_list = [] 

    for token in keyword_split: 
        if token == '': 
            pass 
        else: 
            keyword_list.append(token) 
    
    return keyword_list
     
def generate_query(keyword): 
    keyword_parsed = parse_keyword(keyword) 
    
    # print(f"keyword parsing: {keyword_parsed}")
    # print(f"keyword keys : {keyword_parsed.keys()}")

    query_list = [] 
    year_len = 4 
    month_len = 2 
    day_len = 2 
    for key, value in keyword_parsed.items():        
        if key == 'file_name' and value != []: 
            for file_name in value: 
                query_list.append({'file' : {'$regex' : str(file_name), '$options':'i'}})
        elif key == 'extension' and value != None:             
            query_list.append({'file' : {'$regex' : f'.{value}$', '$options':'i'}})
        elif key == 's_date' and value != None: 
            year = value[:year_len] 
            month = value[year_len:year_len + month_len] 
            day = value[year_len + month_len : ]             
            dt = datetime.datetime(year=int(year), month=int(month), day=int(day))
            time_stamp = time.mktime(dt.timetuple())
            query_list.append({'modified_date' : {'$gte' : time_stamp}})
        elif key == 'e_date' and value != None: 
            year = value[:year_len] 
            month = value[year_len:year_len + month_len] 
            day = value[year_len + month_len : ] 
            dt = datetime.datetime(year=int(year), month=int(month), day=int(day))
            time_stamp = time.mktime(dt.timetuple())
            query_list.append({'modified_date' : {'$lte' : time_stamp}})
        elif key == 'size_min' and value != None: 
            scale_mb = 1024 * 1024 
            file_size = int(float(value) * scale_mb) # Byte 
            query_list.append({'capacity' : {'$gte' : file_size}})
        elif key == 'size_max' and value != None: 
            scale_mb = 1024 * 1024 
            file_size = int(float(value) * scale_mb) # Byte 
            query_list.append({'capacity' : {'$lte' : file_size}})
        elif key == 'dir' and value != None: 
            print(f"dir value : {value}")
            query_list.append({'path' : {'$regex' : value.replace('/','\\\\'), '$options':'i'} })

    return { '$and' : query_list}

def generate_query_v2(keywords): 
    keyword_list = parse_keyword_v2(keywords) 
    
    query_list = [] 

    if keyword_list == []: 
        return query_list 
    else: 
        for keyword in keyword_list:        
            query_list.append({'file' : {'$regex' : str(keyword), '$options':'i'}})
        return { '$and' : query_list}
    

if __name__ == "__main__":
    client = MongoClient('localhost', 27017)
    search_db = client['file_search']
    collection = search_db['file_info_gcs_20210823']

    # keyword = "probe scanner .exe s_date:20210212 e_date:20210312 size:>3"
    keyword = "dir:z:/"
    # keyword = "  scanner .pptx  "

    query_cmd = generate_query(keyword)

    print(f"query_cmd : {query_cmd}")

    results = collection.find(query_cmd) 

    

    # for result in results: 
    #     datetimeobj = datetime.datetime.fromtimestamp(result['modified_date'])

    #     print(f"file name: {result['file']},")
    #     print(f"capacity : {round(result['capacity']/1024/1024,4)} MB,")
    #     print(f"file_path: {result['path']}")
    #     print(f"modified_date: {datetimeobj}")

    print(f"result count: {results.count()}")




    
    



    # mongo_query =  generate_query(keyword_parsed)

    # collection.find()
    


    

    