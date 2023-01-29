import pyxel
from random import randint

example = []

# Genera una pantalla de prueba de manera aleatoria.
for y in range(6):
    line = []
    for x in range(13):
        line.append(randint(1, 11))

    example.append(line)

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
SCREEN_H = 144

class Ball():
    def __init__(self, paddle):
        self.velx = 0 - VELX
        self.vely = 0 - VELY
        self.posx = (SCREEN_W / 2) - 2
        self.posy = 124
        self.posxx = self.posx + 4
        self.posyy = self.posy + 4

        self.paddle = paddle

    def draw(self):
        pyxel.blt(self.posx, self.posy, 0, 32, 8, 4, 4)

    def update(self):
        # Vamos a comprobar si choca contra el padd
        if (
            self.posyy + VELY >= 128 and
            self.posx >= self.paddle.posx and
            self.posxx <= self.paddle.posx + 16
        ):
            self.vely = 0 - VELY

        # Comprobamos si esta llegando a algun sprite
        cols, tiles = self._checkColDir()
        if len(cols) > 0:
            for col in cols:
                if col == COL_TOP:
                    self.vely = 0 - VELY
                if col == COL_BOTTOM:
                    self.vely = VELY
                if col == COL_LEFT:
                    self.velx = 0 - VELX
                if col == COL_RIGHT:
                    self.velx = VELX

            for tile in tiles:
                tile_x, tile_y = tile
                _tile = self._checkTile(tile_x, tile_y)
                if _tile and _tile[0] >= 1 and _tile[1] == 0:
                    x = pyxel.floor(tile_x / 8)
                    y = pyxel.floor(tile_y / 8)
                    example[y - 3][x - 1] = 0

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
        self.posy = 124
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
        self.posy = 128

    def draw(self):
        pyxel.blt(self.posx, self.posy, 0, 40, 8, 16, 4)

    def update(self):
        if pyxel.btn(pyxel.KEY_LEFT) and self.posx > 8:
            self.posx -= 2
        elif pyxel.btn(pyxel.KEY_RIGHT) and self.posx < 96:
            self.posx += 2

    def getPosition(self):
        return (self.posx, self.posy)
    
    def resetPos(self):
        self.posx = (SCREEN_W / 2) - 8
        self.posy = 128

class App():
    def __init__(self):
        self.paddle = Paddle()
        self.ball = Ball(self.paddle)
        
        # 1: Pantalla de inicio. 2: Jugando. 3: Muerte
        self.game_state = 1
        self.move_ball = False

        pyxel.init(120, 144, title="Arkaway", display_scale=3)
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

        if pyxel.btnp(pyxel.KEY_SPACE):
            if self.game_state == 1:
                self.game_state = 2
            elif self.game_state == 2 and not self.move_ball:
                self.move_ball = True
            elif self.game_state == 3:
                LIVES = 3
                self.game_state = 1
                self.move_ball = False
        
        if self.game_state == 2:
            self.paddle.update()
            if self.move_ball:
                self.ball.update()
            else:
                padPos = self.paddle.getPosition()
                self.ball.setPosition(padPos[0] + 6, padPos[1] - 4)

    def draw(self):
        tile_y = 3
        tile_x = 1
        pyxel.cls(0)

        if self.game_state == 1:
            pyxel.text((SCREEN_W / 2) - 15, 32, 'ARKAWAY', 10)
            pyxel.text((SCREEN_W / 2) - 40, 48, 'Press Space to start', 3)
        elif self.game_state == 2:
            pyxel.bltm(0, 0, 0, 0, 0, 120, 144)
            pyxel.text(4, 4, 'LIVES: {}'.format(LIVES), 9)
            lives_start = 32
            
            for i in range(LIVES):
                pyxel.blt(lives_start, 3, 0, 56, 8, 8, 8)
                lives_start += 8
            
            for y in range(len(example)):
                for x in range(13):
                    sprite = example[y][x]
                    pyxel.tilemap(0).pset(tile_x, tile_y, (sprite, 0))
                    tile_x += 1

                tile_x = 1
                tile_y += 1

            self.ball.draw()
            self.paddle.draw()
        elif self.game_state == 3:
            pyxel.text((SCREEN_W / 2) - 18, 32, 'GAME OVER', 8)


App()
