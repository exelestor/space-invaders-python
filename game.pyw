from tkinter import *
import random
import time
import os
import platform
import logging

WINDOW_WIDTH = 960
WINDOW_HEIGHT = 576
BGCOLOR = '#001133'
LOGLEVEL = 'DEBUG'

if platform.system() == 'Windows':
    keycodes = {
        "up":    38,
        "down":  40,
        "left":  37,
        "right": 39,
    
        "w": 87,
        "s": 83,
        "a": 65,
        "d": 68,
        "q": 81,
        "r": 82,
        "m": 77,
    
        "shot1": 16,
        "shot0": 45,
        "start": 13,
        "help":  72,
    }
elif platform.system() == 'Linux':
    keycodes = {
        "up":    111,
        "down":  116,
        "left":  113,
        "right": 114,
    
        "w": 25,
        "s": 39,
        "a": 38,
        "d": 40,
        "q": 24,
        "r": 27,
        "m": 58,
    
        "shot1": 65,
        "shot0": 105,
        "start": 36,
        "help":  43,
    }
else:
    print('OS is not supported.')
    exit(1)

logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, LOGLEVEL))
logging.basicConfig(format=u'%(asctime)s [%(levelname)s]  [%(filename)s:%(lineno)d] %(message)s', stream=sys.stdout)

# Класс для хранения игровых переменных
class Options:
    is_game_over = False
    points_to_win = 500 # при достижении этого числа игрок побеждает
    enemies_num = 20 # количество противников
    cell_size = 3 # размер клетки игрового поля
    fps = 100
    shot_speed = 7 # скорость полета пули
    shot_interval = 0.15 # интервал между выстрелами
    enemies_speed = 1 # скорость перемещения
    start = False
    help = False

    # Возвращает цвет игрока согласно его номеру
    def define_color(self, player_number):
        if player_number == 0:
            return '#FF00FF'
        elif player_number == 1:
            return '#00FFFF'
        else:
            return '#FFFFFF'


class Enemy:
    hp = 2

    # Перемещает противника на начальную позицию
    def init_coords(self):
        self.x = WINDOW_WIDTH + 11 * options.cell_size + random.randrange(0, 40 * options.cell_size)
        self.y = random.randrange(WINDOW_HEIGHT - 7 * options.cell_size * 2 - options.cell_size * 18) + options.cell_size * 8

    # Проверка пересечения области, в которой находится противник,
    # с прямоугольником, координаты вершин которого передаются в функцию.
    # Возвращается True/False.
    def check_collision(self, coordinates_array):
        return (
                self.x - 10 * options.cell_size / 2 <= coordinates_array[2] and
                self.y - 10 * options.cell_size / 2 <= coordinates_array[3] and
                self.x + 10 * options.cell_size / 2 >= coordinates_array[0] and
                self.y + 10 * options.cell_size / 2 >= coordinates_array[1]
        )

    # Перемещает противника по игровому полю и возвращает на
    # начальную позицию при его пересечении.
    def update(self):
        self.x -= options.enemies_speed
        canvas.coords(self.item, self.x, self.y)
        if self.x < -11 * options.cell_size:
            self.init_coords()

    # Уменьшает количество очков здоровья и меняет картинку (2 - зеленый, 1 - желтый, 0 - красный)
    def decrease_hp(self):
        self.hp = self.hp - 1
        if self.hp == 1:
            canvas.itemconfig(self.item, image=self.img_mid_hp)
        elif self.hp == 0:
            canvas.itemconfig(self.item, image=self.img_low_hp)
        elif self.hp < 0:
            self.hp = 2
            self.init_coords()
            canvas.itemconfig(self.item, image=self.img_ok_hp)

    # В конструкторе класса рисуется изображения и вызывается
    # функция перемещения противника на начальную позицию.
    def __init__(self):
        self.img_ok_hp = PhotoImage(file=os.getcwd()+'/images/enemy.png')
        self.img_mid_hp = PhotoImage(file=os.getcwd()+'/images/enemy1.png')
        self.img_low_hp = PhotoImage(file=os.getcwd()+'/images/enemy2.png')
        self.img_ok_hp = self.img_ok_hp.zoom(options.cell_size)
        self.img_mid_hp = self.img_mid_hp.zoom(options.cell_size)
        self.img_low_hp = self.img_low_hp.zoom(options.cell_size)
        self.init_coords()
        self.item = canvas.create_image(self.x, self.y, image=self.img_ok_hp)


