import matplotlib.pyplot as plt
import matplotlib
import os

matplotlib.use("Agg")


def create_pie_diagram(id: str, categories: list, values: list):
    """
    Создание круговой диаграммы
    :param id: id пользователя
    :param categories: Список категорий
    :param values: Список значений
    """
    if os.path.exists(f'userfiles/statistics/{id}pie.png'):
        os.remove(f'userfiles/statistics/{id}pie.png')
    filtered_categories = []
    filtered_values = []
    for i in range(len(categories)):
        if not values[i] == 0:
            filtered_categories.append(categories[i])
            filtered_values.append(values[i])

    plt.pie(filtered_values, labels=filtered_categories)
    plt.axis('equal')
    plt.title('Сумма по категориям')
    plt.savefig(f'userfiles/statistics/{id}pie.png')
    plt.close()
    return


def create_barh_diagram(id: str, categories: list, values: list):
    """
    Создание столбчатой диаграммы
    :param id: id пользователя
    :param categories: Список категорий
    :param values: Список значений
    :return:
    """
    if os.path.exists(f'userfiles/statistics/{id}barh.png'):
        os.remove(f'userfiles/statistics/{id}barh.png')
    filtered_categories = []
    filtered_values = []
    for i in range(len(values)):
        if not values[i] == 0:
            filtered_categories.append(categories[i])
            filtered_values.append(values[i])

    plt.barh(filtered_categories, filtered_values)
    plt.title('Колличество позиций по категориям')
    plt.subplots_adjust(left=0.3)
    plt.savefig(f'userfiles/statistics/{id}barh.png')
    plt.close()
    return
