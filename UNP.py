import requests

def get_company_info(unp):
    url = f'http://grp.nalog.gov.by/api/grp-public/data?unp={unp}&charset=UTF-8&type=json'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверим на успешный ответ от сервера
        data = response.json()

        # Проверяем, если в ответе есть нужные данные
        row = data.get('row', {})
        if row:
            print(f"ИНН/УНП: {row.get('vunp', 'Неизвестно')}")
            print(f"Полное наименование: {row.get('vnaimp', 'Неизвестно')}")
            print(f"Краткое наименование: {row.get('vnaimk', 'Неизвестно')}")
            print(f"Дата постановки на учет: {row.get('dreg', 'Неизвестно')}")
            print(f"Код инспекции МНС: {row.get('nmns', 'Неизвестно')}")
            print(f"Наименование инспекции МНС: {row.get('vmns', 'Неизвестно')}")
            print(f"Код состояния плательщика: {row.get('ckodsost', 'Неизвестно')}")
            print(f"Дата изменения состояния плательщика: {row.get('dlikv', 'Неизвестно')}")
            print(f"Адрес: {row.get('vpadres', 'Неизвестно')}")
        else:
            print("Данные не найдены.")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")

if __name__ == '__main__':
    unp = input("Введите УНП: ")
    get_company_info(unp)
