import pyxel
import json
from os import path
from random import randint

# Constantes del juego
VELX = 2
VELY = 2
COL_TOP = 1
COL_BOTTOM = 2
COL_LEFT = 3
COL_RIGHT = 4
COL_PADDLE = 5
SCREEN_W = 120
SCREEN_H = 160

# Aquí se almacena el mapa actual
cur_map = []
score = 0
game_mode = 1
lives = 3


def centerText(text, posy, color):
    '''Centra un texto en pantalla'''
    pyxel.text(
        (SCREEN_W / 2) - ((len(text) * 4) / 2),
        posy, text, color
    )


class Ball():
    def __init__(self, paddle, game_mode):
        self.paddle = paddle
        self.velx = -VELX
        self.vely = -VELY
        self.posx = (SCREEN_W / 2) - 2
        self.posy = self.paddle.posy - 4
        self.posxx = self.posx + 4
        self.posyy = self.posy + 4
        self.game_mode = game_mode

    def draw(self):
        pyxel.blt(self.posx, self.posy, 0, 40, 8, 4, 4, 0)

    def update(self):
        global score
        # Vamos a comprobar si choca contra el pad
        if (
            self.posyy >= self.paddle.posy and
            self.posy < self.paddle.posy + 4 and
            self.posxx >= self.paddle.posx and
            self.posx <= self.paddle.posx + (self.paddle.size * 8)
        ):
            pyxel.play(0, 0)

            if (
                self.posxx >= self.paddle.posx and
                self.posxx <= self.paddle.posx + 8
            ):
                self.velx = -VELX
            elif (
                self.posx >= self.paddle.posx + 8 and
                self.posx <= self.paddle.posx + (self.paddle.size * 8)
            ):
                self.velx = VELX

            if (
                self.posxx <= self.paddle.posx + 4 or
                self.posx >= self.paddle.posx + 12
            ):
                self.vely = -1
            else:
                self.vely = -VELY

        # Comprobamos si esta llegando a algún sprite
        cols, tiles = self._checkColDir()
        if len(cols) > 0:
            for col in cols:
                if col == COL_TOP:
                    if self.vely == 1:
                        self.vely = -1
                    else:
                        self.vely = -VELY
                if col == COL_BOTTOM:
                    if self.vely == -1:
                        self.vely = 1
                    else:
                        self.vely = VELY
                if col == COL_LEFT:
                    self.velx = -VELX
                if col == COL_RIGHT:
                    self.velx = VELX

            for tile in tiles:
                tile_x, tile_y = tile

                _tile = self._checkTile(tile_x, tile_y)
                if _tile and _tile[0] >= 1 and _tile[0] < 12 and _tile[1] == 0:
                    pyxel.play(0, 1)
                    x = pyxel.floor(tile_x / 8)

                    if self.game_mode == 2:
                        x -= 2

                    y = pyxel.floor(tile_y / 8)
                    cur_map[y - 3][x - 1] = 0
                    score += 10
                else:
                    pyxel.play(0, 0)

        self.posx += self.velx
        self.posxx += self.velx
        self.posy += self.vely
        self.posyy += self.vely

    def getPosition(self):
        return (self.posx, self.posy, self.posxx, self.posyy)

    def setPosition(self, x, y):
        self.posx = x
        self.posxx = x + 4
        self.posy = y
        self.posyy = y + 4

    def resetBall(self):
        self.velx = 0 - VELX
        self.vely = 0 - VELY
        self.posx = (SCREEN_W / 2) - 2
        self.posy = self.paddle.posy - 4
        self.posxx = self.posx + 4
        self.posyy = self.posy + 4

    def _checkTile(self, posx, posy):
        tile_x = pyxel.floor(posx / 8)
        tile_y = pyxel.floor(posy / 8)
        cur_tilemap = 0

        if self.game_mode == 2:
            cur_tilemap = 2

        tile = pyxel.tilemap(cur_tilemap).pget(tile_x, tile_y)

        if (
            (tile[0] == 0 and tile[1] == 0) or
            (tile[0] == 7 and tile[1] == 1) or
            (tile[0] == 8 and tile[1] == 1)
        ):
            return

        return tile

    def _checkColDir(self):
        cols = []
        tiles = []
        if pyxel.sgn(self.vely) == 1:
            tile = self._checkTile(self.posx, self.posyy + VELY)
            if tile:
                tiles.append([self.posx, self.posyy + VELY])
                cols.append(COL_TOP)

        if pyxel.sgn(self.vely) == -1:
            tile = self._checkTile(self.posx, self.posy - VELY)
            if tile:
                tiles.append([self.posx, self.posy - VELY])
                cols.append(COL_BOTTOM)

        if pyxel.sgn(self.velx) == 1:
            tile = self._checkTile(self.posxx, self.posy)
            if tile:
                tiles.append([self.posxx, self.posy])
                cols.append(COL_LEFT)

        if pyxel.sgn(self.velx) == -1:
            tile = self._checkTile(self.posx - VELX, self.posy)
            if tile:
                tiles.append([self.posx - VELX, self.posy])
                cols.append(COL_RIGHT)

        return (cols, tiles)


