import direct_requester as req
import date_parser as par
import date_colors as col
import datetime
from datetime import date
import webbrowser

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

# OAuth-токен пользователя, от имени которого будут выполняться запросы
token = '*******************************************'

webbrowser.open_new_tab('https://oauth.yandex.ru/authorize?response_type=token&client_id=*********************')
print('Введите токен')
token = input()

days_amount = 14 # сколько дней отведено под красные/.../зеленые даты (2 недели)

today = datetime.datetime.today().date() # дата сегодня
start_date = today + datetime.timedelta(days=-1) # дата, с которой показываются просроченные акции (вчера)
end_date = today + datetime.timedelta(days=days_amount-1) # тут дата, до которой включительно показываются акции

# start_date ---> today ---> end_date
# от start до today (не включительно) - серые даты (просроченные)
# от today до end_date - красные\оранжевые\желтые\зеленые даты

# получаем id и тексты
id_texts = req.get_id_and_texts(token)

# тексты превращаем в даты
id_dates = dict()
for i in id_texts.keys():
    # парсим из текстов даты
    dates = par.parse_dates(id_texts[i])
    happy_new_year = start_date.year != end_date.year
    # Выбираем даты из промежутка    
    needed_dates = list()
    for d in dates:
        if d >= start_date and d <= end_date:
            needed_dates.append(d)
        elif happy_new_year: # если в промежутке оказался новый год
            d_true_year = 0
            if today.year < end_date.year:
                d_true_year = datetime.datetime(d.year+1, d.month, d.day).date()
            else:
                d_true_year = datetime.datetime(d.year-1, d.month, d.day).date()
            if d_true_year >= start_date and d_true_year <= end_date:
                needed_dates.append(d_true_year)
    if len(needed_dates) > 0:
        id_dates[i] = needed_dates

# раскрашиваем даты
id_date_color = list()
for i in id_dates.keys():
    for d in id_dates[i]:
        id_date_color.append((i, d, col.get_color(d, days_amount)))

# сортируем по дате
id_date_color = sorted(id_date_color, key=lambda x: x[1])

# результат:
for i in id_date_color:
    print('ID: '+str(i[0])+'\t Date: '+str(i[1])+'\t Color: '+i[2])
