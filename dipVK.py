import requests
import json
from pprint import pprint
from datetime import datetime
import time
from tqdm import tqdm
import os
import os.path






class VKUser:
    url = 'https://api.vk.com/method/'
    def __init__(self, token, version):
        self.version = version
        self.token = token
        self.params = {
            'access_token': self.token,
            'v': self.version
        }
        self.owner_id = requests.get(self.url+'users.get', self.params).json()['response'][0]['id']

    def get_photo(self, count, user_id=None):
        if user_id is None:
            user_id = self.owner_id
        url = 'https://api.vk.com/method/'
        self.params = {
            'access_token': self.token,
            'v': self.version,
            'user_ids': user_id,
        }
        user_id_new = requests.get(self.url + 'users.get', self.params).json()['response'][0]['id']
        #print(user_id_new)
        photo_url = url + 'photos.get'
        photo_params = {
            'album_id': 'profile',
            'rev': 0,
            'extended': 1,
            'photo_sizes': 1,
            'count': count,
            'owner_id': user_id_new,
            'access_token': self.token,
            'v': self.version
        }
        #res = requests.get(photo_url, params={**self.params, **photo_params})
        res = requests.get(photo_url, params=photo_params)
        vk_dict = res.json()
        #print(res.json())
        data_json_list = []

        for x in tqdm(vk_dict['response']['items']):
            file_url = x['sizes'][-1]['url']
            #print(file_url)
            data_json = x['sizes'][-1]['type']
            file_name = str(x['likes']['count'])
            date = x['date']
            ts = int(date)
            ts_new = str(datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d'))
            api = requests.get(file_url)
            #file_name_new = file_name+"-likes-"+ts_new+".jpg"
            file_name_new = file_name+"-likes-"+".jpg"
            #chek_file = os.path.isfile("/images/"+file_name_new)
            chek_file = os.path.exists("./images/"+file_name_new)
            #print(chek_file)
            if chek_file == True:
                file_name_new_2 = file_name+"-likes-"+ts_new +".jpg"
                data_json_w = {}
                data_json_w["file_name"] = file_name_new_2
                data_json_w["size"] = data_json
                data_json_list.append(data_json_w)
                with open("images/%s" % file_name_new_2, "wb") as f:
                    f.write(api.content)
            else:
                data_json_w = {}
                data_json_w["file_name"] = file_name_new
                data_json_w["size"] = data_json
                data_json_list.append(data_json_w)
                with open("images/%s" % file_name_new, "wb") as f:
                    f.write(api.content)

            with open('data.json', 'w', encoding='utf-8') as file:          #Запись в JSON файл
                json.dump(data_json_list, file)

        return print("Скачивание фото выполнено!")

class VKYandex:
    def __init__(self, token_yandex):
        self.token_yandex = token_yandex

    def upload(self):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources"
        headers = {'Content-Type': 'application/json', 'Authorization': self.token_yandex}
        path = 'images/'
        params = {"path": path, "overwrite": "false"}
        files_list = os.listdir(path)
        data = os.path.join(path)
        #print(files_list)
        #print(data)
        requests.put(upload_url, headers=headers, params=params)


        for z in tqdm(files_list):
            headers = {'Content-Type': 'application/json', 'Authorization': self.token_yandex}
            upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
            headers_2 = headers
            params = {"path": data+z, "overwrite": "true"}
            response_2 = requests.get(upload_url, headers=headers_2, params=params)
            x = response_2.json()
            #print(x)
            href = x.get("href")
            #print(href)
            response_3 = requests.put(href, data=open(path+z, 'rb'))
            #print(response_3)
            response_3.raise_for_status()

        return print("Фотографии загружены на диск!")




if __name__ == '__main__':
    token_vk = '' #Токен ВК
    token_yandex = '' #Токен яндекс диска
    vk_client = VKUser(token_vk, '5.130')
    vk_yandex = VKYandex(token_yandex)
    vk_client.get_photo("10") #Передаём количество фото, user_id или screen_name. Если указываем только кол-во фото, скачиваются фотографии пользователя токина.
    vk_yandex.upload()




