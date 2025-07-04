from num2words import num2words


def number_to_words(amount):
    # Разделим на целую и дробную части
    rubles = int(amount)
    kopecks = round((amount - rubles) * 100)

    # Преобразуем рубли в пропись
    rubles_words = num2words(rubles, lang='ru', to='cardinal')

    # Определяем правильное склонение для рублей
    if rubles == 1:
        rubles_words = rubles_words + " рубль"
    elif 2 <= rubles <= 4:
        rubles_words = rubles_words + " рубля"
    else:
        rubles_words = rubles_words + " рублей"

    # Преобразуем копейки в пропись
    if kopecks == 0:
        return rubles_words  # Если копейки равны нулю, выводим только рубли
    else:
        kopecks_words = str(kopecks)
        # Формируем итоговую строку с копейками в нужном формате
        return f"{rubles_words}, {kopecks_words} коп."


# Пример
if __name__ == '__main__':
    amount = float(input("Введите сумму (например, 1001.23): "))
    print(number_to_words(amount))
