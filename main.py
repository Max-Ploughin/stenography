"""
Реализовать стеганографию. Закодировать в изображении сообщение младшими битами. Писать в младшие биты, чтобы не было
сильного искажения. Например через какой-то шаг. Взять картинку, не брать jpeg, т.к. он выполняет сжатие с потерями.
Png или bmp  , где нет сжатия с потерями. Картинку можно захардкодить. Каждый пиксель состоит из 3 (просто rgb) или
4 байт(rgb + альфа-канал). А байты состоят из 8 бит. Если в определенные биты исходной картинки записать определенные
биты текста. Если в бите уже стоит единица, ее можно оставлять, а если ноль – то менять. Лучше писать в младшие биты
байта с каким-то шагом, чтобы визуальное изменение картинки было меньше. В каждый n-ный байт в младший бит записать
очередной бит сообщения. Пользователь вводит текст, мы его конвертируем в последовательность битов. Затем из
зашифрованной картинки нужно восстановить исходное сообщение и вывести его на экран.

"""
import os
import sys


def start():
    while True:
        option = int(input("Выберите опцию: 1 - зашифровать, 2 - расшифровать, 3 - выйти\n"))

        if option == 1:
            code_text_to_img()
            print("Выполнено!")
        elif option == 2:
            decode()
            text_file = open('decodedtext.txt')
            result_print = text_file.read()
            print()
            print("Расшифрованный текст:", result_print)
        elif option == 3:
            break
        else:
            print("Неизвестная опция")


# функция создания масок
def create_mask(degree):
    # шаблоны
    mask_for_text = 0b11111111
    mask_for_img = 0b11111111

    mask_for_text <<= (8 - degree)
    mask_for_text %= 256

    mask_for_img >>= degree
    mask_for_img <<= degree

    return mask_for_text, mask_for_img


# шифруем текст в картинку формата BMP
def code_text_to_img():
    degree = 8
    # проверка на то, что текст поместится в картинку
    text_size = os.stat('text.txt').st_size
    img_size = os.stat('sample4.bmp').st_size

    if text_size >= (img_size * degree / 8) - 54:
        print("Текст слишком большой")
        return

    # открываем тектовый файл с сообщением
    text = open('text.txt', 'r')
    origin_img = open('sample4.bmp', 'rb')
    uncoded_img = open('picencode.bmp', "wb")

    # фиксируем системную информацию файла
    system_data = origin_img.read(54)
    uncoded_img.write(system_data)

    text_mask, img_mask = create_mask(degree)

    # цикл для кодировки
    while True:
        symbol = text.read(1)
        if not symbol:
            break

        symbol = ord(symbol)
        print_info_txt = symbol
        print("Символ -", symbol, "=", bin(print_info_txt))

        for byte in range(0, 8, degree):
            img_byte = int.from_bytes(origin_img.read(1), sys.byteorder) & img_mask

            bits = symbol & text_mask
            bits >>= (8 - degree)
            img_byte |= bits
            uncoded_img.write(img_byte.to_bytes(1, sys.byteorder))
            symbol <<= degree

    uncoded_img.write(origin_img.read())

    text.close()
    origin_img.close()
    uncoded_img.close()


def decode():
    degree = 8
    symbols_amount = int(input("Введите количество символов в слове: "))

    # проверка на размер символов
    img_size = os.stat('picencode.bmp').st_size
    if symbols_amount >= (img_size * degree / 8) - 54:
        print("Текст слишком большой")
        return

    text_file = open('decodedtext.txt', 'w')
    coded_img = open('picencode.bmp', 'rb')

    # пропускаем системные данные
    coded_img.seek(54)

    text_mask, img_mask = create_mask(degree)
    img_mask = ~img_mask

    read = 0  # счетчик для чтения
    while read < symbols_amount:
        symbol = 0

        for byte in range(0, 8, degree):
            img_byte = int.from_bytes(coded_img.read(1), sys.byteorder) & img_mask
            symbol <<= degree
            symbol |= img_byte

        print("Символ № {0} это {1:c}".format(read, symbol))
        read += 1
        text_file.write(chr(symbol))

    text_file.close()
    coded_img.close()


start()
