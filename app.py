import json

# исходные данные
busy = [
    {"start": "10:30", "stop": "10:50"},
    {"start": "18:40", "stop": "18:50"},
    {"start": "14:40", "stop": "15:50"},
    {"start": "16:40", "stop": "17:20"},
    {"start": "20:05", "stop": "20:20"},
]

free_interval_duration: int = 30

start_time: str = "09:00"
stop_time: str = "21:00"


## алгоритм
# - оставляем те занятые интервалы, которые пересекаются с рабочими часами
# - свободные интервалы - все промежутки между занятыми интервалами
# - оставляем только те свободные интервалы, которые в рабочих часах
# - делим оставшиеся свободные интервалы на интервалы нужной длины


# функции для конвертации времени в минуты
def time2mins(time: str) -> int:
    """
    Конвертация строки со временем в число минут с 00:00
    """
    h, m = map(int, time.split(":"))
    minutes = h * 60 + m
    return minutes


# функция дл конвертации из минут во время
def mins2time(minutes: int) -> str:
    """
    Преобразование числа минут в строку со временем формата 00:00 - 23:59.
    Число минут должно быть в диапазоне от 0 до 1439 (24 часа),
    иначе число часов будет больше 23
    """
    h = minutes // 60
    m = minutes % 60
    timeformat = f"{h:02}:{m:02}"
    return timeformat


# преобразую список словарей в список минутных интервалов
# т.к. последняя минута не входит в интервал, то отнимаю 1 минуту из интервала,
# чтобы граница интервала была не строгой

busy_intervals = [
    (
        time2mins(interval.get("start")),
        time2mins(interval.get("stop")) - 1,
    )
    for interval in busy
]

# сортирую интервалы по начальному времени
# предполагается что занятые интервалы не пересекаются
busy_intervals = sorted(busy_intervals, key=lambda i: i[0])

# расчёт рабочих минут
start_minute = time2mins(start_time)
# вычитаем минуту, чтобы граница интервала была нестрогой [9:00 - 20:59]
stop_minute = time2mins(stop_time) - 1


# Занятые интервалы должны 
# полностью или частично пересекаться с рабочими часами.
# Свободные интервалы выбираются как промежутки между занятыми интервалами.
# Крайний случай - занятых интервалов нет.
# Общий случай - 1 или более занятых интервалов 
# пересекающихся со свободным временем.

# Удаляем все занятые интервалы за пределами рабочего времени
# или оставляем только те, которые пересекаются с рабочим временем
busy_intervals = [
    interval
    for interval in busy_intervals
    if (interval[1] >= start_minute and interval[0] <= stop_minute)
]

# определяем свободные интервалы (начальное значение)
free_intervals = []

# крайний случай 1 - когда занятых интервалов нет
if not busy_intervals:
    free_interval = (start_minute, stop_minute)
    free_intervals.append(free_interval)
# общий случай - осталось 1 и более занятых интервала
else:
    # считаем первый свободный интервал (до всех занятых)
    # если первый занятой интервал не накрывает начало рабочего времени
    if start_minute < busy_intervals[0][0]:
        free_interval_first = (start_minute, busy_intervals[0][0] - 1)
        free_intervals.append(free_interval_first)

    for i in range(len(busy_intervals) - 1):
        free_interval = (
            busy_intervals[i][1] + 1,
            busy_intervals[i + 1][0] - 1,
        )
        free_intervals.append(free_interval)

    # считаем последний свободный интервал после всех занятых
    # если последний занятой интервал не накрывает конец рабочего времени
    if stop_minute > busy_intervals[-1][1]:
        free_interval_last = (busy_intervals[-1][1] + 1, stop_minute)
        free_intervals.append(free_interval_last)


# делим свободные интервалы на куски нужной длины
def divide_interval(
    interval: tuple[int, int], size: int
) -> list[tuple[int, int]]:
    """
    Деление интервала на набор подинтервалов заданной длины.
    Для всех интервалов границы нестрогие [x1, x2].
    params: interval: tuple[int, int] - интервал для деления в формате [x1, x2]
            size: int - длина подинтервалов
    return: list[tuple[int, int] - список интервалов после делений
    """
    start = interval[0]
    finish = interval[1]
    steps = (finish - start + 1) // size
    subintervals = [
        (start + step * size, start + (step + 1) * size - 1)
        for step in range(steps)
    ]
    return subintervals


free_intervals_sized = []
[
    free_intervals_sized.extend(
        divide_interval(interval, size=free_interval_duration)
    )
    for interval in free_intervals
]

# преобразуем результат из минут в словарь со строчным временем
free = [
    {
        "start": mins2time(interval[0]),
        "stop": mins2time(interval[1] + 1),
    }
    for interval in free_intervals_sized
]

print(json.dumps(free, indent=2))