class Player:
    hp = 3
    x = 50
    y = 50
    speed = 2
    number = 0
    score = 0
    shot_time = 0
    shot = [] # массив, в который помещаются экземпляры Shot()

    # Для создания полигона потребуется массив координат.
    # Фукнция строит его и возвращает в соответствии с
    # актуальной позицией кораблика.
    def get_shape(self):
        a = options.cell_size + 1
        b = a * 2
        c = a * 3

        # Контур кораблика :3
        #
        #    1-------+-------2 - - - +
        #    | ///// | ///// |       -
        #    | ///// | ///// |       -
        #    12-----11-------3-------4
        #    -       | ///// | ///// |
        #    -       | ///// | ///// |
        #    9------10-------6-------5
        #    | ///// | ///// |       -
        #    | ///// | ///// |       -
        #    8-------+-------7 - - - +
        return [
            0 + self.x, 0 + self.y,  # 1
            b + self.x, 0 + self.y,  # 2
            b + self.x, a + self.y,  # 3
            c + self.x, a + self.y,  # 4
            c + self.x, b + self.y,  # 5
            b + self.x, b + self.y,  # 6
            b + self.x, c + self.y,  # 7
            0 + self.x, c + self.y,  # 8
            0 + self.x, b + self.y,  # 9
            a + self.x, b + self.y,  # 10
            a + self.x, a + self.y,  # 11
            0 + self.x, a + self.y   # 12
        ]

    # Обновляет параметры кораблика
    def update(self):
        # Если очки здоровья закончились - удаляем элемент слоя
        if self.hp == 0:
            canvas.delete(self.item)
        else:
            # Передвигаем в актуальную позицию
            canvas.coords(self.item, self.get_shape())
            # Для каждой пули проверяем коллизию
            for i in self.shot:
                if i.coordinates[0] > WINDOW_WIDTH + 100:
                    self.shot.remove(i)
                elif i.check_collision():
                    self.shot.remove(i)
                i.update()

            # Проверяем коллизию игрока с врагами
            for i in enemies:
                if i.check_collision([
                    self.x, self.y,
                    self.x + (options.cell_size + 1) * 3, self.y + (options.cell_size + 1) * 3
                ]):
                    i.decrease_hp()
                    self.init_coords()
                    self.hp -= 1
                    lifes_bar.set_lifes_number(self.hp, self.number)

    def make_shot(self):
        if time.time() - self.shot_time > options.shot_interval:
            self.shot_time = time.time()
            self.shot.insert(0, Shot(self.number))

    # Возврат на начальную позицию
    def init_coords(self):
        self.x = 50
        if self.number == 0:
            self.y = WINDOW_HEIGHT / 2 - 50
        else:
            self.y = WINDOW_HEIGHT / 2 + 50

    # В конструкторе класса задается цвет кораблика в зависимости
    # от номера игрока, затем выполняется отрисовка.
    def __init__(self, number):
        self.number = number
        self.init_coords()
        self.item = canvas.create_polygon(self.get_shape(), fill=options.define_color(number))

    # При удалении объекта игрока удаляем также все его пули
    def __del__(self):
        del self.shot[:]


