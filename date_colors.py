import datetime

# Раскрашиваем даты

#Самые близкие вверху списка - красные.
#Далее оранжевым, желтым.
#Максимально отдаленные - зеленым.
#Просроченные - серым.

#Если кол-во чисел в диапазоне (от текущей до выбранной даты включительно) делится на 4, то все цвета поровну.
#Если нет, то при остатке от деления на 4 осталась 1 - +1 зеленая дата.
#%4 = 2 --- +1 зеленая, +1 желтая.
#%4 = 3 --- +1 зеленая, +1 желтая, +1 оранжевая.
def get_color(date, days_amount):
    if days_amount < 1:
        raise ValueError('days_amount должен быть натуральным числом')
    today = datetime.datetime.today().date()
    if date < today:
        return 'grey'
    elif date > today + datetime.timedelta(days=days_amount-1):
        return 'green'
    
    n = (date - today).days + 1 # акция сегодня = 1, акция завтра = 2 и т.д.
    colors = {1:'red', 2:'orange', 3:'yellow', 4:'green'}

    if days_amount < 5:
        return colors[n]
    elif days_amount % 4 == 1:
        if n == days_amount:
            return 'green' # 12  34  56  789
        else:
            return colors[((n - 1) // (days_amount // 4)) + 1] # 11 22 33 44
    elif days_amount % 4 == 2:
        if n <= (days_amount // 4) * 2:
            return colors[((n - 1) // (days_amount // 4)) + 1] # 12 34 567 8910
        else:
            return colors[((n + 1) // ((days_amount // 4) + 1)) + 1]# 333 444 678 91011
    elif days_amount % 4 == 3: # 12 345 678 91011    
        return colors[(n // ((days_amount // 4) + 1)) + 1] # 11 222 333 444
    else:
        return colors[((n - 1) // (days_amount // 4)) + 1]

# Пример:
# Сегодня 27 мая. Дата завершения акции 30 мая. Промежуток из красных/.../зеленых дат составляет 14 дней.
#
# date = datetime.date(2022, 5, 30)
# days_amount = 14
#
# результат должен быть оранжевый:'orange'
