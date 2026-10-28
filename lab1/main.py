"""
Лабораторная работа №1. Порождающие паттерны: Одиночка, Строитель.
Вариант 12 - «Расчёт баллистической траектории».

Программа спрашивает параметры выстрела, считает дальность, высоту и время
полёта, рисует траекторию в консоли и сохраняет исходные данные в файл.
"""
import json
import math
import os


class Settings:
    """
    Паттерн «Одиночка»: настройки программы существуют в одном экземпляре.
    Объект получают только через Settings.get_instance().
    """
    _instance = None
    FILE = "settings.json"

    # пользовательские настройки по умолчанию
    DEFAULTS = {
        "gravity": 9.81,         # ускорение свободного падения, м/с^2
        "chart_width": 60,       # ширина графика, символов
        "chart_height": 15,      # высота графика, строк
        "point_symbol": "*",     # символ траектории
        "ground_symbol": "=",    # символ земли
        "gun_symbol": "A",       # символ пушки
        "decimals": 2,           # знаков после запятой
        "shots_file": "shots.txt",  # куда сохранять исходные данные
        "save_shots": True,      # сохранять ли исходные данные
        "show_chart": True,      # рисовать ли график
        "chart_points": 200,     # сколько точек траектории рисовать
    }

    @classmethod
    def get_instance(cls):
        # объект создаётся только при первом вызове, потом возвращается тот же
        if cls._instance is None:
            cls._instance = Settings()
        return cls._instance

    def __init__(self):
        self.values = dict(self.DEFAULTS)
        if os.path.exists(self.FILE):
            with open(self.FILE, encoding="utf-8") as f:
                self.values.update(json.load(f))
        else:
            self.save()

    def save(self):
        with open(self.FILE, "w", encoding="utf-8") as f:
            json.dump(self.values, f, ensure_ascii=False, indent=2)

    def get(self, key):
        return self.values[key]


class Shot:
    """Исходные данные выстрела. Создаётся через ShotBuilder."""

    def __init__(self, name, speed, angle, height):
        self.name = name
        self.speed = speed      # м/с
        self.angle = angle      # градусы
        self.height = height    # высота старта, м


class ShotBuilder:
    """
    Паттерн «Строитель»: выстрел собирается по шагам,
    а build() проверяет данные перед созданием объекта.
    """

    def __init__(self):
        self._name = "Ядро"   # необязательный параметр со значением по умолчанию
        self._speed = None
        self._angle = None
        self._height = 0.0

    # каждый метод возвращает self, поэтому вызовы можно писать цепочкой
    def name(self, value):
        self._name = value
        return self

    def speed(self, value):
        self._speed = value
        return self

    def angle(self, value):
        self._angle = value
        return self

    def height(self, value):
        self._height = value
        return self

    def build(self):
        if self._speed is None or self._speed <= 0:
            raise ValueError("скорость должна быть больше нуля")
        if self._angle is None or not 0 <= self._angle <= 90:
            raise ValueError("угол должен быть от 0 до 90 градусов")
        if self._height < 0:
            raise ValueError("высота старта не может быть отрицательной")
        return Shot(self._name, self._speed, self._angle, self._height)


def calculate(shot):
    """Формулы полёта без сопротивления воздуха. Возвращает (время, дальность, высота)."""
    g = Settings.get_instance().get("gravity")
    a = math.radians(shot.angle)
    vx = shot.speed * math.cos(a)
    vy = shot.speed * math.sin(a)
    time = (vy + math.sqrt(vy ** 2 + 2 * g * shot.height)) / g
    distance = vx * time
    max_height = shot.height + vy ** 2 / (2 * g)
    return time, distance, max_height


def draw(shot, time, distance, max_height):
    """Рисует траекторию символами: строки - высота, столбцы - расстояние."""
    s = Settings.get_instance()
    width, height = s.get("chart_width"), s.get("chart_height")
    g = s.get("gravity")
    a = math.radians(shot.angle)
    n = s.get("chart_points")
    if distance == 0 or max_height == 0:
        return                                 # рисовать нечего
    canvas = [[" "] * width for _ in range(height)]

    for i in range(n):                         # n точек по времени полёта
        t = time * i / (n - 1)
        x = shot.speed * math.cos(a) * t
        y = shot.height + shot.speed * math.sin(a) * t - g * t * t / 2
        col = round(x / distance * (width - 1))
        row = height - 1 - round(y / max_height * (height - 1))
        canvas[row][col] = s.get("point_symbol")

    for line in canvas:
        print("  |" + "".join(line))
    print("  |" + s.get("gun_symbol") + s.get("ground_symbol") * (width - 1))


def main():
    print("=== Расчёт баллистической траектории ===")
    try:
        shot = (ShotBuilder()
                .name(input("Название снаряда: "))
                .speed(float(input("Скорость, м/с: ")))
                .angle(float(input("Угол, град: ")))
                .height(float(input("Высота старта, м: ")))
                .build())
    except ValueError as e:
        print("Ошибка:", e)
        return

    settings = Settings.get_instance()
    time, distance, max_height = calculate(shot)
    if settings.get("show_chart"):
        draw(shot, time, distance, max_height)

    d = settings.get("decimals")
    print(f"Максимальная высота: {max_height:.{d}f} м")
    print(f"Дальность полёта:    {distance:.{d}f} м")
    print(f"Время полёта:        {time:.{d}f} с")

    if settings.get("save_shots"):
        with open(settings.get("shots_file"), "a", encoding="utf-8") as f:
            f.write(f"{shot.name};{shot.speed};{shot.angle};{shot.height}\n")
        print("Исходные данные сохранены в", settings.get("shots_file"))

    # проверка «Одиночки»: оба вызова вернули один и тот же объект
    print("Settings - один объект:", Settings.get_instance() is Settings.get_instance())


if __name__ == "__main__":
    main()