class Keyboard:
    up = False
    down = False
    left = False
    right = False
    w = False
    a = False
    s = False
    d = False
    shot0 = False
    shot1 = False
    q = False
    r = False
    m = False

    # При нажатии клавиши соответствующая ей переменная
    # принимает значение True. Вместе со следующей функцией
    # это позволяет осуществлять перемещения по двум осям
    # одновременно и делать выстрел независимо от того,
    # выполняется ли перемещение на данный момент.
    def keydown(self, event):
        logger.debug(event)
        if event.keycode == keycodes["up"]:
            self.up = True
        elif event.keycode == keycodes["down"]:
            self.down = True
        elif event.keycode == keycodes["left"]:
            self.left = True
        elif event.keycode == keycodes["right"]:
            self.right = True
        elif event.keycode == keycodes["w"]:
            self.w = True
        elif event.keycode == keycodes["s"]:
            self.s = True
        elif event.keycode == keycodes["a"]:
            self.a = True
        elif event.keycode == keycodes["d"]:
            self.d = True
        elif event.keycode == keycodes["q"]:
            self.q = True
        elif event.keycode == keycodes["r"]:
            self.r = True
        elif event.keycode == keycodes["m"]:
            self.m = True
        elif event.keycode == keycodes["shot1"]:
            self.shot1 = True
        elif event.keycode == keycodes["shot0"]:
            self.shot0 = True
        elif event.keycode == keycodes["start"]:
            options.start = True
        elif event.keycode == keycodes["help"]:
            options.help = not options.help

    # Если отпустить клавишу, соответствующая переменная
    # принимает значение False.
    def keyup(self, event):
        if event.keycode == keycodes["up"]:
            self.up = False
        elif event.keycode == keycodes["down"]:
            self.down = False
        elif event.keycode == keycodes["left"]:
            self.left = False
        elif event.keycode == keycodes["right"]:
            self.right = False
        elif event.keycode == keycodes["w"]:
            self.w = False
        elif event.keycode == keycodes["s"]:
            self.s = False
        elif event.keycode == keycodes["a"]:
            self.a = False
        elif event.keycode == keycodes["d"]:
            self.d = False
        elif event.keycode == keycodes["q"]:
            self.q = False
        elif event.keycode == keycodes["r"]:
            self.r = False
        elif event.keycode == keycodes["m"]:
            self.m = False
        elif event.keycode == keycodes["shot1"]:
            self.shot1 = False
        elif event.keycode == keycodes["shot0"]:
            self.shot0 = False

    # Проверка того, какие действия необходимо выполнить
    def check(self):
        if self.up and player[0].y > 0:
            player[0].y -= player[0].speed
        if self.down and player[0].y < WINDOW_HEIGHT - options.cell_size * 4:
            player[0].y += player[0].speed
        if self.left and player[0].x > 0:
            player[0].x -= player[0].speed
        if self.right and player[0].x < WINDOW_WIDTH - options.cell_size * 4:
            player[0].x += player[0].speed
        if self.w and player[1].y > 0:
            player[1].y -= player[1].speed
        if self.s and player[1].y < WINDOW_HEIGHT - options.cell_size * 4:
            player[1].y += player[1].speed
        if self.a and player[1].x > 0:
            player[1].x -= player[1].speed
        if self.d and player[1].x < WINDOW_WIDTH - options.cell_size * 4:
            player[1].x += player[1].speed
        if self.shot0 and player[0].hp > 0:
            player[0].make_shot()
        if self.shot1 and player[1].hp > 0:
            player[1].make_shot()


