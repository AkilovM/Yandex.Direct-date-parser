import re, datetime, calendar

# превращаем строки типа 'Акция до 28.01!' в дату (year, 1, 28)

months_dict = {
    'январ':1,
    'феврал':2,
    'март':3,
    'апрел':4,
    'май':5,
    'мая':5,
    'маю':5,
    'мае':5,
    'июн':6,
    'июл':7,
    'август':8,
    'сентябр':9,
    'октябр':10,
    'ноябр':11,
    'декабр':12
    }

# строим регулярные выражения
p1 = re.compile(r'\d{1,2}[ \.:-]\d{2}')# 3.02    27 04   2-03
p2 = re.compile(r'\d{1,2}(?: январ| феврал| март| апрел| май| мая| маю| мае| июн| июл| август| сентябр| октябр| ноябр| декабр)')#   20 апреля   1 января
p3 = re.compile(r'январ|феврал|март|апрел|май|мая|маю|мае|июн|июл|август|сентябр|октябр|ноябр|декабр') # по умолчанию выставляем конец месяца

def parse_dates(text_list):
    today = datetime.datetime.today().date()
    dates_list = list()
    
    # парсим даты
    for t in text_list:
        if t is not None:
            for match in re.findall(p1, t.lower()):
                day_month = re.split(r'[ \.:-]', match)
                month = int(day_month[1])
                max_day = calendar.monthrange(today.year, month)[1]
                day = int(day_month[0])
                if day > max_day:
                    day = max_day
                dates_list.append(datetime.datetime(today.year, month, day).date())

            month_memory = list() # Чтобы третий регвыр не добавлял повторно месяц, найденный вторым регвыром
            for match in re.findall(p2, t.lower()):
                day_month = re.split(r'[ ]', match)
                month = months_dict[day_month[1]]
                month_memory.append(day_month[1])
                max_day = calendar.monthrange(today.year, month)[1]
                day = int(day_month[0])
                if day > max_day:
                    day = max_day
                dates_list.append(datetime.datetime(today.year, month, day).date())

            for match in re.findall(p3, t.lower()):
                if match not in month_memory:
                    month = months_dict[match]
                    max_day = calendar.monthrange(today.year, month)[1]
                    dates_list.append(datetime.datetime(today.year, month, max_day).date())
    dates_list.sort()
    return dates_list

# примеры для проверки:
test = ['весь Март',
    'до конца Марта!',
    'до 31 Марта',
    'до 28.01',
    'до 2-03',
    'до 15 04',
    'до 05:05',
    'до 03 Декабря',
    'до 2 сентября']
