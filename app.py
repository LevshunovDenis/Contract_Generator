from flask import Flask, render_template, request, send_file
from docxtpl import DocxTemplate
from datetime import datetime
import requests
import os
from num2words import num2words  # Импортируем библиотеку для преобразования в пропись
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Функция для получения информации по УНП из ЕГР
def get_company_info(unp):
    url = f'http://grp.nalog.gov.by/api/grp-public/data?unp={unp}&charset=UTF-8&type=json'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверим на успешный ответ от сервера
        data = response.json()
        row = data.get('row', {}) # Проверяем, если в ответе есть нужные данные
        if row:
            return {
                'vunp': row.get('vunp', 'Неизвестно'),
                'vnaimp': row.get('vnaimp', 'Неизвестно'),
                'vnaimk': row.get('vnaimk', 'Неизвестно'),
                'dreg': row.get('dreg', 'Неизвестно'),
                'nmns': row.get('nmns', 'Неизвестно'),
                'vmns': row.get('vmns', 'Неизвестно'),
                'ckodsost': row.get('ckodsost', 'Неизвестно'),
                'dlikv': row.get('dlikv', 'Неизвестно'),
                'vpadres': row.get('vpadres', 'Неизвестно')
            }
        else:
            return {'vnaimp': 'Неизвестно'}
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return {'vnaimp': 'Неизвестно'}

# Функция для преобразования числа в пропись
def number_to_words(amount):
    rubles = int(amount)
    kopecks = round((amount - rubles) * 100)
    rubles_words = num2words(rubles, lang='ru', to='cardinal') # Пропись рублей
    last_digit = rubles % 10
    last_two_digits = rubles % 100
    if 11 <= last_two_digits <= 14: # Склонение рублей
        ruble_word = "рублей" # Склонение рублей
    elif last_digit == 1: # Склонение рублей
        ruble_word = "рубль" # Склонение рублей
    elif 2 <= last_digit <= 4: # Склонение рублей
        ruble_word = "рубля" # Склонение рублей
    else: # Склонение рублей
        ruble_word = "рублей" # Склонение рублей
    last_digit_k = kopecks % 10 # Склонение копеек
    last_two_digits_k = kopecks % 100 # Склонение копеек
    if 11 <= last_two_digits_k <= 14: # Склонение копеек
        kopeck_word = "копеек" # Склонение копеек
    elif last_digit_k == 1: # Склонение копеек
        kopeck_word = "копейка" # Склонение копеек
    elif 2 <= last_digit_k <= 4: # Склонение копеек
        kopeck_word = "копейки" # Склонение копеек
    else: # Склонение копеек
        kopeck_word = "копеек" # Склонение копеек
    result_text = f"{rubles_words} {ruble_word}, {kopecks:02d} {kopeck_word}" # Строка прописью



    # Возвращаем строку с числом в формате 0.00 и прописью
    return f"{amount:.2f} ({result_text.capitalize()})"



    # ОКонвертируем даты поставки в более читаемый вид