# Управление отображением очков здоровья
class LifesBar:
    def __init__(self):
        padding = options.cell_size * 5
        # Импортируем изображения, затем отрисовываем их. Объекты будут храниться в массиве.
        self.img1 = PhotoImage(file=os.getcwd()+'/images/heart1.png')
        self.img1 = self.img1.zoom(options.cell_size)
        self.img2 = PhotoImage(file=os.getcwd()+'/images/heart0.png')
        self.img2 = self.img2.zoom(options.cell_size)
        self.items = [
            canvas.create_image(
                WINDOW_WIDTH / 2 - padding,
                WINDOW_HEIGHT - padding * 1.5,
                image=self.img1
            ),
            canvas.create_image(
                WINDOW_WIDTH / 2 - padding - options.cell_size * 8,
                WINDOW_HEIGHT - padding * 1.5,
                image=self.img1
            ),
            canvas.create_image(
                WINDOW_WIDTH / 2 - padding - options.cell_size * 16,
                WINDOW_HEIGHT - padding * 1.5,
                image=self.img1
            ),
            canvas.create_image(
                WINDOW_WIDTH / 2 + padding,
                WINDOW_HEIGHT - padding * 1.5,
                image=self.img2
            ),
            canvas.create_image(
                WINDOW_WIDTH / 2 + padding + options.cell_size * 8,
                WINDOW_HEIGHT - padding * 1.5,
                image=self.img2
            ),
            canvas.create_image(
                WINDOW_WIDTH / 2 + padding + options.cell_size * 16,
                WINDOW_HEIGHT - padding * 1.5,
                image=self.img2
            ),
        ]

    # Отрисовываем переданое в функцию количество очков здоровья в соответствии с номером игрока
    def set_lifes_number(self, number, player):
        if player == 0:
            if number <= 2:
                canvas.delete(self.items[5])
            if number <= 1:
                canvas.delete(self.items[4])
            if number == 0:
                canvas.delete(self.items[3])
        elif player == 1:
            if number <= 2:
                canvas.delete(self.items[2])
            if number <= 1:
                canvas.delete(self.items[1])
            if number == 0:
                canvas.delete(self.items[0])


# Счетчики количества очков
class PointsBar:
    def __init__(self):
        self.padding = options.cell_size * 5
        # для левой и правой частей берем изображения разных цветов из папок numbers1 и numbers0 соответственно
        self.images = {
            'left': [PhotoImage(file=os.getcwd()+'/images/numbers1/' + str(i) + '.png') for i in range(0, 10)],
            'right': [PhotoImage(file=os.getcwd()+'/images/numbers0/' + str(i) + '.png') for i in range(0, 10)],
        }
        # увеличиваем изображения
        for i in range(0, 10):
            self.images['left'][i] = self.images['left'][i].zoom(options.cell_size)
            self.images['right'][i] = self.images['right'][i].zoom(options.cell_size)

        # здесь будем хранить отрисованные цифры для счетчика
        self.numbers = {
            'left': [
                canvas.create_image(
                    WINDOW_WIDTH / 2 - self.padding - options.cell_size * 25,
                    WINDOW_HEIGHT - self.padding * 1.5,
                    image=self.images['left'][0]
                ),
            ],
            'right': [
                canvas.create_image(
                    WINDOW_WIDTH / 2 + self.padding + options.cell_size * 25,
                    WINDOW_HEIGHT - self.padding * 1.5,
                    image=self.images['right'][0]
                ),
            ]
        }

    # указывает количество очков для определенного игрока
    def set_points_number(self, number, player):
        strnumber = str(number)

        # для удобства
        if player == 1:
            temp = 'left'
        else:
            temp = 'right'

        if number > 0:
            canvas.itemconfig(
                self.numbers[temp][0],
                image=self.images[temp][int(strnumber[len(strnumber) - 1])]
            )

        if number >= 10:
            exact_char = int(strnumber[len(strnumber) - 2])
            if len(self.numbers[temp]) == 1:
                if player == 0:
                    self.numbers[temp].insert(
                        0,
                        canvas.create_image(
                            WINDOW_WIDTH / 2 + self.padding + options.cell_size * 30,
                            WINDOW_HEIGHT - self.padding * 1.5,
                            image=self.images[temp][exact_char]
                        )
                    )
                elif player == 1:
                    self.numbers[temp].append(
                        canvas.create_image(
                            WINDOW_WIDTH / 2 - self.padding - options.cell_size * 30,
                            WINDOW_HEIGHT - self.padding * 1.5,
                            image=self.images[temp][exact_char]
                        )
                    )
            else:
                canvas.itemconfig(self.numbers[temp][1], image=self.images[temp][exact_char])

        if number >= 100:
            exact_char = int(strnumber[len(strnumber) - 3])
            if len(self.numbers[temp]) == 2:
                if player == 0:
                    self.numbers[temp].insert(
                        0,
                        canvas.create_image(
                            WINDOW_WIDTH / 2 + self.padding + options.cell_size * 35,
                            WINDOW_HEIGHT - self.padding * 1.5,
                            image=self.images[temp][exact_char])
                    )
                elif player == 1:
                    self.numbers[temp].append(
                        canvas.create_image(
                            WINDOW_WIDTH / 2 - self.padding - options.cell_size * 35,
                            WINDOW_HEIGHT - self.padding * 1.5,
                            image=self.images[temp][exact_char])
                    )
            else:
                    canvas.itemconfig(self.numbers[temp][2], image=self.images[temp][exact_char])


