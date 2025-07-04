from datetime import datetime


def get_today_date():
    # Получаем сегодняшнюю дату
    today = datetime.today()

    # Форматируем дату в виде: день.месяц.год
    formatted_date = today.strftime("%d.%m.%Y")

    return formatted_date


if __name__ == '__main__':
    print("Сегодняшняя дата:", get_today_date())
