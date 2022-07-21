class Car:
    """Взял у Владоса для первого пути """

    def __init__(self, ):
        """Конструктор.

        Args:
            length:
                Длина машины.
            width:
                Ширина машины (наибольшая).
            min_radius:
                Минимальный радиус поворота.
            wheelbase:
                Колёсная база.
            front_track:
                Передняя колея.
            back_track:
                Задняя колея.
            rear_view_mirror:
                Ширина зеркал заднего вида.
            pos_rear_view_mirror:
                Растояние от переда авто до середины зекала заднего вида.

        Notes:
            Важно соблюдать одну размерность во всём проекте!

        """
        self.length = 4384
        self.width = 1699
        self.min_radius = 5400
        self.wheelbase = 2552
        self.front_track = 1460
        self.back_track = 1498
    # self.rear_view_mirror = rear_view_mirror
    # self.pos_rear_view_mirror = pos_rear_view_mirror
