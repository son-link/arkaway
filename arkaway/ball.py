import pyxel
from . import globals


class Ball():
    def __init__(self, paddle, game_mode):
        self.paddle = paddle
        self.velx = -globals.VELX
        self.vely = -globals.VELY
        self.posx = (globals.SCREEN_W / 2) - 2
        self.posy = self.paddle.posy - 4
        self.posxx = self.posx + 4
        self.posyy = self.posy + 4
        self.game_mode = game_mode

    def draw(self):
        pyxel.blt(self.posx, self.posy, 0, 40, 8, 4, 4, 0)

    def update(self):
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
                self.velx = -globals.VELX
            elif (
                self.posx >= self.paddle.posx + 8 and
                self.posx <= self.paddle.posx + (self.paddle.size * 8)
            ):
                self.velx = globals.VELX

            if (
                self.posxx <= self.paddle.posx + 4 or
                self.posx >= self.paddle.posx + 12
            ):
                self.vely = -1
            else:
                self.vely = -globals.VELY

        # Comprobamos si esta llegando a algún sprite
        cols, tiles = self._checkColDir()
        if len(cols) > 0:
            for col in cols:
                if col == globals.COL_TOP:
                    if self.vely == 1:
                        self.vely = -1
                    else:
                        self.vely = -globals.VELY
                if col == globals.COL_BOTTOM:
                    if self.vely == -1:
                        self.vely = 1
                    else:
                        self.vely = globals.VELY
                if col == globals.COL_LEFT:
                    self.velx = -globals.VELX
                if col == globals.COL_RIGHT:
                    self.velx = globals.VELX

            for tile in tiles:
                tile_x, tile_y = tile

                _tile = self._checkTile(tile_x, tile_y)
                if _tile and _tile[0] >= 1 and _tile[0] < 12 and _tile[1] == 0:
                    pyxel.play(0, 1)
                    x = pyxel.floor(tile_x / 8)

                    if self.game_mode == 2:
                        x -= 2

                    y = pyxel.floor(tile_y / 8)
                    globals.cur_map[y - 3][x - 1] = 0
                    globals.score += 10
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
        self.velx = 0 - globals.VELX
        self.vely = 0 - globals.VELY
        self.posx = (globals.SCREEN_W / 2) - 2
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
            tile = self._checkTile(self.posx, self.posyy + globals.VELY)
            if tile:
                tiles.append([self.posx, self.posyy + globals.VELY])
                cols.append(globals.COL_TOP)

        if pyxel.sgn(self.vely) == -1:
            tile = self._checkTile(self.posx, self.posy - globals.VELY)
            if tile:
                tiles.append([self.posx, self.posy - globals.VELY])
                cols.append(globals.COL_BOTTOM)

        if pyxel.sgn(self.velx) == 1:
            tile = self._checkTile(self.posxx, self.posy)
            if tile:
                tiles.append([self.posxx, self.posy])
                cols.append(globals.COL_LEFT)

        if pyxel.sgn(self.velx) == -1:
            tile = self._checkTile(self.posx - globals.VELX, self.posy)
            if tile:
                tiles.append([self.posx - globals.VELX, self.posy])
                cols.append(globals.COL_RIGHT)

        return (cols, tiles)