# выстрел
class Shot:
    coordinates = [] # массив с координатами пули

    def __init__(self, player_number):
        self.number = player_number
        self.coordinates = [
            player[self.number].x + options.cell_size * 5,
            player[self.number].y + options.cell_size + 1,
            player[self.number].x + options.cell_size * 6,
            player[self.number].y + options.cell_size * 2 + 1
        ]

        color = options.define_color(player_number)
        self.item = canvas.create_rectangle(self.coordinates, fill=color, outline=color)

    # при удалении пули убираем её с экрана
    def __del__(self):
        canvas.delete(self.item)
        logger.debug('Shot of player {} destroyed'.format(self.number))

    def check_collision(self):
        for i in enemies:
            if i.check_collision(self.coordinates) and i.x <= WINDOW_WIDTH + options.cell_size * 9:
                i.decrease_hp()
                player[self.number].score += 1
                points_bar.set_points_number(player[self.number].score, self.number)
                logger.debug('Player {} score: {}'.format(self.number, player[self.number].score))
                return True
        return False

    def update(self):
        self.coordinates[0] += options.shot_speed
        self.coordinates[2] += options.shot_speed
        canvas.coords(self.item, self.coordinates)


class Screens:
    game_name = 'Space Invaders'
    help_text_info = 'Нажмите ENTER, чтобы начать\nили h, чтобы показать правила'
    help_text_keys = """Управление:
Игрок 1
вверх: w
вниз: a
вправо: s
влево: d
огонь: L Shift
Игрок 2
(стрелочки)
огонь: Num 0 """
    help_text_rules = """Правила:
Игроки, перемещаясь в пространстве,
должны атаковать монстров и не сталкиваться с ними.
Каждое столкновение с монтром тратит одну жизнь.
По истечении трех жизней у одного из игроков
игра заканчивается, и объявляется победитель.
Если оба корабля выжили - выигрывает тот, что набрал 500 очков."""
    help_text_back = 'h - назад'

    def __init__(self):
        # координаты разных объектов на экране
        self.start_elements_coords = {
            'start': [
                WINDOW_WIDTH / 2 - 200, WINDOW_HEIGHT / 2 - 100,
                WINDOW_WIDTH / 2 + 200, WINDOW_HEIGHT / 2 - 100,
                WINDOW_WIDTH / 2 + 200, WINDOW_HEIGHT / 2 + 100,
                WINDOW_WIDTH / 2 - 200, WINDOW_HEIGHT / 2 + 100,
            ],
            'start_shadow': [
                WINDOW_WIDTH / 2 - 200 + 2, WINDOW_HEIGHT / 2 - 100 + 2,
                WINDOW_WIDTH / 2 + 200 + 2, WINDOW_HEIGHT / 2 - 100 + 2,
                WINDOW_WIDTH / 2 + 200 + 2, WINDOW_HEIGHT / 2 + 100 + 2,
                WINDOW_WIDTH / 2 - 200 + 2, WINDOW_HEIGHT / 2 + 100 + 2,
            ],
            'help': [
                WINDOW_WIDTH / 2 - 400, WINDOW_HEIGHT / 2 - 180,
                WINDOW_WIDTH / 2 + 400, WINDOW_HEIGHT / 2 - 180,
                WINDOW_WIDTH / 2 + 400, WINDOW_HEIGHT / 2 + 180,
                WINDOW_WIDTH / 2 - 400, WINDOW_HEIGHT / 2 + 180,
            ],
            'help_shadow': [
                WINDOW_WIDTH / 2 - 400 + 2, WINDOW_HEIGHT / 2 - 180 + 2,
                WINDOW_WIDTH / 2 + 400 + 2, WINDOW_HEIGHT / 2 - 180 + 2,
                WINDOW_WIDTH / 2 + 400 + 2, WINDOW_HEIGHT / 2 + 180 + 2,
                WINDOW_WIDTH / 2 - 400 + 2, WINDOW_HEIGHT / 2 + 180 + 2,
            ],
            'start_header': [
                WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 30
            ],
            'start_header_shadow': [
                WINDOW_WIDTH / 2 + 2, WINDOW_HEIGHT / 2 - 30 + 2
            ],
            'start_info': [
                WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 50
            ],
            'start_info_shadow': [
                WINDOW_WIDTH / 2 + 1, WINDOW_HEIGHT / 2 + 50 + 1
            ],
            'help_keys': [
                WINDOW_WIDTH / 2 - 390, WINDOW_HEIGHT / 2 - 170
            ],
            'help_keys_shadow': [
                WINDOW_WIDTH / 2 - 390 + 1, WINDOW_HEIGHT / 2 - 170 + 1
            ],
            'help_rules': [
                WINDOW_WIDTH / 2 + 390, WINDOW_HEIGHT / 2 - 170
            ],
            'help_rules_shadow': [
                WINDOW_WIDTH / 2 + 390 + 1, WINDOW_HEIGHT / 2 - 170 + 1
            ],
            'help_back': [
                WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 150
            ],
            'help_back_shadow': [
                WINDOW_WIDTH / 2 + 1, WINDOW_HEIGHT / 2 + 150 + 1
            ],
        }


    def _draw_header(self):
        self.start_elements = [
            canvas.create_polygon(
                self.start_elements_coords['start'], outline=options.define_color(0), fill='', width=3
            ),
            canvas.create_polygon(
                self.start_elements_coords['start_shadow'], outline=options.define_color(1), fill='', width=3
            ),
            canvas.create_text(
                self.start_elements_coords['start_header'],
                text=self.game_name, font=('Helvetica', 32), fill=options.define_color(0)
            ),
            canvas.create_text(
                self.start_elements_coords['start_header_shadow'],
                text=self.game_name, font=('Helvetica', 32), fill=options.define_color(1)
            ),
            canvas.create_text(
                self.start_elements_coords['start_info'],
                text=self.help_text_info, justify=CENTER, font=('Helvetica', 12), fill=options.define_color(0)
            ),
            canvas.create_text(
                self.start_elements_coords['start_info_shadow'],
                text=self.help_text_info, justify=CENTER, font=('Helvetica', 12), fill=options.define_color(1)
            ),
        ]

    # стартовый экран
    def start(self):
        canvas.delete('all')
        self._draw_header()
        while options.start == False:
            tk.update()
            time.sleep(0.05)
            if options.help:
                self.help()
                self._draw_header()

        canvas.delete('all')

    # экран раздела помощи
    def help(self):
        canvas.delete('all')

        self.start_elements = [
            canvas.create_polygon(
                self.start_elements_coords['help'], outline=options.define_color(0), fill='', width=3
            ),
            canvas.create_polygon(
                self.start_elements_coords['help_shadow'], outline=options.define_color(1), fill='', width=3
            ),
            canvas.create_text(
                self.start_elements_coords['help_keys'],
                text=self.help_text_keys, justify=LEFT, font=('Helvetica', 12), fill=options.define_color(0),
                anchor='nw'
            ),
            canvas.create_text(
                self.start_elements_coords['help_keys_shadow'],
                text=self.help_text_keys, justify=LEFT, font=('Helvetica', 12), fill=options.define_color(1),
                anchor='nw'
            ),
            canvas.create_text(
                self.start_elements_coords['help_rules'],
                text=self.help_text_rules, justify=RIGHT,
                font=('Helvetica', 12), fill=options.define_color(0),
                anchor='ne'
            ),
            canvas.create_text(
                self.start_elements_coords['help_rules_shadow'],
                text=self.help_text_rules, justify=RIGHT,
                font=('Helvetica', 12), fill=options.define_color(1),
                anchor='ne'
            ),
            canvas.create_text(
                self.start_elements_coords['help_back'],
                text='Автор:\n'+self.help_text_back, justify=CENTER,
                font=('Helvetica', 12), fill=options.define_color(0)
            ),
            canvas.create_text(
                self.start_elements_coords['help_back_shadow'],
                text='Автор:\n'+self.help_text_back, justify=CENTER,
                font=('Helvetica', 12), fill=options.define_color(1)
            ),
        ]

        while options.help:
            tk.update()
            time.sleep(0.05)

        canvas.delete('all')

    # экран game_over
    def game_over(self, who_won):
        canvas.delete('all')
        if who_won == 0:
            who_won_pos = 'справа'
        elif who_won == 1:
            who_won_pos = 'слева'
        else:
            who_won_pos = '¯\_(ツ)_/¯'

        self.start_elements = [
            canvas.create_polygon(
                self.start_elements_coords['start'], outline=options.define_color(who_won), fill='', width=3
            ),
            canvas.create_text(
                self.start_elements_coords['start_header'],
                text='Победил игрок '+who_won_pos, font=('Helvetica', 22), fill=options.define_color(who_won)
            ),
            canvas.create_text(
                self.start_elements_coords['start_info'],
                text='r - начать заново\nm - главное меню\nq - выход', justify=CENTER,
                font=('Helvetica', 12), fill=options.define_color(who_won),
            ),
        ]

        while 1:
            time.sleep(0.05)
            tk.update()
            if keyboard.r:
                canvas.delete('all')
                init_elements()
                start()
                break
            if keyboard.q:
                canvas.delete('all')
                break
            if keyboard.m:
                canvas.delete('all')
                self.start()
                init_elements()
                start()
                break


