import os
import time
import json
import requests


accessid  = ""
accesskey = ""
sumo_users = []

'''requests decorator'''
def request(func):
  def wrapper(*args):
    print('Calling %s...' % func.__name__)
    print(args)
    headers = {'Content-type':'application/json','isAdminMode': 'true'}
    try:
        if "post" in args:
            url,content,method= func(*args)
            resp = requests.post(url, headers=headers, auth=(accessid,accesskey))
        else:
            url  = func(*args)
            resp = requests.get(url,auth=(accessid,accesskey), headers=headers)
        return resp.json()
    except(ValueError, requests.exceptions.HTTPError) as e:
        return "Error: " + str(e)      
  return wrapper 
        
'''Build API object to take requests'''

class SumoAPI():
    
    def __init__(self):
        self.base_url    = 'https://api.us2.sumologic.com/api/'
        self.method      = "post"
        self.content     = ""

    @request
    def get_users(self):
        path = 'v1/users'
        url  = self.base_url + path
        return (url)
  
    @request
    def get_personal_folders(self):
        url  = self.base_url+'v2/content/folders/personal'
        return (url)

    @request
    def get_global_folders(self,*args):
        if not args:
            url = self.base_url+'v2/content/folders/global'
        else:
            '''get global folder result by passing in id as arg'''
            url = self.base_url+'v2/content/folders/global/%s/result' %args
        return (url)

    @request
    def get_single_folder(self,folder_id):
        url = self.base_url+'v2/content/folders/%s' %folder_id
        return (url)

    @request
    def get_single_user(self,user_id):
        url = self.base_url+'v1/users/%s' %(user_id)
        return (url)

    @request
    def get_content(self,content_path):
        url = self.base_url+'v2/content/%s' %(content_path)
        return (url) 

    @request
    def get_content_path(self,content_id):
        url = self.base_url+'v2/content/%s/path' %(content_id)
        return (url)

    @request
    def start_export(self,id,method):
        url = self.base_url+'v2/content/%s/export' % id
        method = self.method
        content = self.content
        return (url,self.method,self.content)

    @request
    def export_status(self,content_id,job_id):
        url = self.base_url+'v2/content/%s/export/%s/status' %(content_id,job_id)
        return (url)

    @request
    def get_export_result(self,content_id,job_id):
        url = self.base_url+'v2/content/%s/export/%s/result' %(content_id,job_id)
        return (url)
 
    @request
    def start_import(self,folder_id,content,method):
        url     = self.base_url+'v2/content/folders/%s/import' % folder_id
        content = self.content
        method  = self.method
        return (url,self.method,self.content)
 
    @request
    def import_status(self,folder_id,job_id):
        url  = self.base_url+'v2/content/%s/import/%s/status' %(folder_id,job_id)
        return (url)


'''get  Sumologic user ids'''

def get_user_ids(users):
    
    user_ids = dict.fromkeys([user for user in sumo_users
])
    for i in range(0,len(users['data'])):
        if users['data'][i]['email'] in sumo_users
    :
            user_ids.update({users['data'][i]['email']:users['data'][i]['id']})
    return user_ids 

'''get all of the content id for users by getting all user content and filtering by 
   createdby: userid '''

def get_user_content(): 
    '''Retrive content ID's for users from a Sumo Org'''
    all_users         = sumo.get_users()
    user_map          = get_user_ids(all_users)
    global_id         = sumo.get_global_folders() 
    global_content    = sumo.get_global_folders(global_id['id'])
    user_content      = [item for item in global_content['data'] if item['createdBy'] in user_map.values()]
    content_ids       = [i['id'] for i in user_content if 'id' in i ]
    content_map       = dict.fromkeys([k for k,v in user_map.items()]) 
    for key, value in content_map.items():
        for i in range(0,len(content_ids)):
            if user_content[i]['createdBy'] in user_map[key]:
                content_map[key] = content_ids[i]
    return content_map
   
'''Export user content '''

def run_export(content_map):
    
    result  = dict.fromkeys([user for user in sumo_users
])
    for user in sumo_users
:
        response = sumo.start_export(content_map[user],"post") 
        export_status = sumo.export_status(content_map[user],response['id'])
        while export_status['status'] == 'InProgress':
            print('Waiting for export to finish...')
            time.sleep(2)
            break
        content = sumo.get_export_result(content_map[user],response['id'])
        result[user] = content
    return result 

'''Import user content'''

def run_import(payload):
    
    print('Calling run_import')
    accessid  =  ""
    accesskey =  ""
    new_content_map = get_user_content() 
    for user in sumo_users
:
        payload = payload[user]
        try:
            resp = requests.post(sumo.base_url+\
            'v2/content/folders/%s/import' % (new_content_map[user]) \
            , headers={'Content-type':'application/json','isAdminMode':'true'}\
            , auth=(accessid,accesskey), data=json.dumps(payload)) 
        except(ValueError, requests.exceptions.HTTPError) as e:
            return "Error: " + str(e)
    return resp.json()

def main():
    
    sumo              = SumoAPI()
    user_content      = get_user_content()
    exported_content  = run_export(user_content)
    run_import(exported_content)

if __name__ == "__main__":
    main()