# Функция для преобразования даты в нужный формат
def convert_date_format(date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    return date_obj.strftime('%d.%m.%Y')
   


    # Обработка отсутствия бюджет + внебюджет

# Обработка точек и запытях
def safe_float(val):
    try:
        return float(val.replace(',', '.'))  # поддержка запятых в числе
    except (ValueError, AttributeError):
        return 0.0

# Функция для получения сегодняшней даты
def get_today_date():
    today = datetime.today()
    formatted_date = today.strftime("%d.%m.%Y")
    return formatted_date

# Запуск файла index
@app.route('/')
def index():
    return render_template('index.html')

# Генерация и заполнение документа Word
@app.route('/generate_word', methods=['POST'])
def generate_word():
    finance_type = request.form.get('finance_type')  # Получаем данные из формы 
    nomer_dogovora = request.form.get('nomer_dogovora') # Получаем данные из формы 
    centr_podpis = request.form.get('centr_podpis') # Получаем данные из формы 
    postavchik_unp = request.form.get('postavchik') # Получаем данные из формы 
    v_interesah = request.form.get('v_interesah') # Получаем данные из формы 
    summа_dogovora = float(request.form.get('summa_dogovora'))  # Получаем данные из формы и преобразуем сумму в float
    summa_budget = safe_float(request.form.get('summa_budget', 0)) # Получаем данные из формы и преобразуем сумму в float
    summa_offbudget = safe_float(request.form.get('summa_offbudget', 0)) # Получаем данные из формы и преобразуем сумму в float
    summa_propis = number_to_words(summа_dogovora)  # Получаем данные из формы и получаем сумму прописью
    summa_budget = number_to_words(summa_budget) # Получаем данные из формы и получаем сумму прописью
    summa_offbudget = number_to_words(summa_offbudget) # Получаем данные из формы и получаем сумму прописью
    metod_oplata = request.form.get('metod_oplata') # Получаем данные из формы 
    first_date = convert_date_format(request.form.get('first_date')) # Конвертация даты в нужный формат
    last_date = convert_date_format(request.form.get('last_date')) # Конвертация даты в нужный формат
    metod_post = request.form.get('metod_post') # Получаем данные из формы 
    adress_post = request.form.get('adress_post') # Получаем данные из формы 
    rekviz_post = request.form.get('rekviz_post') # Получаем данные из формы 
    UNP = request.form.get('UNP') # Получаем данные из формы 
    email_post = request.form.get('email_post') # Получаем данные из формы 
    phone = request.form.get('phone') # Получаем данные из формы 
    bank = request.form.get('bank') # Получаем данные из формы 
    podpis = request.form.get('podpis') # Получаем данные из формы 
    


    # на основании переменной centr_podpis определяем данные для автозаполнения
    centr_podpisant = ''
    centr_podpisant_fio = ''
    if centr_podpis == "sindeev":
        centr_podpisant = "управляющего Синдеева Евгения Дмитриевича, действующего на основании Устава "
        centr_podpisant_fio = "Е.Д. Синдеев"
    elif centr_podpis == "lisimenko":
        centr_podpisant = "заместителя управляющего Лисименко Владислава Евгеньевича, действующего на основании доверенности № 28 от 03.01.2025 года "
        centr_podpisant_fio = "В.Е. Лисименко"
    else:
        centr_podpisant = "Тип финансирования не определён."
    


    # Словарь связи УНК и заказчика
    UNK_dict = {
        "Отдел образования Кормянского районного исполнительного комитета": "20100",
        "Отдел культуры Кормянского районного исполнительного комитета": "20060",
        "Барсуковский сельский исполнительный комитет": "20311",
        "Боровобудский сельский исполнительный комитет": "20391",
        "Ворновский сельский исполнительный комитет": "20321",
        "Коротьковский сельский исполнительный комитет": "20341",
        "Литвиновичский сельский исполнительный комитет": "20351",
        "Лужковский сельский исполнительный комитет": "20361",
        "Староградский сельский исполнительный комитет": "20381",
        "Государственное учреждение 'Кормянский районный архив'": "1008",
        "Учреждение 'Кормянский территориальный центр социального обслуживания населения'": "2018",
        "Сектор спорта и туризма Кормянского районного исполнительного комитета": "1020"
    }
    UNK = UNK_dict.get(v_interesah, "Неизвестно") # Получаем УНК в зависимости от выбранного заказчика



    # Словарь связи договора обслуживания и заказчика
    dog_obs_dict = {
        "Отдел образования Кормянского районного исполнительного комитета": "29 от 23.04.2020г",
        "Отдел культуры Кормянского районного исполнительного комитета": "30 от 23.04.2020г",
        "Барсуковский сельский исполнительный комитет": "35 от 23.04.2020г.",
        "Боровобудский сельский исполнительный комитет": "36 от 23.04.2020г",
        "Ворновский сельский исполнительный комитет": "37 от 23.04.2020г",
        "Коротьковский сельский исполнительный комитет": "39 от 23.04.2020г",
        "Литвиновичский сельский исполнительный комитет": "40 от 23.04.2020г",
        "Лужковский сельский исполнительный комитет": "41 от 23.04.2020г",
        "Староградский сельский исполнительный комитет": "42 от 23.04.2020г",
        "Государственное учреждение 'Кормянский районный архив'": "44 от 15.07.2024г",
        "Учреждение 'Кормянский территориальный центр социального обслуживания населения'": "45 от 03.01.2025г",
        "Сектор спорта и туризма Кормянского районного исполнительного комитета": "43 от 16.10.2023г"
    }
    dog_obs = dog_obs_dict.get(v_interesah, "Неизвестно") # Получаем номер договора обслуживания организации в зависимости от выбранного заказчика 



    # Словарь связи подписанта и его основания и заказчика
    podpis_dict = {
        "Отдел образования Кормянского районного исполнительного комитета": "начальника отдела Игнатенко Ивана Владимировича, действующего на основании Положения об отделе, ",
        "Отдел культуры Кормянского районного исполнительного комитета": "начальника отдела Борисенко Светланы Аркадьевны, действующего на основании Положения об отделе, ",
        "Барсуковский сельский исполнительный комитет": "председателя Старовойтовой Натальи Александровны, действующего на основании Закона Республики Беларусь от 04.01.2010г №108-3 'О местном управлении и самоуправлении в Республике Беларусь, '",
        "Боровобудский сельский исполнительный комитет": "председателя Бондаренко Людмилы Михайловны, действующего на основании Закона Республики Беларусь от 04.01.2010г №108-3 'О местном управлении и самоуправлении в Республике Беларусь, '",
        "Ворновский сельский исполнительный комитет": "председателя Ядренцевой Татьяны Михайловны, действующего на основании Закона Республики Беларусь от 04.01.2010г №108-3 'О местном управлении и самоуправлении в Республике Беларусь, '",
        "Коротьковский сельский исполнительный комитет": "председателя Шотик Александра Чеславовича, действующего на основании Закона Республики Беларусь от 04.01.2010г №108-3 'О местном управлении и самоуправлении в Республике Беларусь, '",
        "Литвиновичский сельский исполнительный комитет": "председателя Попасемовой Светланы Викторовны, действующего на основании Закона Республики Беларусь от 04.01.2010г №108-3 'О местном управлении и самоуправлении в Республике Беларусь, '",
        "Лужковский сельский исполнительный комитет": "председателя Копачевой Ирины Александровны, действующего на основании Закона Республики Беларусь от 04.01.2010г №108-3 'О местном управлении и самоуправлении в Республике Беларусь, '",
        "Староградский сельский исполнительный комитет": "председателя Сергеенко Ольги Александровны, действующего на основании Закона Республики Беларусь от 04.01.2010г №108-3 'О местном управлении и самоуправлении в Республике Беларусь, '",
        "Государственное учреждение 'Кормянский районный архив'": "директора Агеенко Жанны Викторовны, действующей на основании Устава, ",
        "Учреждение 'Кормянский территориальный центр социального обслуживания населения'": "директора Воргановой Натальи Ивановны, действующей на основании Устава, ",
        "Сектор спорта и туризма Кормянского районного исполнительного комитета": "заведующего сетором Гериловича Евгения Витальевича, действующего на основании Положения о секторе, "
    }
    podpis = podpis_dict.get(v_interesah, "Неизвестно")  # Получаем подписанта и его основания от выбранного заказчика



    # Словарь связи подписанта в конце документа (ФИО) и его основания от выбранного заказчика
    podpis_fio_dict = {
        "Отдел образования Кормянского районного исполнительного комитета": "И. В. Игнатенко",
        "Отдел культуры Кормянского районного исполнительного комитета": "С. А. Борисенко",
        "Барсуковский сельский исполнительный комитет": "Н. А. Старовойтова",
        "Боровобудский сельский исполнительный комитет": "Л. М. Бондаренко",
        "Ворновский сельский исполнительный комитет": "Т. М. Ядренцева",
        "Коротьковский сельский исполнительный комитет": "А. Ч. Шотик",
        "Литвиновичский сельский исполнительный комитет": "С. В. Попасемова",
        "Лужковский сельский исполнительный комитет": "И. А. Копачева",
        "Староградский сельский исполнительный комитет": "О. А. Сергеенко",
        "Государственное учреждение 'Кормянский районный архив'": "Ж.В. Агеенко",
        "Учреждение 'Кормянский территориальный центр социального обслуживания населения'": "Н.И. Ворганова",
        "Сектор спорта и туризма Кормянского районного исполнительного комитета": "Е. В. Герилович"
    }
    podpis_fio = podpis_fio_dict.get(v_interesah, "Неизвестно") # Получаем ФИО подписанта в конце документа от выбранного заказчика
    


    # Словарь связи реквизитов от выбранного заказчика
    rekviz_dict = {
        "Отдел образования Кормянского районного исполнительного комитета": "Отдел образования Кормянского районного исполнительного комитета, 247173, Гомельская область, Кормянский район, г.п. Корма, ул. Ильющенко, 34, р/с, BY83AKBB36044200072823200000, БИК  AKBBBY2Х, ЦБУ № 314 ОАО «АСБ Беларусбанк», ОКПО: 02150502,   УНП: 400050827.",
        "Отдел культуры Кормянского районного исполнительного комитета": "Отдел культуры Кормянского районного исполнительного комитета, 247173, Гомельская область, г.п. Корма, ул. Ильющенко 36, УНП 400051318, р/с, BY82AKBB36044200072953200000, Код банка AKBBBY2Х, ЦБУ №314 ОАО «АСБ Беларусбанк», Тел. 21280",
        "Барсуковский сельский исполнительный комитет": "Барсуковский сельский исполнительный комитет, адрес: 247180, а.г. Барсуки, ул. Володарского, 3. Р/с BY42AKBB 3600 4200 1158 3000 0000 ЦБУ № 314 ОАО «АСБ Беларусбанк». БИК: AKBBBY2Х, УНК: 20311, УНП: 401150049, Тел. (02337) 9 48 26",
        "Боровобудский сельский исполнительный комитет": "Боровобудский сельский исполнительный комитет, адрес: 247183, а.г. Боровая Буда, пер. Мира, 1Б. Р/с BY53AKBB 3604 4007 1650 6320 0000 ЦБУ № 314 ОАО «АСБ Беларусбанк». БИК: AKBBBY2Х, УНК: 20391, УНП: 401150077, Тел. (02337) 9 57 20",
        "Ворновский сельский исполнительный комитет": "Ворновский сельский исполнительный комитет, адрес: 247187, д. Ворновка, ул. Школьная, 11. Р/с BY55AKBB 3600 4200 2159 9000 0000 ЦБУ № 314 ОАО «АСБ Беларусбанк». БИК: AKBBBY2Х, УНК: 20321, УНП: 401150036. Тел. (02337) 9 41 37",
        "Коротьковский сельский исполнительный комитет": "Коротьковский сельский исполнительный комитет, 247173, Гомельская область, Кормянский район, г.п. Корма, ул. Школьная, 15, р/с BY02AKBB36044007161023200000, БИК  AKBBBY2Х, ЦБУ № 314 ОАО «АСБ Беларусбанк», УНК 20341 УНП 401150092  Тел. (02337) 42527",
        "Литвиновичский сельский исполнительный комитет": "247172, Гомельская область, Кормянский район, аг. Литвиновичи, ул. Крестьянская, 3, р/с BY39AKBB36044007162033200000, БИК  AKBBBY2X, ЦБУ № 314  ОАО «АСБ Беларусбанк» УНК 20351    УНП 401150064  Тел. (02337) 94331 ",
        "Лужковский сельский исполнительный комитет": "247186, Гомельская область, Кормянский район, а.г. Лужок, ул. Школьная, 3, р/с BY76 AKBB 3604 4007 1630 4320 0000, БИК  AKBBBY2X, ЦБУ № 314 ОАО «АСБ Беларусбанк», УНК 20361    УНП 401150023, Тел. (02337) 45380",
        "Староградский сельский исполнительный комитет": "247181, д. Староград, ул. Советская, 13. Р/с BY90AKBB 3604 4007 1660 7320 0000 ЦБУ № 314 ОАО «АСБ Беларусбанк». БИК: AKBBBY2Х, УНК: 20381, УНП: 401150010. Тел. (02337) 9 31 17",
        "Государственное учреждение 'Кормянский районный архив'": "Государственное учреждение «Кормянский районный архив», 247173, Гомельская область, Кормянский район, г.п. Корма, пер. Ильющенко, 8-208, р/с, BY70AKBB36044200073543200000, БИК  AKBBBY2Х, ЦБУ № 314 ОАО «АСБ Беларусбанк», УНК 1008,  УНП 491496171 Тел. 41059",
        "Учреждение 'Кормянский территориальный центр социального обслуживания населения'": "Учреждение «Кормянский территориальный центр социального обслуживания населения» адрес: 247173, Гомельская область, Кормянский район, г.п. Корма, ул. Абатурова, 44.р/с BY70AKBB36044007123083200000, БИК  AKBBBY2Х, ЦБУ № 314 ОАО «АСБ Беларусбанк», УНК 20180,  УНП 490321424 Тел.: 8 02337 4 21 23,  4 21 57",
        "Сектор спорта и туризма Кормянского районного исполнительного комитета": "Сектор спорта и туризма Кормянского районного исполнительного комитета, 247173, Гомельская область, Кормянский район, г.п. Корма, ул. Ильющенко, 34, р/с, BY10AKBB36044200001260000000, БИК  AKBBBY2Х, ЦБУ № 314 ОАО «АСБ Беларусбанк», УНК 1020,  УНП 401170731 Тел. +375 25 920 70 59"
    }
    rekviz_value = rekviz_dict.get(v_interesah, "Неизвестно") # Получаем реквизиты от выбранного заказчика
    
    # В зависимости от типа финансирования правильно прописываем пункт 3.1
    if finance_type == 'budget':
        summa_propis = f"Общая сумма Договора составляет {summa_propis} белорусских рублей."
    elif finance_type == 'offbudget':
        summa_propis = f"Общая сумма Договора составляет {summa_propis} белорусских рублей."
    elif finance_type == 'both':
        summa_propis = f"Общая сумма Договора составляет {summa_propis}  белорусских рублей из них: {summa_budget} белорусских рублей- средства районного бюджета УНК {UNK}; {summa_offbudget} белорусских рублей- внебюджетные средства."
    else:
        summa_propis = "Тип финансирования не определён."

    # В зависимости от типа финансирования правильно прописываем пункт 3.2
    if finance_type == 'budget' and v_interesah == "Отдел образования Кормянского районного исполнительного комитета":
        istochnik = f"Источник финансирования - районный бюджет, УНК - 20100"
    elif finance_type == 'offbudget' and v_interesah == "Отдел образования Кормянского районного исполнительного комитета":
        istochnik = f"Источник финансирования - внебюджетные средства"
    elif finance_type == 'both' and v_interesah == "Отдел образования Кормянского районного исполнительного комитета":
        istochnik = f"Источник финансирования - внебюджетные средства, районный бюджет"
    elif finance_type == 'budget' and v_interesah == "Сектор спорта и туризма Кормянского районного исполнительного комитета":
        istochnik = f"Источник финансирования - районный бюджет, УНК - 1020"
    elif finance_type == 'offbudget' and v_interesah == "Сектор спорта и туризма Кормянского районного исполнительного комитета":
        istochnik = f"Источник финансирования - внебюджетные средства"
    elif finance_type == 'both' and v_interesah == "Сектор спорта и туризма Кормянского районного исполнительного комитета":
        istochnik = f"Источник финансирования - внебюджетные средства, районный бюджет"
    elif finance_type == 'budget' and v_interesah == "Отдел культуры Кормянского районного исполнительного комитета":
        istochnik = f"Источник финансирования - районный бюджет, УНК - 20060"
    elif finance_type == 'offbudget' and v_interesah == "Отдел культуры Кормянского районного исполнительного комитета":
        istochnik = f"Источник финансирования - внебюджетные средства"
    elif finance_type == 'both' and v_interesah == "Отдел культуры Кормянского районного исполнительного комитета":
        istochnik = f"Источник финансирования - внебюджетные средства, районный бюджет"
    elif finance_type == 'budget' and v_interesah == "Государственное учреждение 'Кормянский районный архив'":
        istochnik = f"Источник финансирования - районный бюджет, УНК - 1008"
    elif finance_type == 'offbudget' and v_interesah == "Государственное учреждение 'Кормянский районный архив'":
        istochnik = f"Источник финансирования - внебюджетные средства"
    elif finance_type == 'both' and v_interesah == "Государственное учреждение 'Кормянский районный архив'":
        istochnik = f"Источник финансирования - внебюджетные средства, районный бюджет"
    elif finance_type == 'budget' and v_interesah == "Учреждение 'Кормянский территориальный центр социального обслуживания населения'":
        istochnik = f"Источник финансирования - районный бюджет, УНК - 2018"
    elif finance_type == 'offbudget' and v_interesah == "Учреждение 'Кормянский территориальный центр социального обслуживания населения'":
        istochnik = f"Источник финансирования - внебюджетные средства"
    elif finance_type == 'both' and v_interesah == "Учреждение 'Кормянский территориальный центр социального обслуживания населения'":
        istochnik = f"Источник финансирования - внебюджетные средства, районный бюджет"
    elif finance_type == 'budget' and v_interesah == "Барсуковский сельский исполнительный комитет":
        istochnik = f"Источник финансирования - бюджет сельского совета, УНК - 20311"
    elif finance_type == 'offbudget' and v_interesah == "Барсуковский сельский исполнительный комитет":
        istochnik = f"Источник финансирования - внебюджетные средства"
    elif finance_type == 'both' and v_interesah == "Барсуковский сельский исполнительный комитет":
        istochnik = f"Источник финансирования - внебюджетные средства, бюджет сельского совета"
    elif finance_type == 'budget' and v_interesah == "Боровобудский сельский исполнительный комитет":
        istochnik = f"Источник финансирования - бюджет сельского совета, УНК - 20391"
    elif finance_type == 'offbudget' and v_interesah == "Боровобудский сельский исполнительный комитет":
        istochnik = f"Источник финансирования - внебюджетные средства"
    elif finance_type == 'both' and v_interesah == "Боровобудский сельский исполнительный комитет":
        istochnik = f"Источник финансирования - внебюджетные средства, бюджет сельского совета"
    elif finance_type == 'budget' and v_interesah == "Ворновский сельский исполнительный комитет":
        istochnik = f"Источник финансирования - бюджет сельского совета, УНК - 20321"
    elif finance_type == 'offbudget' and v_interesah == "Ворновский сельский исполнительный комитет":
        istochnik = f"Источник финансирования - внебюджетные средства"
    elif finance_type == 'both' and v_interesah == "Ворновский сельский исполнительный комитет":
        istochnik = f"Источник финансирования - внебюджетные средства, бюджет сельского совета"
    elif finance_type == 'budget' and v_interesah == "Коротьковский сельский исполнительный комитет":
        istochnik = f"Источник финансирования - бюджет сельского совета, УНК - 20341"
    elif finance_type == 'offbudget' and v_interesah == "Коротьковский сельский исполнительный комитет":
        istochnik = f"Источник финансирования - внебюджетные средства"
    elif finance_type == 'both' and v_interesah == "Коротьковский сельский исполнительный комитет":
        istochnik = f"Источник финансирования - внебюджетные средства, бюджет сельского совета"
    elif finance_type == 'budget' and v_interesah == "Литвиновичский сельский исполнительный комитет":
        istochnik = f"Источник финансирования - бюджет сельского совета, УНК - 20351"
    elif finance_type == 'offbudget' and v_interesah == "Литвиновичский сельский исполнительный комитет":
        istochnik = f"Источник финансирования - внебюджетные средства"
    elif finance_type == 'both' and v_interesah == "Литвиновичский сельский исполнительный комитет":
        istochnik = f"Источник финансирования - внебюджетные средства, бюджет сельского совета"
    elif finance_type == 'budget' and v_interesah == "Лужковский сельский исполнительный комитет":
        istochnik = f"Источник финансирования - бюджет сельского совета, УНК - 20361"
    elif finance_type == 'offbudget' and v_interesah == "Лужковский сельский исполнительный комитет":
        istochnik = f"Источник финансирования - внебюджетные средства"
    elif finance_type == 'both' and v_interesah == "Лужковский сельский исполнительный комитет":
        istochnik = f"Источник финансирования - внебюджетные средства, бюджет сельского совета"
    elif finance_type == 'budget' and v_interesah == "Староградский сельский исполнительный комитет":
        istochnik = f"Источник финансирования - бюджет сельского совета, УНК - 20381"
    elif finance_type == 'offbudget' and v_interesah == "Староградский сельский исполнительный комитет":
        istochnik = f"Источник финансирования - внебюджетные средства"
    elif finance_type == 'both' and v_interesah == "Староградский сельский исполнительный комитет":
        istochnik = f"Источник финансирования - внебюджетные средства, бюджет сельского совета"
    else:
        summa_propis = "Тип финансирования не определён."
    

    full_postavka = ''
    if metod_oplata == '100% предоплата':
        metod_oplata = f"Предоплата в размере 100% осуществляется Покупателем  со счетов органов Государственного казначейства на расчетный счет Поставщика. Обязательство по оплате считается исполненным с момента передачи платежного поручения в органы государственного казначейства"
        full_postavka = f'Поставка Товара производится в  течение 5 рабочих дней с момента поступления денежных средств на расчетный счет Поставщика. Поставщик письменно уведомляет Покупателя о готовности Товара к отгрузке.'
    elif metod_oplata == 'Оплата по факту':
        metod_oplata = f"Расчеты осуществляются в безналичной форме платежными поручениями. Оплата производится со счета органов государственного казначейства на расчетный счет Поставщика по факту поставки Товара на основании ТН (ТТН) в течение 10-ти банковских дней. Обязательство по оплате считается исполненным с момента передачи платежного поручения в органы государственного казначейства."   
        full_postavka = f'Поставка Товара производится с {first_date} по {last_date}.  Поставщик письменно уведомляет Покупателя о готовности Товара к отгрузке.'
    else:
        metod_oplata = "" 
        full_postavka = ""
  
    # Получаем полное наименование поставщика через УНП
    company_info = get_company_info(postavchik_unp)

    # Получаем сегодняшнюю дату
    today_date = get_today_date()

    # Путь к шаблону Word документа в зависимости от типа финансирования
    if finance_type == 'offbudget':
        template_path = os.path.join('templates', 'template_offbudget.docx')
    else:
        template_path = os.path.join('templates', 'template.docx')

    # Загружаем шаблон
    doc = DocxTemplate(template_path)

    # Место для замены меток на значения из формы
    context = {
        'nomer_dogovora': nomer_dogovora,
        'date': today_date,  # Заменяем дату на сегодняшнюю
        'postavchik': company_info['vnaimp'],  # Подставляем полное наименование из API
        'v_interesah': v_interesah,
        'centr_podpisant': centr_podpisant,
        'summа_dogovora': summа_dogovora,
        'summa_propis': summa_propis,
        'istochnik': istochnik,
        'metod_oplata': metod_oplata,
        'full_postavka': full_postavka,
        'first_date': first_date,
        'last_date': last_date,
        'metod_post': metod_post,
        'adress_post': adress_post,
        'rekviz_post': company_info['vpadres'],
        'UNP': company_info['vunp'],
        'bank': bank,
        'email_post': email_post,
        'phone': phone,
        'rekviz': rekviz_value,
        'podpis': podpis,
        'centr_podpisant_fio': centr_podpisant_fio,
        'UNK': UNK,
        'dog_obs': dog_obs,
        'podpis_fio': podpis_fio,
    }

    # Заполняем шаблон
    doc.render(context)

    # Сохраняем файл на сервере
    output_path = os.path.join('static', f'generated_{nomer_dogovora}.docx')
    doc.save(output_path)

    # Отправляем файл пользователю
    return send_file(output_path, as_attachment=True)
   
# Запускаем программу
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)