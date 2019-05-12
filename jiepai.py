import requests
from urllib.parse import urlencode
import os
from hashlib import md5
from multiprocessing.pool import Pool

base_url = "https://www.toutiao.com/api/search/content/?keyword=%E8%A1%97%E6%8B%8Daid=24&app_name=web_search&"

headers = {
    'cookie': '__guid=32687416.1194945246485899000.1557528654558.5679; __tasessionId=axwkoui641557528655106; csrftoken=65b2803ae5809cf3caaf8186223d2a28; tt_webid=6689535944012580366; UM_distinctid=16aa3f13a02696-095ca24304678d-3c604504-1fa400-16aa3f13a0360d; CNZZDATA1259612802=1385119398-1557528803-%7C1557528803; s_v_web_id=c42e1e231fd132e0e56a4b5d306c5367; monitor_count=2',
    'Referer': 'https://www.toutiao.com/search/?keyword=%E8%A1%97%E6%8B%8D',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}


def get_page(offset):
    params = {
        'offset': offset,
        'format': 'json',
        'keyword': '街拍',
        'autoload': 'true',
        'count': '20',
        'cur_tab': '1',
        'from': 'search_tab',
        'pd': 'synthesis',
    }
    url = base_url + urlencode(params)
    # print(url)
    try:
        response = requests.get(url, headers)
        # print(response)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError:
        return None


def get_images(json):
    if json:
        # print(json)
        items = json.get('data')
        # print(items)
        for item in items:
            if item.get('cell_type') is not None:
                continue
            title = item.get('title')
            images = item.get('image_list')
            # print(images)
            for image in images:
                jiepai = {}
                jiepai['title'] = title
                jiepai['image'] = image.get('url')
                yield jiepai


print('Get image successfully')


def save_image(item):
    img_path = 'img' + os.path.sep + item.get('title')
    print('Created path of document successfully')
    if not os.path.exists(img_path):
        os.makedirs(img_path)
    try:
        response = requests.get(item.get('image'))
        if requests.codes.ok == response.status_code:
            file_path = img_path + os.path.sep + '{}.{}'.format(md5(response.content).hexdigest(), 'jpg')
            if not os.path.exists(file_path):
                print('Created path of image successfully')
                with open(file_path, 'wb')as f:
                    f.write(response.content)
                    print('Downloaded image path is %s' % file_path)
                    print('downloaded image successfully')
            else:
                print('Already downloaded', file_path)
    except requests.ConnectionError as e:
        print('Error', e.args)
        print('Failed to save image,item %s' % item)


def main(offset):
    json = get_page(offset)
    results = get_images(json)
    for result in results:
        print(result)
        save_image(result)


GROUP_START = 0
GROUP_END = 0

if __name__ == '__main__':
    pool = Pool()
    groups = ([x * 20 for x in range(GROUP_START, GROUP_END + 1)])
    pool.map(main, groups)
    pool.close()
    pool.join()
