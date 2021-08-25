from pymongo import MongoClient

def get_db_handle(db_name='data_search', host='localhost', port='27017',
                  username='admin', password='1024', collection='file_info_gcs_20210823'):
    client = MongoClient(host=host,
                        port=int(port),
                        username=username,
                        password=password
                        )
    db_handle = client[db_name]
    collection_handle = db_handle[collection]

    return db_handle, collection_handle 