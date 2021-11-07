import math
from random import randint
import pygame
from pygame.draw import *
import numpy as np


FPS = 60

RED = (255, 0, 0)
YELLOW = (255, 165, 0)
GREEN = (74, 156, 84)
PURPLE1 = (134, 60, 174)
PURPLE2 = (185, 106, 172)
GREY = (99, 96, 103)
LIGHTGREY = (187, 187, 187)
BALLS_COLORS = [RED, GREEN]  # цвет снарядов
TARGET_COLORS = [RED, PURPLE1, PURPLE2]  # цвет целей (не бомбочек)

WIDTH = 800  # задает ширину экрана
HEIGHT = 600  # задает высоту экрана

gun_surf_y = 470  # задает координаты танка
gun_surf_x = 90
gun_y = gun_surf_y + 75  # задает координаты пушки
gun_x = gun_surf_x + 75

H = [0, 0, 0]  # величина, изменяющаяся за партию игры. с каждым попаданием по
# бомбе (серому шарику) эта величина увеличивается и бомба возвращается на спавн
ch = 0  # величина, характеризующая сколько шариков за пределами игровой площадки
const_bullet = 0  # величина, характеризующая сколько всего шариков потребовалось
name = ''  # имя игрока
bomb_md = 0  # мод "бомбочка" 0 -отключено; 1 - включено

time_bomb = [90, 221, 354]  # время, за которое бомба n достигает игровую площадку
tik = 1  # игровая единица времени

v_tank = 5  # скорость танка
situation = 0  # используется чтобы проверить заряжается ли пушка. создана для того,
# пушка рисовалась во время event
bullet = 0  # кол-во затраченных пуль на данный момент. величина динамичная
t = 0  # "время", используется в промежутке после поражении цели
target_number_const = 5  # кол-во целей с вычетом бомбочек
target_number = target_number_const  # кол-во живых целей (не бомбочек)

pygame.init()

font = pygame.font.Font(None, 30)  # шрифт текста

screen = pygame.display.set_mode((WIDTH, HEIGHT))  # игровая площадь
screen.fill((255, 255, 255))

gun_surface = pygame.Surface((1100, 1500), pygame.SRCALPHA)  # площадь танка
gun_surface.fill(0)


class Ball:

    def __init__(self, vx=0, vy=0):
        """ Конструктор класса ball

        Args:
        x - начальное положение мяча по горизонтали
        y - начальное положение мяча по вертикали
        r - радиус мяча
        vx - скорость мяча по горизонтали
        vy - скорость мяча по вертикали
        color - цвет мяча
        """
        self.x = gun_x
        self.y = gun_y
        self.r = 10
        self.vx = vx
        self.vy = vy
        self.color = BALLS_COLORS[randint(1, 1)]

    def move(self):
        """Переместить мяч по прошествии единицы времени.

        Метод описывает перемещение мяча за один кадр перерисовки. То есть, обновляет значения
        self.x и self.y с учетом скоростей self.vx и self.vy, силы гравитации, действующей на мяч,
        и стен по краям окна (размер окна 800х600).
        """

        '''задает движение мяча'''
        if self.vy != 0 and self.color == RED:
            self.vy -= 1
        self.x += self.vx
        self.y -= self.vy

        '''задает границы мяча'''
        if self.x >= -self.r + 800:
            self.vx *= -1
        if self.y >= 600 - self.r:
            self.vy *= -1

            '''замедляет мяч при ударении с полом'''
            if self.vy >= 1:
                self.vy = (self.vy ** 2 - (self.vy * 0.7) ** 2) ** 0.5  # аналогия с ЗСЭ
            else:
                self.vy = 0

            if self.vx >= 1:
                self.vx = (self.vx ** 2 - (self.vx * 0.5) ** 2 ) ** 0.5
            elif self.vx <= 1:
                self.vx = -1 * (self.vx ** 2 - (self.vx * 0.5) ** 2 ) ** 0.5
            else:
                self.vx = 0

        '''возвращает мяч если тот вышел за границы'''
        if self.x >= 800:
            self.x -= self.r + 10
        if self.y >= 600:
            self.y -= self.r + 10

    def draw(self):
        """рисует мячик"""

        circle(
            screen,
            self.color,
            (self.x, self.y),
            self.r
        )

    def hittest(self, inf):
        """Функция проверяет сталкивалкивается ли данный обьект с целью, описываемой в обьекте obj.

        Args:
            obj: Обьект, с которым проверяется столкновение.
        Returns:
            Возвращает True в случае столкновения мяча и цели. В противном случае возвращает False.
        """

        if (self.x - inf[0]) ** 2 + (self.y - inf[1]) ** 2 < (self.r + inf[2]) ** 2:
            return True
        return False


