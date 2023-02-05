import pyxel
import json

# Constantes del juego
VELX = 2
VELY = 2
COL_TOP = 1
COL_BOTTOM = 2
COL_LEFT = 3
COL_RIGHT = 4
COL_PADDLE = 5
LIVES = 3
SCREEN_W = 120
SCREEN_H = 160

# Aquí se almacena el mapa actual
cur_map = []
score = 0


class Ball():
    def __init__(self, paddle):
        self.paddle = paddle
        self.velx = -VELX
        self.vely = -VELY
        self.posx = (SCREEN_W / 2) - 2
        self.posy = self.paddle.posy - 4
        self.posxx = self.posx + 4
        self.posyy = self.posy + 4

    def draw(self):
        pyxel.blt(self.posx, self.posy, 0, 32, 8, 4, 4)

    def update(self):
        global score
        # Vamos a comprobar si choca contra el pad
        if (
            self.posyy >= self.paddle.posy and
            self.posy < self.paddle.posy + 4 and
            self.posxx >= self.paddle.posx and
            self.posx <= self.paddle.posx + 16
        ):
            if (
                self.posxx >= self.paddle.posx and
                self.posxx <= self.paddle.posx + 8
            ):
                self.velx = -VELX
            elif (
                self.posx >= self.paddle.posx + 8 and
                self.posx <= self.paddle.posx + 16
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
                    x = pyxel.floor(tile_x / 8)
                    y = pyxel.floor(tile_y / 8)
                    cur_map[y - 3][x - 1] = 0
                    score += 10

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

        tile = pyxel.tilemap(0).pget(tile_x, tile_y)
        if tile[0] == 0 and tile[1] == 0:
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
    def __init__(self):
        self.posx = (SCREEN_W / 2) - 8
        self.posy = SCREEN_H - 16

    def draw(self):
        pyxel.blt(self.posx, self.posy, 0, 40, 8, 16, 4)

    def update(self):
        if (
            (
                pyxel.btn(pyxel.KEY_LEFT) or
                pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT)
            ) and
            self.posx > 8
        ):
            self.posx -= 2
        elif (
            (
                pyxel.btn(pyxel.KEY_RIGHT) or
                pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)
            ) and
            self.posx + 16 < SCREEN_W - 8
        ):
            self.posx += 2

    def getPosition(self):
        return (self.posx, self.posy)

    def resetPos(self):
        self.posx = (SCREEN_W / 2) - 8


class App():
    def __init__(self):
        self.paddle = Paddle()
        self.ball = Ball(self.paddle)
        self.best_score = 0

        # 1: Pantalla de inicio. 2: Jugando. 3: Muerte
        self.game_state = 1
        self.move_ball = False
        self.level = 0

        self.maps = {}

        with open('maps.json') as maps:
            self.maps = json.load(maps)

        self.getScore()

        pyxel.init(SCREEN_W, SCREEN_H, title="Arkaway", display_scale=3)
        pyxel.load('assets.pyxres')
        pyxel.run(self.update, self.draw)

    def update(self):
        global LIVES

        # Primero comprobamos si la bola se sale por abajo
        ballPos = self.ball.getPosition()
        if ballPos[1] >= SCREEN_H:
            LIVES = LIVES - 1
            self.ball.resetBall()
            self.paddle.resetPos()
            self.move_ball = False

        if LIVES == 0:
            self.game_state = 3
            self.move_ball = True

        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
            if self.game_state == 1:
                self.setMap()
                self.game_state = 2
            elif self.game_state == 2 and not self.move_ball:
                self.move_ball = True
            elif self.game_state == 3:
                LIVES = 3
                self.game_state = 1
                self.move_ball = False

        if self.game_state == 1:
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

        if self.game_state == 3:
            self.saveScore()

    def draw(self):
        global score
        pyxel.cls(0)

        if self.game_state == 1:
            pyxel.text((SCREEN_W / 2) - 15, 32, 'ARKAWAY', 10)
            pyxel.text(8, 48, 'Press Space key or A button to start', 3)
            pyxel.text(2, 60, 'Left or Right to select level', 3)
            pyxel.text(8, 72, f'Level: {self.level + 1}', 3)
            pyxel.text(8, 80, f'Best Score: {self.best_score}', 3)
        elif self.game_state == 2:
            tile_y = 3
            tile_x = 1
            pyxel.bltm(0, 0, 0, 0, 0, 120, SCREEN_H)
            pyxel.text(2, 2, 'LIVES', 9)
            pyxel.text(2, 10, f'SCORE: {score}', 9)
            pyxel.text(SCREEN_W - 36, 2, f'LEVEL: 0{self.level + 1}', 9)
            lives_start = 32

            for i in range(LIVES):
                pyxel.blt(lives_start, 1, 0, 56, 8, 8, 8)
                lives_start += 8

            for y in range(len(cur_map)):
                for x in range(13):
                    sprite = cur_map[y][x]
                    pyxel.tilemap(0).pset(tile_x, tile_y, (sprite, 0))
                    tile_x += 1

                tile_x = 1
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


App()
