import pyzbar.pyzbar as pyzbar
import cv2


def read_qr(path: str) -> list:
    """
    Функция для распознания и чтения QR кода
    :param path: Путь к изображению с кодом
    :return: Список информации из кода с датой покупки и стоимостью
    """
    im = cv2.imread(path) #Чтение файла
    im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY) #Перевод цветов в оттенки серого
    im = cv2.bilateralFilter(im, 11, 17, 17) #Фильтрация изображения
    im = cv2.GaussianBlur(im, (3, 3), 0) #Повыщение чёткости
    info = pyzbar.decode(im, symbols=[pyzbar.ZBarSymbol.QRCODE]) #Распознание QR кода

    if not list(info):
        return None
    else:
        try:
            data = str(info[0][0]).split('&') #Разделение информации из кода
            day = int(data[0][10:12])
            month = int(data[0][8:10])
            year = int(data[0][4:8])
            price = float(data[1][2:])
        except ValueError:
            return None
        return [day, month, year, price]
