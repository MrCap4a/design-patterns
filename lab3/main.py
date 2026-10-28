"""
Лабораторная работа №3. Структурные паттерны: Адаптер, Мост.
Вариант 12 - «Расчёт баллистической траектории».

Выстрел можно рассчитать своими формулами или старым «артиллерийским»
модулем через адаптер. Отчёт (краткий/подробный) выводится в консоль или в файл.
"""
import math

G = 9.81


# ---------- Адаптер ----------

class Calculator:
    """Интерфейс, с которым работает программа: скорость в м/с, угол в градусах."""

    def calculate(self, speed, angle):
        """Возвращает словарь: дальность (м), высота (м), время (с)."""
        raise NotImplementedError


class PhysicsCalculator(Calculator):
    """Наш калькулятор по формулам физики."""

    def calculate(self, speed, angle):
        a = math.radians(angle)
        return {
            "distance": speed ** 2 * math.sin(2 * a) / G,
            "height": (speed * math.sin(a)) ** 2 / (2 * G),
            "time": 2 * speed * math.sin(a) / G,
        }


class OldArtilleryTable:
    """
    «Чужой» старый модуль, менять его нельзя. Неудобный интерфейс:
    угол в делениях угломера (круг = 6000 делений), скорость в км/ч,
    дальность в километрах.
    """

    def range_km(self, mils, kmh):
        v = kmh / 3.6
        return v ** 2 * math.sin(2 * mils / 6000 * 2 * math.pi) / G / 1000

    def apex_m(self, mils, kmh):
        vy = kmh / 3.6 * math.sin(mils / 6000 * 2 * math.pi)
        return vy ** 2 / (2 * G)

    def flight_s(self, mils, kmh):
        vy = kmh / 3.6 * math.sin(mils / 6000 * 2 * math.pi)
        return 2 * vy / G


class ArtilleryAdapter(Calculator):
    """
    Паттерн «Адаптер»: реализует наш интерфейс Calculator,
    а внутри переводит единицы и вызывает старый модуль.
    """

    def __init__(self, table):
        self.table = table  # адаптируемый объект

    def calculate(self, speed, angle):
        mils = angle / 360 * 6000   # градусы -> деления угломера
        kmh = speed * 3.6           # м/с -> км/ч
        return {
            "distance": self.table.range_km(mils, kmh) * 1000,  # км -> м
            "height": self.table.apex_m(mils, kmh),
            "time": self.table.flight_s(mils, kmh),
        }


# ---------- Мост ----------

class Output:
    """Реализация моста: куда выводить строки."""

    def write(self, text):
        raise NotImplementedError

    def close(self):
        pass


class ConsoleOutput(Output):
    def write(self, text):
        print(text)


class FileOutput(Output):
    def __init__(self, file_name):
        self.file_name = file_name
        self.lines = []

    def write(self, text):
        self.lines.append(text)

    def close(self):
        with open(self.file_name, "w", encoding="utf-8") as f:
            f.write("\n".join(self.lines) + "\n")
        print("Отчёт сохранён в", self.file_name)


class Report:
    """
    Паттерн «Мост»: абстракция «отчёт» хранит ссылку на реализацию Output.
    Любой вид отчёта работает с любым способом вывода.
    """

    def __init__(self, output):
        self.out = output

    def show(self, result):
        raise NotImplementedError


class ShortReport(Report):
    def show(self, r):
        self.out.write(f"Дальность {r['distance']:.2f} м, высота {r['height']:.2f} м")
        self.out.close()


class FullReport(Report):
    def show(self, r):
        self.out.write("=== Подробный отчёт ===")
        self.out.write(f"Дальность: {r['distance']:.2f} м")
        self.out.write(f"Высота:    {r['height']:.2f} м")
        self.out.write(f"Время:     {r['time']:.2f} с")
        self.out.write("Точки траектории (x; y):")
        for i in range(6 if r["distance"] > 0 else 0):
            # без сопротивления воздуха траектория - парабола через (0;0), (L;0) и вершину
            x = r["distance"] * i / 5
            y = 4 * r["height"] * x * (r["distance"] - x) / r["distance"] ** 2
            self.out.write(f"  {x:8.2f}; {y:6.2f}")
        self.out.close()


def main():
    print("=== Отчёты о выстреле ===")
    speed = float(input("Скорость, м/с: "))
    angle = float(input("Угол, град: "))

    if input("Расчёт: 1 - формулы, 2 - старый модуль: ") == "2":
        calculator = ArtilleryAdapter(OldArtilleryTable())
    else:
        calculator = PhysicsCalculator()

    if input("Вывод: 1 - консоль, 2 - файл: ") == "2":
        output = FileOutput("report.txt")
    else:
        output = ConsoleOutput()

    if input("Отчёт: 1 - краткий, 2 - подробный: ") == "2":
        report = FullReport(output)
    else:
        report = ShortReport(output)

    report.show(calculator.calculate(speed, angle))


if __name__ == "__main__":
    main()
