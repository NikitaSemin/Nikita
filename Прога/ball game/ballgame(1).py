import pygame
from pygame.draw import *
from random import randint
pygame.init()

FPS = 200
screen = pygame.display.set_mode((1200, 700))

RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
MAGENTA = (255, 0, 255)
CYAN = (0, 255, 255)
BLACK = (0, 0, 0)
COLORS = [RED, YELLOW, BLUE]

hit = 0 #суммарное кол-во очков
miss = 0 #суммарное кол-во промахов
number = 25 #кол-во шаров
font = pygame.font.Font(None, 30) #шрифт текста
name = input('Ведите, пожалуйста, свое имя: ')

class Ball:

    def __init__(self):
        '''задает данные'''
        self.x = randint(100, 1100)
        self.y = randint(100, 600)
        self.color = COLORS[randint(0, 2)]
        self.r = randint(10, 50)
        self.vx = randint(1, 5)
        self.vy = randint(1, 5)

        self.vl = 0 #vl - скорость колебаний
        self.d = 0 #величина характеризующая
        # на сколько меняется скорость vl
        self.k = 0 #величина характеризующая в пол или
        # отр сторону меняются скорость

    def draw(self):
        '''рисует новый шарик и делает движение
         желтого шарика колебательным'''
        B = self.y <= self.r + 6 or self.y >= (694 - self.r)

        if self.color == YELLOW: #заставляет колебаться
            if (self.k == 0 and self.vl < 5) or self.vl == -5:
                self.vl += self.d
                self.k = 0
            else:
                self.k = 1
            if self.k == 1 and self.vl > -5:
                self.vl -= self.d
            else:
                self.k = 0

        if B == True: #убирает колебания вблизь со стенкой
            self.vl = 0
            self.d = 0
        elif self.vl == 0 and B == False:
            self.d = 1

        self.x += self.vx #физика движения
        self.y += self.vy + self.vl

        # удар со стенкой
        if self.x <= self.r + 0 or self.x >= (1200 - self.r):
            self.vx *= -1
        if self.y <= self.r + 0 or self.y >= (700 - self.r):
            self.vy *= -1
        circle(screen, self.color, (self.x, self.y), self.r)

    def check(self, event):
        '''проверяет меткость'''
        x1 = event.pos[0]
        y1 = event.pos[1]
        (x, y, r) = (self.x, self.y, self.r)
        if ((x1-x)**2 + (y1-y)**2) <= r**2:
            return 1
        return 0

    def dele(self):
        '''удаляет шарик'''
        self.r = -1

    def inf(self):
        '''выносит данные шарика в код'''
        return(
        self.x, self.y, self.r,
        self.vx, self.vy, self.color
        )

    def change(self, vx, vy, x, y):
        '''меняет скорость шарика после удара'''
        self.vx = vx
        self.vy = vy
        self.x = x
        self.y = y

def vozvrat(x, y, r):
    '''отлепляет шарики, если они прилипли'''
    if y <= r - 3:
        y += 6
    if y >= (703 - r):
        y -= 6
    if x <= r - 3:
        x += 6
    if x >= (1203 - r):
        x -= 6
    return(x, y)

def razlom(x1, y1, x2, y2):
    '''отлепляет шарики, если они прилипли'''
    dx = x1 - x2
    dy = y1 - y2
    if dx != 0:
        nx = dx / abs(dx)
        x1 = x1 + 1 * nx
    if dy != 0:
        ny = dy / abs(dy)
        y1 = y1 + 1 * ny
    # n показывает какой шар правее а какой левее
    return(x1, y1, x2, y2)

def check2(inf1, inf2):
    '''проверяет удар, а также проверяет, не
    выпал ли шарик за границы. если выпал,
    то он перемещается в игровую область'''
    (x1, y1, r1, vx1, vy1, color) = inf1
    (x2, y2, r2, vx2, vy2, color) = inf2
    # color не используется в функции
    # меняет скорости при ударе
    if ((x1 - x2) ** 2 + (y1 - y2) ** 2 <= (r1 + r2) ** 2 + 10) \
            and r1 > 0 and r2 > 0:
        v = vx1
        vx1 = vx2
        vx2 = v
        v = vy1
        vy1 = vy2
        vy2 = v
    if (x1 - x2) ** 2 + (y1 - y2) ** 2 <= (r1 + r2) ** 2 + 3:
        (x1, y1, x2, y2) = razlom(x1, y1, x2, y2)
    # возвращает в игравоую область если шар застрял
    # причем он возращает в область так, чтобы он
    # ненароком не вошел в другой шар
    if (x1 - x2) ** 2 + (y1 - y2) ** 2 >= (r1 + r2) ** 2 + 40:
        (x1, y1) = vozvrat(x1, y1, r1)
        (x2, y2) = vozvrat(x2, y2, r2)
    return(
           vx1, vy1,
           vx2, vy2,
           x1, y1,
           x2, y2
    )

def chet1(ball, pool, event, hit, miss):
    '''подсчет попаданий и промахов'''
    if event.button == 1:
        k = 0
        for ball in pool:
            if ball.check(event) == 1:
                hit += 1
                ball.dele()
                k = 1
        if k == 0:
            miss += 1
    return(hit, miss)

def chet2(hit, miss):
    '''считает очки за игру с учетом промахов'''
    if miss >0:
        score = hit / miss
    else:
        score = hit
    return(score)

def check_best(score):
    '''проверяет лучший результат'''
    with open('best.txt', 'r') as output:
        for line in output:
            best_score = line.rstrip()
    best_score = float(best_score)
    if best_score < score:
        return(True)
    return(False)

pygame.display.update()
clock = pygame.time.Clock()
finished = False

pool = [Ball() for _ in range(number)]

while not finished:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finished = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            (hit, miss) = chet1(ball, pool, event, hit, miss)
            # счет промахов и попаданий

    #движение с соударениями
    i = -1
    for ball1 in pool: #0
        i += 1
        j = -1
        for ball2 in pool: #1
            j += 1
            if j > i:
                inf1 = ball1.inf()  # inf - информация о шаре
                inf2 = ball2.inf()
                if (inf1[5] == RED) * (inf2[5] == RED) == 1:
                    (
                     vx1, vy1,
                     vx2, vy2,
                     x1, y1,
                     x2, y2
                    ) = check2(inf1, inf2)
                    ball2.change(vx2, vy2, x2, y2)
                    ball1.change(vx1, vy1, x1, y1)
    for ball in pool:
        ball.draw()

    #вывод очков на экран
    text_surf = font.render\
    (
     "Scores: " + str(hit) + " miss: " + str(miss),
     False,
     (255, 255, 255)
     )
    screen.blit(text_surf, (0, 0))

    pygame.display.update()
    screen.fill(BLACK)

score = chet2(hit, miss) #счет очков

if check_best(score) == True: #обработка лучшего результата
    with open('best.txt', 'w') as input:
        print('name: ', name, '\n', score, file=input)

with open('results.JSON', 'a') as output: #запись результата
    print('name: ', name, '\n', 'score: ', score, '\n', file=output)

pygame.quit()