class Paddle():
    def __init__(self, game_mode):
        self.posx = (SCREEN_W / 2) - 8
        self.posy = SCREEN_H - 16
        self.size = 2  # 1: Small, 2: normal, 3: big
        self.vel = VELX
        self.game_mode = game_mode

    def draw(self):
        pyxel.blt(
            self.posx, self.posy, 0, 32,
            8 + ((self.size - 1) * 4),
            8 * self.size,  4, 0
        )

    def update(self):
        if (
            (
                pyxel.btn(pyxel.KEY_LEFT) or
                pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT)
            ) and
            not self._compCollideWall(self.posx - VELX)
        ):
            self.posx -= VELX
        elif (
            (
                pyxel.btn(pyxel.KEY_RIGHT) or
                pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)
            ) and
            not self._compCollideWall(self.posx + 16)
        ):
            self.posx += VELX

    def getPosition(self):
        return (self.posx, self.posy)

    def resetPos(self):
        self.posx = (SCREEN_W / 2) - 8

    def _compCollideWall(self, posx):
        tile_x = pyxel.floor(posx / 8)
        tile_y = pyxel.floor(self.posy / 8)

        cur_tilemap = 0

        if self.game_mode == 2:
            cur_tilemap = 2

        tile = pyxel.tilemap(cur_tilemap).pget(tile_x, tile_y)
        if tile[0] == 3 and tile[1] == 1:
            return True

        return False