class Gun:

    def __init__(self):
        """
        f2_power - мощность пушки, чем дольше держишь лкм, тем быстрее вылетит шар
        f2_on - показатель, отвечающий, заряжается ли пушка
        an - угол пушки с гор плоскостью в радианах
        color - цвет пушки
        x, y - координаты оси поворота пушки
        l - длина пушки
        dl - разность длины за один кадр прописовки
        width - ширина пушки
        """

        self.f2_power = 10
        self.f2_on = 0
        self.an = 1
        self.color = (58, 63, 38)
        self.x = 75
        self.y = 75
        self.l = 20
        self.dl = 1
        self.width = 10

    def fire2_start(self):
        """активирует пушку (пушка накапливает мощность)"""

        self.f2_on = 1

    def fire2_end(self):
        """Выстрел мяча.

        Происходит при отпускании кнопки мыши.
        Начальные значения компонент скорости мяча vx и vy зависят от положения мыши.
        """

        global balls, bullet
        bullet += 1
        a = abs(self.an)
        vx = self.f2_power * math.cos(a)
        vy = self.f2_power * math.sin(self.an)
        if t == 0:
            new_ball = Ball(vx, vy)
            balls.append(new_ball)
        if len(balls) > 1:
            del balls[0]
        self.f2_on = 0
        self.f2_power = 10

    def targetting(self, event):
        """Прицеливание. Зависит от положения мыши."""

        self.an = math.atan2(
            (gun_y - event.pos[1]),
            (event.pos[0] - gun_x)
        )

    def check(self):
        """проверяет, заряжается ли пушка'"""

        return(self.f2_on)

    def draw(self):
        """рисует пушку в зависимости от угла"""

        '''рисует плоскость на которой рисуется пушка, та в свою очередь
        рисуется на поверхности экрана'''
        gun_surface.fill(0)

        '''если пушка заряжается, то пушка меняет цвет и удлиняется'''
        if self.f2_on == 1:
            self.color = YELLOW
            if self.l < 70:
                self.l += self.dl
        else:
            self.color = (58, 63, 38)
            self.l = 20

        '''рисует пушку'''
        a = self.an
        polygon(
            gun_surface,
            (self.color),
            [
                (self.x, self.y),
                (self.x + self.width * np.sin(a), self.y + self.width * np.cos(a)),
                (
                    self.x + self.l * np.cos(a) + self.width * np.sin(a),
                    self.y - self.l * np.sin(a) + self.width * np.cos(a)
                ),
                (self.x + self.l * np.cos(a), self.y - self.l * np.sin(a)),
            ]
        )

    def power_up(self):
        """задает мощность выстрела"""

        if self.f2_on:
            self.f2_power = self.l / 2


