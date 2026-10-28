"""
Лабораторная работа №5. Структурные паттерны: Фасад, Приспособленец.
Вариант 12 - «Расчёт баллистической траектории».

Пневматическая сеялка «выстреливает» семена на поле. Каждое семя летит
по своей траектории с сопротивлением воздуха: лёгкие падают ближе, тяжёлые дальше.
"""
import math
import random


# ---------- Приспособленец ----------

class SeedType:
    """
    Паттерн «Приспособленец»: общие данные культуры (масса, размер, форма)
    хранятся в одном объекте на всю культуру. Скорость и угол у каждого
    семени свои - они передаются в fly() параметрами.
    """

    def __init__(self, name, symbol, mass, diameter, cx):
        self.name = name
        self.symbol = symbol      # символ на карте поля
        self.mass = mass          # кг
        self.diameter = diameter  # м
        self.cx = cx              # коэффициент сопротивления

    def fly(self, speed, angle, height):
        """Дальность полёта одного семени, м (метод Эйлера, шаг 0.001 с)."""
        area = math.pi * self.diameter ** 2 / 4
        k = 0.5 * 1.225 * self.cx * area / self.mass
        vx = speed * math.cos(math.radians(angle))
        vy = speed * math.sin(math.radians(angle))
        x, y, dt = 0.0, height, 0.001
        while y > 0:
            v = math.hypot(vx, vy)
            vx -= k * v * vx * dt
            vy -= (9.81 + k * v * vy) * dt
            x += vx * dt
            y += vy * dt
        return x


class SeedTypeFactory:
    """Фабрика приспособленцев: на повторный запрос отдаёт уже созданный объект."""

    DATA = {  # название: (символ, масса кг, диаметр м, Cx)
        "горох": ("Г", 0.00025, 0.007, 0.47),
        "пшеница": ("П", 0.00004, 0.004, 0.50),
        "подсолнечник": ("С", 0.00008, 0.006, 0.60),
    }

    def __init__(self):
        self.cache = {}

    def get(self, name):
        if name not in self.cache:
            print(f"  (создан объект SeedType «{name}»)")
            self.cache[name] = SeedType(name, *self.DATA[name])
        return self.cache[name]


class Seed:
    """Конкретное семя: ссылка на общий вид + место падения."""

    def __init__(self, kind, x):
        self.kind = kind
        self.x = x


# ---------- Подсистема и Фасад ----------

class Nozzle:
    """Сопло: у каждого семени скорость и угол немного отличаются."""

    def __init__(self, height):
        self.height = height
        self.random = random.Random(12)   # фиксированное зерно - одинаковый результат

    def shoot(self, speed, angle):
        return speed * self.random.uniform(0.9, 1.1), angle + self.random.uniform(-5, 5)


class FieldMap:
    """Карта поля: полосы по 1 м, один символ = 10 семян."""

    def show(self, seeds):
        for strip in range(int(min(s.x for s in seeds)), int(max(s.x for s in seeds)) + 1):
            line = ""
            for name in SeedTypeFactory.DATA:
                count = sum(1 for s in seeds if s.kind.name == name and int(s.x) == strip)
                line += SeedTypeFactory.DATA[name][0] * round(count / 10)
            print(f"{strip:3d}-{strip + 1:<3d} м | {line}")


class Seeder:
    """
    Паттерн «Фасад»: прячет фабрику, сопло, карту и журнал
    за тремя простыми методами sow(), show(), save().
    """

    def __init__(self, nozzle_height=1.5):
        self.factory = SeedTypeFactory()
        self.nozzle = Nozzle(nozzle_height)
        self.field = FieldMap()
        self.seeds = []
        self.log = []

    def sow(self, crop, count, speed, angle):
        kind = self.factory.get(crop)
        total = 0.0
        for _ in range(count):
            v, a = self.nozzle.shoot(speed, angle)
            x = kind.fly(v, a, self.nozzle.height)
            self.seeds.append(Seed(kind, x))    # у всех семян один и тот же kind
            total += x
        line = (f"{crop}: {count} шт., v = {speed} м/с, угол = {angle}, "
                f"средняя дальность {total / count:.2f} м")
        print(line)
        self.log.append(line)

    def show(self):
        print("\nКарта поля (символ = 10 семян):")
        self.field.show(self.seeds)
        print(f"\nОбъектов Seed: {len(self.seeds)}, объектов SeedType: {len(self.factory.cache)}")

    def save(self, file_name):
        with open(file_name, "w", encoding="utf-8") as f:
            f.write("\n".join(self.log) + "\n")
        print("Итоги сохранены в", file_name)


def main():
    print("=== Пневматическая сеялка ===")
    print("Культуры:", ", ".join(SeedTypeFactory.DATA), "(пустая строка - закончить)")
    seeder = Seeder()
    while True:
        crop = input("Культура: ").strip().lower()
        if not crop:
            break
        if crop not in SeedTypeFactory.DATA:
            print("Неизвестная культура")
            continue
        count = int(input("Количество семян: "))
        speed = float(input("Скорость, м/с: "))
        angle = float(input("Угол, град: "))
        seeder.sow(crop, count, speed, angle)

    if seeder.seeds:
        seeder.show()
        seeder.save("sowing.txt")


if __name__ == "__main__":
    main()