class App():
    def __init__(self):
        self.paddle = None
        self.ball = None
        self.best_score = 0

        # 1: Pantalla de inicio. 2: Jugando. 3: Muerte
        self.game_state = 1

        # 1: Normal. 2: Infinite
        self.game_mode = 1
        self.move_ball = False
        self.level = 0

        self.maps = {}

        self.start_frame = 0
        self.newLineAt = 300  # Every 30 frames (10 seconds, 1 sec = 30 frames)
        self.sel_cur_pos = 62
        self.line_len = 13

        __dir = path.realpath(path.dirname(__file__))
        with open(__dir + '/maps.json') as maps:
            self.maps = json.load(maps)

        self.getScore()

        pyxel.init(SCREEN_W, SCREEN_H, title="Arkaway", display_scale=3,
                   capture_scale=3, capture_sec=20)
        pyxel.load('assets.pyxres')
        pyxel.run(self.update, self.draw)

    def update(self):
        global lives, score, cur_map

        # Primero comprobamos si la bola se sale por abajo
        if self.move_ball:
            ballPos = self.ball.getPosition()
            if ballPos[1] >= SCREEN_H:
                lives = lives - 1
                self.ball.resetBall()
                self.paddle.resetPos()
                self.move_ball = False

        if lives == 0:
            self.game_state = 3
            self.move_ball = False

        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
            if self.game_state == 1:
                self.paddle = Paddle(self.game_mode)
                self.ball = Ball(self.paddle, self.game_mode)
                self.paddle.vel = VELX
                self.start_frame = pyxel.frame_count
                if self.game_mode == 1:
                    self.setMap()
                    self.line_len = 13
                else:
                    self.paddle.vel = 3
                    self.newLineAt = 300
                    self.genRandLine()
                    self.line_len = 9

                self.game_state = 2
            elif self.game_state == 2 and not self.move_ball:
                self.move_ball = True
            elif self.game_state == 3:
                lives = 3
                self.game_state = 1
                self.move_ball = False
                cur_map = []

        if self.game_state == 1:

            if (
                pyxel.btnp(pyxel.KEY_UP) or
                pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_UP)
            ):
                if self.game_mode == 1:
                    self.game_mode = 2
                else:
                    self.game_mode = 1

            if (
                pyxel.btnp(pyxel.KEY_DOWN) or
                pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN)
            ):
                if self.game_mode == 2:
                    self.game_mode = 1
                else:
                    self.game_mode = 2

            self.sel_cur_pos = 57 + (self.game_mode * 8)

            if (
                pyxel.btnp(pyxel.KEY_LEFT) or
                pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT)
            ):
                if self.level > 0:
                    self.level -= 1
                else:
                    self.level = len(self.maps) - 1

            if (
                pyxel.btnp(pyxel.KEY_RIGHT) or
                pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)
            ):
                if self.level < len(self.maps) - 1:
                    self.level += 1
                else:
                    self.level = 0

        if self.game_state == 2:
            self.paddle.update()
            if self.move_ball:
                self.ball.update()
            else:
                padPos = self.paddle.getPosition()
                self.ball.setPosition(padPos[0] + 6, padPos[1] - 4)

            level_complete = self.levelComplete()
            if level_complete and self.game_mode == 1:
                if self.level < len(self.maps) - 1:
                    self.ball.resetBall()
                    self.paddle.resetPos()
                    self.level += 1
                    self.setMap()
                    self.move_ball = False
                else:
                    self.game_state = 3

            if self.game_mode == 2 and self.move_ball:
                if (pyxel.frame_count - self.start_frame) % self.newLineAt == 0:
                    self.genRandLine()

                if score > 0 and score % 500 == 0 and self.newLineAt > 60:
                    self.newLineAt -= 15

        if self.game_state == 3:
            self.saveScore()

    def draw(self):
        global lives, score
        pyxel.cls(0)

        cur_tilemap = 0

        if self.game_state == 1:
            pyxel.bltm(0, 0, 1, 0, 0, SCREEN_W, SCREEN_H)
            pyxel.blt(40, self.sel_cur_pos, 0, 40, 8, 4, 4, 0)
            pyxel.text(48, 64, 'Normal', 9)
            pyxel.text(48, 72, 'Endless', 9)
            centerText('2023 Son Link', SCREEN_H - 24, 7)
            centerText('Make with   and Pyxel', SCREEN_H - 16, 7)
            pyxel.blt((SCREEN_W / 2) - 2, SCREEN_H - 16, 0, 49, 9, 5, 5, 0)

        elif self.game_state == 2:
            tile_y = 3
            tile_x = 1

            if self.game_mode == 1:
                pyxel.bltm(0, 0, 0, 0, 0, SCREEN_W, SCREEN_H)

            elif self.game_mode == 2:
                pyxel.bltm(0, 0, 2, 0, 0, SCREEN_W, SCREEN_H)
                cur_tilemap = 2
                tile_x = 3

            pyxel.text(2, 2, 'SCORE', 9)
            pyxel.text(2, 9, str(score), 10)

            pyxel.text(36, 2, 'lives', 9)
            lives_start = 36

            if lives < 5:
                for i in range(lives):
                    pyxel.blt(lives_start, 9, 0, 49, 9, 5, 5, 0)
                    lives_start += 8
            else:
                pyxel.blt(lives_start, 9, 0, 49, 9, 5, 5, 0)
                pyxel.text(lives_start + 6, 9, f'x{lives}', 10)

            pyxel.text(68, 2, 'BEST', 9)
            if score > self.best_score:
                self.best_score = score

            pyxel.text(68, 9, str(self.best_score), 10)

            if self.game_mode == 1:
                pyxel.text(98, 2, 'LEVEL', 9)
                pyxel.text(98, 9, str(self.level + 1), 10)

            for y in range(len(cur_map)):
                for x in range(self.line_len):
                    sprite = cur_map[y][x]
                    if sprite == 0:
                        pyxel.tilemap(cur_tilemap).pset(tile_x, tile_y, (7, 1))
                    else:
                        pyxel.tilemap(cur_tilemap).pset(tile_x, tile_y, (sprite, 0))
                    tile_x += 1

                tile_x = 1
                if self.game_mode == 2:
                    tile_x = 3

                tile_y += 1

            self.ball.draw()
            self.paddle.draw()
        elif self.game_state == 3:
            pyxel.text((SCREEN_W / 2) - 18, 32, 'GAME OVER', 8)

    def setMap(self):
        global cur_map
        cur_map = self.maps[self.level]

    def saveScore(self):
        global score
        with open('score.txt', 'w') as save:
            save.write(str(score))
            save.close()

    def getScore(self):
        try:
            with open('score.txt', 'r') as f:
                self.best_score = int(f.readline())
        except FileNotFoundError:
            self.best_score = 0

    def levelComplete(self):
        global cur_map

        no_empty_tiles = 0

        for y in range(len(cur_map)):
            for x in range(self.line_len):
                sprite = cur_map[y][x]
                if sprite > 0 and sprite < 12:
                    no_empty_tiles += 1

        if no_empty_tiles > 0:
            return False
        return True

    def genRandLine(self):
        global cur_map
        line = []

        for x in range(9):
            line.append(randint(1, 11))

        cur_map.insert(0, line)


App()
