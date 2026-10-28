"""
Лабораторная работа №4. Структурные паттерны: Компоновщик, Декоратор.
Вариант 12 - «Расчёт баллистической траектории».

Расчёт салюта. Заряд взлетает, взрывается и выпускает вложенные заряды
и звёздочки - это дерево (Компоновщик). Силы, действующие на частицы,
набираются обёртками (Декоратор).
"""
import math


# ---------- Декоратор ----------

class Force:
    """Общий интерфейс: и базовая сила, и обёртки умеют считать ускорение."""

    def acceleration(self, vx, vy):
        raise NotImplementedError

    def describe(self):
        raise NotImplementedError


class Gravity(Force):
    """Базовый компонент: только сила тяжести."""

    def acceleration(self, vx, vy):
        return 0.0, -9.81

    def describe(self):
        return "тяжесть"


class ForceDecorator(Force):
    """
    Паттерн «Декоратор»: обёртка с тем же интерфейсом Force.
    Хранит обёрнутый объект и добавляет к его результату свою силу.
    """

    def __init__(self, inner):
        self.inner = inner

    def acceleration(self, vx, vy):
        return self.inner.acceleration(vx, vy)

    def describe(self):
        return self.inner.describe()


class AirDrag(ForceDecorator):
    """Сопротивление воздуха: a = -k * |v| * v."""
    K = 0.01

    def acceleration(self, vx, vy):
        ax, ay = self.inner.acceleration(vx, vy)
        v = math.hypot(vx, vy)
        return ax - self.K * v * vx, ay - self.K * v * vy

    def describe(self):
        return self.inner.describe() + " + воздух"


class Wind(ForceDecorator):
    """Ветер, упрощённо - постоянное горизонтальное ускорение."""

    def __init__(self, inner, push):
        super().__init__(inner)
        self.push = push

    def acceleration(self, vx, vy):
        ax, ay = self.inner.acceleration(vx, vy)
        return ax + self.push, ay

    def describe(self):
        return self.inner.describe() + f" + ветер ({self.push} м/с^2)"


def fly(x, y, speed, angle, duration, forces):
    """
    Полёт методом Эйлера в течение duration секунд.
    angle: 0 - вправо, 90 - вверх, 180 - влево, 270 - вниз.
    Возвращает (x, y, упал_ли_на_землю).
    """
    vx = speed * math.cos(math.radians(angle))
    vy = speed * math.sin(math.radians(angle))
    dt = 0.01
    for _ in range(int(duration / dt)):
        ax, ay = forces.acceleration(vx, vy)
        vx, vy = vx + ax * dt, vy + ay * dt
        x, y = x + vx * dt, y + vy * dt
        if y <= 0:
            return x, 0.0, True
    return x, y, False


# ---------- Компоновщик ----------

class FireworkElement:
    """Общий интерфейс элемента салюта."""

    def launch(self, x, y, forces, indent=""):
        raise NotImplementedError

    def count_stars(self):
        raise NotImplementedError


class Star(FireworkElement):
    """Лист дерева: звёздочка летит, пока не догорит."""

    def __init__(self, color, speed, angle, burn_time):
        self.color, self.speed, self.angle, self.burn_time = color, speed, angle, burn_time

    def launch(self, x, y, forces, indent=""):
        x, y, landed = fly(x, y, self.speed, self.angle, self.burn_time, forces)
        if landed:
            print(f"{indent}Звёздочка ({self.color}): ВНИМАНИЕ! упала горящей в x = {x:.1f}")
        else:
            print(f"{indent}Звёздочка ({self.color}): погасла в ({x:.1f}; {y:.1f})")

    def count_stars(self):
        return 1


class Shell(FireworkElement):
    """
    Паттерн «Компоновщик»: заряд содержит другие элементы (заряды или звёздочки)
    и работает с ними через тот же интерфейс launch() / count_stars().
    """

    def __init__(self, name, speed, angle, fuse_time):
        self.name, self.speed, self.angle, self.fuse_time = name, speed, angle, fuse_time
        self.children = []

    def add(self, element):
        self.children.append(element)
        return self

    def launch(self, x, y, forces, indent=""):
        x, y, landed = fly(x, y, self.speed, self.angle, self.fuse_time, forces)
        if landed:
            print(f"{indent}Заряд «{self.name}»: упал, не успев взорваться!")
            return
        print(f"{indent}Заряд «{self.name}»: взрыв в ({x:.1f}; {y:.1f})")
        for child in self.children:              # дети стартуют из точки взрыва
            child.launch(x, y, forces, indent + "    ")

    def count_stars(self):
        return sum(child.count_stars() for child in self.children)


def build_firework(speed):
    """Схема салюта: главный заряд, в нём «Пион», «Ива» и две звёздочки."""
    peony = Shell("Пион", 20, 60, 1.0)
    for angle in (0, 90, 180, 270):
        peony.add(Star("красная", 15, angle, 2.0))

    willow = Shell("Ива", 20, 120, 1.0)
    willow.add(Star("золотая", 8, 45, 4.5)).add(Star("золотая", 8, 135, 4.5))

    main_shell = Shell("Главный", speed, 88, 3.5)
    main_shell.add(peony).add(willow)
    main_shell.add(Star("белая", 25, 30, 1.5)).add(Star("белая", 25, 150, 1.5))
    return main_shell


def main():
    print("=== Расчёт салюта ===")
    forces = Gravity()
    if input("Учитывать воздух? (д/н): ") == "д":
        forces = AirDrag(forces)
    if input("Учитывать ветер? (д/н): ") == "д":
        forces = Wind(forces, float(input("Ускорение ветра, м/с^2: ")))
    speed = float(input("Скорость главного заряда, м/с: "))

    firework = build_firework(speed)
    print("Модель сил:", forces.describe())
    print("Звёздочек в салюте:", firework.count_stars())
    print()
    firework.launch(0.0, 0.0, forces)


if __name__ == "__main__":
    main()
