"""
Лабораторная работа №2. Порождающие паттерны: Абстрактная фабрика, Прототип.
Вариант 12 - «Расчёт баллистической траектории».

Один и тот же снаряд запускается на Земле, Луне и Марсе.
Программа ищет угол, при котором снаряд улетает дальше всего.
"""
import copy
import math


# ---------- Продукты абстрактной фабрики ----------

class Gravity:
    """Сила тяжести планеты."""

    def __init__(self, g):
        self.g = g  # м/с^2


class Atmosphere:
    """Атмосфера планеты: тормозит снаряд силой F = 0.5 * плотность * Cx * S * v^2."""

    def __init__(self, density):
        self.density = density  # кг/м^3

    def drag(self, vx, vy, shot):
        """Ускорение от сопротивления воздуха (ax, ay)."""
        v = math.hypot(vx, vy)
        area = math.pi * shot.diameter ** 2 / 4
        k = 0.5 * self.density * shot.cx * area / shot.mass
        return -k * v * vx, -k * v * vy


# ---------- Абстрактная фабрика ----------

class PlanetFactory:
    """
    Паттерн «Абстрактная фабрика»: каждая планета создаёт свою пару
    «тяжесть + атмосфера». Остальной код не знает, какая это планета.
    """
    name = "?"

    def create_gravity(self):
        raise NotImplementedError

    def create_atmosphere(self):
        raise NotImplementedError


class EarthFactory(PlanetFactory):
    name = "Земля"

    def create_gravity(self):
        return Gravity(9.81)

    def create_atmosphere(self):
        return Atmosphere(1.225)


class MoonFactory(PlanetFactory):
    name = "Луна"

    def create_gravity(self):
        return Gravity(1.62)

    def create_atmosphere(self):
        return Atmosphere(0.0)  # атмосферы нет


class MarsFactory(PlanetFactory):
    name = "Марс"

    def create_gravity(self):
        return Gravity(3.71)

    def create_atmosphere(self):
        return Atmosphere(0.020)  # очень разреженная


# ---------- Прототип ----------

class Shot:
    """
    Паттерн «Прототип»: вместо ввода всех параметров заново
    берём готовый снаряд-образец и копируем его методом clone().
    """

    def __init__(self, name, mass, diameter, cx, speed=50, angle=45):
        self.name = name
        self.mass = mass          # кг
        self.diameter = diameter  # м
        self.cx = cx              # коэффициент сопротивления формы
        self.speed = speed        # м/с
        self.angle = angle        # градусы

    def clone(self):
        # все поля - числа и строки, поэтому поверхностной копии достаточно
        return copy.copy(self)


# каталог образцов
CATALOG = {
    "1": Shot("Пушечное ядро", 4.0, 0.10, 0.47),
    "2": Shot("Теннисный мяч", 0.057, 0.067, 0.55),
    "3": Shot("Бадминтонный волан", 0.005, 0.068, 0.60),
}


def fly(shot, planet):
    """Полёт методом Эйлера с шагом 0.001 с. Возвращает дальность, м."""
    gravity = planet.create_gravity()
    air = planet.create_atmosphere()
    a = math.radians(shot.angle)
    vx, vy = shot.speed * math.cos(a), shot.speed * math.sin(a)
    x = y = 0.0
    dt = 0.001
    while True:
        ax, ay = air.drag(vx, vy, shot)
        vx += ax * dt
        vy += (ay - gravity.g) * dt
        x += vx * dt
        y += vy * dt
        if y <= 0:
            return x


def main():
    planets = [EarthFactory(), MoonFactory(), MarsFactory()]

    print("=== Баллистика на разных планетах ===")
    for key, shot in CATALOG.items():
        print(f"  {key} - {shot.name}")
    prototype = CATALOG.get(input("Выберите снаряд: "))
    if prototype is None:
        print("Нет такого снаряда")
        return
    base = prototype.clone()
    base.speed = float(input("Скорость, м/с: "))

    print(f"\n{'Угол':<6}" + "".join(f"{p.name:>10}" for p in planets))
    best = {p.name: (0, 0) for p in planets}   # планета -> (дальность, угол)

    for angle in range(15, 76, 5):
        shot = base.clone()     # копия прототипа, меняем только угол
        shot.angle = angle
        row = f"{angle:<6}"
        for p in planets:
            distance = fly(shot, p)
            row += f"{distance:>10.1f}"
            if distance > best[p.name][0]:
                best[p.name] = (distance, angle)
        print(row)

    print()
    for name, (distance, angle) in best.items():
        print(f"{name}: лучший угол {angle} град, дальность {distance:.1f} м")
    print("Угол у исходного снаряда не изменился:", base.angle)


if __name__ == "__main__":
    main()