class Target:

    def __init__(self):
        """Инициализация новой цели.
        self.r - радиус цели
        self.x - координата цели по х
        self.y - координата цели по у
        self.A - если True - движется налево, False - направо или просто показатель
        направления движения
        self.color - цвет цели
        self.armor - броня цели
        """

        self.r = randint(20, 50)
        self.x = randint(self.r + 40, 760 - self.r)
        self.y = randint(self.r + 40, 360 - self.r)
        self.A = True
        self.color = TARGET_COLORS[randint(0, 1)]
        self.armor = 100

    def inf(self):
        """возвращает координаты мишени и побочную информацию"""

        return(self.x, self.y, self.r, self.color, self.armor)

    def deinf(self):
        """делает бронированную цель менее прочной"""

        self.armor -= 50
        self.color = TARGET_COLORS[2]

    def draw(self):
        """рисует цель"""

        circle(
            screen,
            self.color,
            (self.x, self.y),
            self.r
        )
        if self.color == TARGET_COLORS[1] or self.color == TARGET_COLORS[2]:
            if self.A:
                self.x -= 5
            else:
                self.x += 5
            if self.x + self.r >= WIDTH:
                self.A = True
            if self.x - self.r <= 0:
                self.A = False


    def new_target(self):
        """рисует новую цель, если предыдущая была уничтожена"""

        self.x = randint(100, 730)
        self.y = randint(100, 450)
        self.r = randint(20, 50)
        self.color = TARGET_COLORS[randint(0, 1)]
        self.armor = 100

    def dele(self):
        """удаляет уничтоженную цель"""

        self.r = -10

    def move(self, tik, j, time_bomb, H):
        """рисует бомбочку и заставляет ее двигаться"""

        self.x = j * 200 + 150  # координаты каждый бомбочки по х
        self.y = 2 * tik - time_bomb[j] - H[j]  # "--"--" по у
        self.r = 30
        circle(
            screen,
            GREY,
            (self.x, self.y),
            self.r
        )


def draw_text(text, x, y):
    txt_surface = font.render(text, True, (0, 0, 0))
    screen.blit(txt_surface, (x, y))


def targets_draw(targets):
    """рисует цели"""

    for i, target in enumerate(targets):
        if i > target_number_const - 1:
            break
        target.draw()


def new_targets(targets):
    """рисует новые цели, после победы партии"""

    for i, t in enumerate(targets):
        if i < target_number_const:
            t.new_target()


def draw_tank():
    """рисует танк и заставляет его двигаться"""

    tank_surface = pygame.Surface((100, 150), pygame.SRCALPHA)
    tank_surface.fill(0)
    ellipse(tank_surface, (78, 96, 58), (25, 0, 45, 35))
    ellipse(tank_surface, (112, 148, 75), (0, 20, 100, 50))
    screen.blit(tank_surface, (gun_surf_x + 30, gun_surf_y + 70))


def bomb(tik, time_bomb, H, targets):
    """рисует "гнезда" бомб и создает бомбочки"""

    ellipse(screen, (0, 0, 0), (100, -10, 100, 20))
    ellipse(screen, (0, 0, 0), (300, -10, 100, 20))
    ellipse(screen, (0, 0, 0), (500, -10, 100, 20))
    for j, target in enumerate(targets):
        if j > target_number_const - 1:
            k = j - target_number_const
            target.move(tik, k, time_bomb, H)


def check(y, r):
    """проверяет, бомбочка вошла в игровую область или нет"""

    if y + r <= 0:
        return True
    return False


def check2(targets):
    """проверяет, не упала ли бомбочка не землю"""

    for tar in targets:
        (x, y, r, color, armor) = tar.inf()
        if y + r >= HEIGHT:
            return True
    return False


def draw_field():
    """рисует поле личных данных игрока"""

    text = 'Введите имя. Имя должно содержать не менее трех символов'
    txt_surface = font.render(text, True, (0, 0, 0))
    screen.blit(txt_surface, (80, 250))
    polygon(screen, LIGHTGREY, [(300, 280), (300, 320), (500, 320), (500, 280)])
    polygon(screen, GREEN, [(520, 280), (520, 320), (560, 320), (560, 280)])


def name_writing():
    """получает на вход имя персонажа"""

    draw_field()
    name = ''

    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return name
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                    draw_field()
                else:
                    name += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.pos[0] >= 520 and event.pos[0] <= 560 and event.pos[1] >= 280 and event.pos[1] <= 320:
                    return name

        draw_text(name, 310, 290)
        pygame.display.update()


