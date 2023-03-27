# -*- coding: utf-8 -*-
import requests, json
from requests.exceptions import ConnectionError
from time import sleep
import re

# direct_requester
# Тут происходит взаимодействие с API Яндекс.Директ

#  Метод для корректной обработки строк в кодировке UTF-8 как в Python 3, так и в Python 2
import sys

if sys.version_info < (3,):
    def u(x):
        try:
            return x.encode("utf8")
        except UnicodeDecodeError:
            return x
else:
    def u(x):
        if type(x) == type(b''):
            return x.decode('utf8')
        else:
            return x

# --- Подготовка, выполнение и обработка запроса ---
def get_headers(token):
    #  Создание HTTP-заголовков запроса
    headers = {"Authorization": "Bearer " + token,  # OAuth-токен. Использование слова Bearer обязательно
                # "Client-Login": clientLogin,  # Логин клиента рекламного агентства
                "Accept-Language": "ru",  # Язык ответных сообщений
                }
    return headers

def get_campaigns(headers):
    # Создание тела запроса
    camp_body = {"method": "get",  # Используемый метод.
        "params": {
            "SelectionCriteria": { # Критерий отбора кампаний. Для получения всех кампаний должен быть пустым
                "Types": ["TEXT_CAMPAIGN", "DYNAMIC_TEXT_CAMPAIGN"]
            },  
            "FieldNames": ["Id", "Name", "Type"]  # Имена параметров, которые требуется получить.
        }}
    CampaignsURL = 'https://api.direct.yandex.com/json/v5/campaigns'
    return get_request(CampaignsURL, camp_body, 'Campaigns', headers)

def camp_ids(campaigns):
    ids = list()
    for camp in campaigns:
        ids.append(camp['Id'])
    return ids

def get_ads(headers, campaigns):
    # Создание тела запроса
    ads_body = {"method": "get",
                "params": {
                    "SelectionCriteria": {  # AdsSelectionCriteria
                        "CampaignIds": camp_ids(campaigns),
                        "Types": ["TEXT_AD", "DYNAMIC_TEXT_AD"] # Только текстовые объявления
                    }, # required
                    "FieldNames": ["Id", "Type"], # required
                    "TextAdFieldNames": ["SitelinkSetId", "Text", "Title", "Title2", "AdExtensions"],
                    "DynamicTextAdFieldNames": ["SitelinkSetId", "Text", "AdExtensions"]
                }}
    AdsURL = 'https://api.direct.yandex.com/json/v5/ads'
    return get_request(AdsURL, ads_body, 'Ads', headers)

# К объявлению можно привязать до 50 уточнений.
# Одно и то же уточнение можно привязать к нескольким объявлениям.

# Возвращает список id уточнений (callouts), а также записывает в словарь какие уточнения принадлежат объявлению
def call_ids(ads, adId_callIds_dict):
    ids = set()
    type_name_dict = {'TEXT_AD': 'TextAd', 'DYNAMIC_TEXT_AD': 'DynamicTextAd'}
    for a in ads:
        for ext in a[type_name_dict[a['Type']]]['AdExtensions']:
            if ext['Type'] == 'CALLOUT':
                ids.add(ext['AdExtensionId'])
                if a['Id'] not in adId_callIds_dict.keys():
                    adId_callIds_dict[a['Id']] = list()
                adId_callIds_dict[a['Id']].append(ext['AdExtensionId'])
    return list(ids)

def get_callouts(headers, ads, adId_callIds_dict):
    # Создание тела запроса
    ids = call_ids(ads, adId_callIds_dict)
    if len(ids) > 0:
        cal_body = {"method": "get",
                    "params": {
                        "SelectionCriteria": { # AdExtensionsSelectionCriteria
                            "Ids": ids,
                            "Types": ["CALLOUT"]
                        }, # required
                        "FieldNames": ["Id", "Type", "Associated"],
                        "CalloutFieldNames": ["CalloutText"]
                    }}
        AdExtURL = 'https://api.direct.yandex.com/json/v5/adextensions'
        return get_request(AdExtURL, cal_body, 'AdExtensions', headers)
    else:
        return list()

# У объявления может быть только один набор быстрых ссылок (либо ни одного).
# Один и тот же набор быстрых ссылок можно привязать к нескольким объявлениям.

def sitelinks_ids(ads, adId_linkId_dict):
    ids = set()
    type_name_dict = {'TEXT_AD': 'TextAd', 'DYNAMIC_TEXT_AD': 'DynamicTextAd'}
    for a in ads:
        link_id = a[type_name_dict[a['Type']]]['SitelinkSetId']
        if link_id != None:
            ids.add(link_id)
            adId_linkId_dict[a['Id']] = link_id
    return list(ids)

def get_sitelinks(headers, ads, adId_linkId_dict):
    ids = sitelinks_ids(ads, adId_linkId_dict)
    if len(ids) > 0:
        # Создание тела запроса
        links_body = {"method": "get",
                    "params": {
                        "SelectionCriteria": { # IdsCriteria
                            "Ids": ids
                        }, # required
                        "FieldNames": ["Id"],
                        "SitelinkFieldNames": ["Description"]
                    }}
        SitelinksURL = 'https://api.direct.yandex.com/json/v5/sitelinks'
        return get_request(SitelinksURL, links_body, 'SitelinksSets', headers)
    else:
        return list()