# создаем окно и настраиваем необходимые параметры для него
tk = Tk()
tk.geometry('%sx%s' % (WINDOW_WIDTH, WINDOW_HEIGHT))
tk.title('Space Invaders')
tk.resizable(0, 0)

# создаем слой, на нем будет происходить отрисовка объектовы
canvas = Canvas(tk, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg=BGCOLOR)

# создаем экземпляр класса Option, чтобы брать игровые переменные
# и экземпляр класса Keyboard, чтобы дальше привязать клавиатуру
options = Options()
keyboard = Keyboard()

canvas.bind("<KeyPress>", keyboard.keydown)
canvas.bind("<KeyRelease>", keyboard.keyup)
canvas.focus_set()
canvas.pack()

# показываем стартовый экран
screens = Screens()
screens.start()

# проводим необходимые настройки для начала игры
def init_elements():
    global player, enemies, lifes_bar, points_bar, options
    options = Options()
    player = []
    lifes_bar = []
    enemies = []
    player = [Player(0), Player(1)]
    lifes_bar = LifesBar()
    points_bar = PointsBar()
    for i in range(0, options.enemies_num):
        enemies.append(Enemy())

# здесь выполняется главный цикл игры
def start():
    while 1:
        keyboard.check() # проверяем нажатые клавиши
        for i in range(0, options.enemies_num): # обновляем противников
            enemies[i].update()

        # обновляем игроков
        player[0].update()
        player[1].update()

        # проверяем условие, при котором игрок побеждает
        if player[0].score >= options.points_to_win or player[1].hp <= 0:
            del player[:] # удаляем экземпляры класса Player
            screens.game_over(0) # показываем экран game_over, в функцию передаем номер победителя
            break

        if player[1].score >= options.points_to_win or player[0].hp <= 0:
            del player[:]
            screens.game_over(1)
            break

        time.sleep(frame_time) # ждем время кадра
        tk.update() # обновляем окно

init_elements()
frame_time = 1 / options.fps
start()