def buttons():
    """рисует поле с регулятором сложности игры"""

    polygon(screen, RED, [(320, 280), (320, 320), (360, 320), (360, 280)])
    polygon(screen, GREEN, [(370, 280), (370, 320), (410, 320), (410, 280)])
    draw_text('Хотите ли вы усложненный вариант игры?', 160, 250)
    draw_text('Да', 375, 290)
    draw_text('Нет', 325, 290)
    pygame.display.update()


def bomb_mode():
    """регулятор сложности игры. она заключается в существовании бомбочек"""

    buttons()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.pos[0] >= 370 and event.pos[0]\
                        <= 410 and event.pos[1] >= 280 and event.pos[1] <= 320:
                    return 1
                if event.pos[0] >= 320 and event.pos[0]\
                        <= 360 and event.pos[1] >= 280 and event.pos[1] <= 320:
                    return 0


finished = False

clock = pygame.time.Clock()

bomb_md = bomb_mode()
if bomb_md == 1:
    bomb_count = 3
else:
    bomb_count = 0

targets = [Target() for _ in range(bomb_count + target_number_const)]  # массив
# класса #target
gun = Gun()  # пушка
balls = [Ball() for _ in range(0)]  # массив класса balls

while not finished:
    if len(str(name)) < 3:
        screen.fill((255, 255, 255))
        name = name_writing()
    else:
        clock.tick(FPS)
        screen.fill((255, 255, 255))

        situation = gun.check()
        targets_draw(targets)
        bomb(tik, time_bomb, H, targets)

        if gun_surf_x > WIDTH - 130:
            v_tank = -5
        elif gun_surf_x < -20:
            v_tank = 5

        gun_surf_x += v_tank
        gun_x = gun_surf_x + 75

        if situation == 1:
            gun.draw()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                finished = True
            if event.type == pygame.MOUSEMOTION:
                gun.targetting(event)
                gun.draw()
            if event.type == pygame.MOUSEBUTTONDOWN:
                gun.fire2_start()
            if event.type == pygame.MOUSEBUTTONUP:
                gun.power_up()
                gun.fire2_end()
                gun.draw()

        if check2(targets) and t < 100:
            t += 1
            draw_text('Вы проиграли', 300, 300)
            for i in range(3):
                H[i] = -10000
            for target in targets:
                target.dele()

        if check2(targets) and t == 100:
            with open('results.JSON', 'a') as output:  # запись результата
                print('name: ', 'test name', '\n', 'Lose score: ', bullet, '\n', file=output)
            new_targets(targets)
            bullet = 0
            const_bullet = 0
            target_number = target_number_const
            t = 0
            tik = 0
            for i in range(3):
                H[i] = 0

        for b in balls:
            b.move()
        for i, b in enumerate(balls):
            if t == 0:
                ch = 0
            for j, target in enumerate(targets):
                (x, y, r, color, armor) = target.inf()
                b.draw()
                if check(y, r):
                    ch += 1
                if b.hittest((x, y, r)):
                    if j < target_number_const:
                        if color == TARGET_COLORS[0] or armor == 50:
                            target.dele()
                            target_number -= 1
                        else:
                            target.deinf()
                    else:
                        H[j - target_number_const] +=\
                            time_bomb[j - target_number_const] + y
                        ch += 1
                    if len(balls) > 0:
                        del balls[0]
                    const_bullet = bullet

        if target_number == 0 and ch == bomb_count:
            for i in range(3):
                H[i] = 10000
            t += 1
            draw_text(
                "Вы уничтожили цель за " + str(const_bullet) + ' выстрелов.',
                200, 300
            )

        if t == 100:
            with open('results.JSON', 'a') as output:  # запись результата
                print('name: ', name, '\n', 'Win score: ', bullet, '\n', file=output)
            new_targets(targets)
            bullet = 0
            const_bullet = 0
            target_number = target_number_const
            t = 0
            tik = 0
            for i in range(3):
                H[i] = 0

        draw_text(str(const_bullet), 40, 10)
        screen.blit(gun_surface, (gun_surf_x, gun_surf_y))
        draw_tank()
        tik += 1

        pygame.display.update()

pygame.quit()