def get_request(URL, jsonBody, class_name, headers):
    # Кодирование тела запроса в JSON
    jsonBody = json.dumps(jsonBody, ensure_ascii=False).encode('utf8')
    
    result_list = list()
    
    # Выполнение запроса
    try:
        result = requests.post(URL, jsonBody, headers=headers)
        
        # Отладочная информация
        #print("Заголовки запроса: {}".format(result.request.headers))
        #print("Запрос: {}".format(u(result.request.body)))
        #print("Заголовки ответа: {}".format(result.headers))
        #print("Ответ: {}".format(u(result.text)))
        #print("\n")

        # Обработка запроса
        if result.status_code != 200 or result.json().get("error", False):
            print("Произошла ошибка при обращении к серверу API Директа.")
            print("Код ошибки: {}".format(result.json()["error"]["error_code"]))
            print("Описание ошибки: {}".format(u(result.json()["error"]["error_detail"])))
            print("RequestId: {}".format(result.headers.get("RequestId", False)))
            print("")
        else:
            print("RequestId: {}".format(result.headers.get("RequestId", False)))
            print("Информация о баллах: {}".format(result.headers.get("Units", False)))
            # Вывод списка кампаний
            for campaign in result.json()["result"][class_name]:
                result_list.append(campaign)

            if result.json()['result'].get('LimitedBy', False):
                # Если ответ содержит параметр LimitedBy, значит,  были получены не все доступные объекты.
                # В этом случае следует выполнить дополнительные запросы для получения всех объектов.
                # Подробное описание постраничной выборки - https://tech.yandex.ru/direct/doc/dg/best-practice/get-docpage/#page
                print("Получены не все доступные объекты.")
            print("")

    # Обработка ошибки, если не удалось соединиться с сервером API Директа
    except ConnectionError:
        # В данном случае мы рекомендуем повторить запрос позднее
        print("Произошла ошибка соединения с сервером API.")

    # Если возникла какая-либо другая ошибка
    except:
        # В данном случае мы рекомендуем проанализировать действия приложения
        print("Произошла непредвиденная ошибка.")
    
    return result_list

# формируем словарь callout_id : callout_text
def call_texts_dict(ext):
    callId_text_dict = dict()
    for e in ext:
        callId_text_dict[e['Id']] = e['Callout']['CalloutText']
    return callId_text_dict

# формируем словарь sitelinkset_id : texts
def links_texts_dict(links):
    linkId_texts_dict = dict()
    for link_set in links:
        texts = list()
        for link in link_set['Sitelinks']:
            texts.append(link['Description'])
        linkId_texts_dict[link_set['Id']] = texts
    return linkId_texts_dict

# cобираем все строки объявления в один список
def collect_ads_texts(ads, ext, links, adId_callIds_dict, adId_linkId_dict):
    type_name_dict = {'TEXT_AD': 'TextAd', 'DYNAMIC_TEXT_AD': 'DynamicTextAd'}
    # в ads собрать Text (если тип TEXT_AD, то ещё и Title, Title2)
    # в ext собрать CalloutText
    # в links собрать Description
    
    ad_texts_dict = dict()
    
    callId_text_dict = call_texts_dict(ext)
    linkId_texts_dict = links_texts_dict(links)
    
    for a in ads:
        # собираем строки из ads
        ad_texts = list()
        text = a[type_name_dict[a['Type']]]['Text']
        if text != None:
            ad_texts.append(text)
        if a['Type'] == 'TEXT_AD':
            title = a[type_name_dict[a['Type']]]['Title']
            if title != None:
                ad_texts.append(title)
            title2 = a[type_name_dict[a['Type']]]['Title2']
            if title2 != None:
                ad_texts.append(title2)
        
        # собираем строки из ext
        if a['Id'] in adId_callIds_dict.keys():
            for calId in adId_callIds_dict[a['Id']]:
                text = callId_text_dict[calId]
                if text != None:
                    ad_texts.append(text)

        # собираем строки из links
        if a['Id'] in adId_linkId_dict.keys():
            ad_texts = ad_texts + linkId_texts_dict[adId_linkId_dict[a['Id']]]
        
        ad_texts_dict[a['Id']] = ad_texts
    return ad_texts_dict

# функция для получения id и текстовых строк (её вызываем в main):
def get_id_and_texts(token):
    app_id = '**************************'
    headers = get_headers(token)
    campaigns = get_campaigns(headers) # кампании
    ads = get_ads(headers, campaigns) # рекламные объявления
    adId_callIds_dict = dict()
    ext = get_callouts(headers, ads, adId_callIds_dict) # уточнения
    adId_linkId_dict = dict()
    links = get_sitelinks(headers, ads, adId_linkId_dict) # быстрые ссылки
    return collect_ads_texts(ads, ext, links, adId_callIds_dict, adId_linkId_dict)
