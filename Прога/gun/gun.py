import math
from random import randint
import pygame
from pygame.draw import *
import numpy as np


FPS = 60

RED = (255, 0, 0, 255)
BLACK = (0, 0, 0, 255)
YELLOW = (255, 165, 0, 255)
WIDTH = 800
HEIGHT = 600
situation = 0  # используется чтобы проверить заряжается ли пушка
bullet = 0  # кол-во попыток чтобы попасть в цель
t = 0  # "время", используется в промежутке после поражении цели
k = 0  # ситуация, когда происходит пауза между поражением и появлением цели

pygame.init()

font = pygame.font.Font(None, 30)  # шрифт текста

screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen.fill((255, 255, 255))

gun_surface = pygame.Surface((110, 150), pygame.SRCALPHA)
gun_surface.fill((0))


class Ball:

    def __init__(self, vx=40, vy = 400):
        """ Конструктор класса ball

        Args:
        x - начальное положение мяча по горизонтали
        y - начальное положение мяча по вертикали
        r - радиус мяча
        vx - скорость мяча по горизонтали
        vy - скорость мяча по вертикали
        color - цвет мяча
        """
        self.x = 30
        self.y = 400
        self.r = 10
        self.vx = vx
        self.vy = vy
        self.color = RED

    def move(self):
        """Переместить мяч по прошествии единицы времени.

        Метод описывает перемещение мяча за один кадр перерисовки. То есть, обновляет значения
        self.x и self.y с учетом скоростей self.vx и self.vy, силы гравитации, действующей на мяч,
        и стен по краям окна (размер окна 800х600).
        """

        '''задает движение мяча'''
        if self.vy !=0:
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
                self.vy = (self.vy ** 2 - (self.vy * 0.7) ** 2 ) ** 0.5
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

    def draw(self, s):
        '''рисует мячик'''

        '''рисует белый мачик поверх красного, чтобы создать анимацию движения
        либо рисует красный шарик (новое положение шарика)'''
        if s == 'white':
            circle(
                screen,
                (255, 255, 255),
                (self.x, self.y),
                self.r
            )
        else:
            if k == 0:
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
        '''
        f2_power - мощность пушки, чем дольше держишь лкм, тем быстрее вылетит шар
        f2_on - показатель, отвечающий, заряжается ли пушка
        an - угол пушки с гор плоскостью в радианах
        color - цвет пушки
        x, y - координаты оси поворота пушки
        l - длина пушки
        dl - разность длины за один кадр прописовки
        width - ширина пушки
        '''

        self.f2_power = 10
        self.f2_on = 0
        self.an = 1
        self.color = BLACK
        self.x = 30
        self.y = 400 - 325
        self.l = 20
        self.dl = 1
        self.width = 10

    def fire2_start(self):
        '''активирует пушку (пушка накапливает мощность)'''

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
        new_ball = Ball(vx, vy)
        balls.append(new_ball)
        if len(balls) > 1:
            del balls[0]
        self.f2_on = 0
        self.f2_power = 10

    def targetting(self, event):
        """Прицеливание. Зависит от положения мыши."""
        self.an = math.atan2(
            (400 - event.pos[1]),
            (event.pos[0] - 30)
        )

    def check(self):
        '''проверяет, заряжается ли пушка'''

        return(self.f2_on)


    def draw(self):
        '''рисует пушку в зависимости от угла'''

        '''рисует плоскость на которой рисуется пушка, та в свою очередь
        рисуется на поверхности экрана'''
        gun_surface.fill((0, 0, 0))
        gun_surface.fill((0))

        '''если пушка заряжается, то пушка меняет цвет и удлиняется'''
        if self.f2_on == 1:
            self.color = YELLOW
            if self.l < 70:
                self.l += self.dl
        else:
            self.color = BLACK
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

        '''рисует плоскость пушки на экране'''


    def power_up(self):
        '''задает мощность выстрела'''

        if self.f2_on:
            self.f2_power = self.l / 2


class Target:

    def __init__(self):
        """ Инициализация новой цели. """
        self.r = randint(20, 50)
        self.x = randint(600, 800 - self.r)
        self.y = randint(100, 600 - self.r)
        self.color = RED

    def inf(self):
        '''возвращает координаты мишени'''

        return(self.x, self.y, self.r)

    def draw(self):
        '''рисует мишень'''

        target_surface = pygame.Surface((1000, 1000), pygame.SRCALPHA)
        #target_surface.fill(0)

        circle(
            target_surface,
            self.color,
            (self.x, self.y),
            self.r
        )
        screen.blit(target_surface, (0, 0))

    def new_target(self):
        '''рисует новую мишень, если предыдущая была уничтожена'''

        self.x = randint(600, 780)
        self.y = randint(300, 550)
        self.r = randint(20, 50)

    def dele(self):
        '''удаляет уничтоженный шарик'''

        self.r = -10

def targets_draw(targets):
    for t in targets:
        t.draw()


balls = [Ball() for _ in range(0)]

clock = pygame.time.Clock()
gun = Gun()
targets = [Target() for _ in range(2)]
finished = False

while not finished:
    situation = gun.check()
    clock.tick(FPS)

    if situation == 1:
        gun.draw()
        targets_draw(targets)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finished = True
        if event.type == pygame.MOUSEMOTION:
            gun.targetting(event)
            gun.draw()
            targets_draw(targets)
        if event.type == pygame.MOUSEBUTTONDOWN:
            gun.fire2_start()
        if event.type == pygame.MOUSEBUTTONUP:
            gun.power_up()
            gun.fire2_end()

    for i, b in enumerate(balls):
        for target in targets:
            (x, y, r) = target.inf()
            if i + 1 == len(balls):  # ненужная хрень
                b.draw('white')
                gun.draw()
                target.draw()
                check = b.move()
                b.draw('')
                if b.hittest((x, y, r)):
                    target.dele()
                    circle(
                        screen,
                        (255, 255, 255),
                        (x, y),
                        r
                    )
                    const_bullet = bullet
                    k = 1 #начинается отсчет времени
    if k == 1:
        t += 1

        text_surf1 = font.render \
                (
                "Вы уничтожили цель за " + str(const_bullet) + ' выстрелов.',
                False,
                (0, 0, 0)
            )
        screen.blit(text_surf1, (200, 300))
    if t == 100:
        target.new_target()
        bullet = 0
        const_bullet = 0
        k = 0
        t = 0

    text_surf2 = font.render \
            (
            str(bullet),
            False,
            (0, 0, 0)
        )
    screen.blit(text_surf2, (40, 10))
    screen.blit(gun_surface, (0, 325))

    pygame.display.update()


pygame.quit()
