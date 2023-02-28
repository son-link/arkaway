import pyxel
from . import globals


class Paddle():
    def __init__(self, game_mode):
        self.posx = (globals.SCREEN_W / 2) - 8
        self.posy = globals.SCREEN_H - 16
        self.size = 2  # 1: Small, 2: normal, 3: big
        self.vel = globals.VELX
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
            not self._compCollideWall(self.posx - globals.VELX)
        ):
            self.posx -= globals.VELX
        elif (
            (
                pyxel.btn(pyxel.KEY_RIGHT) or
                pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)
            ) and
            not self._compCollideWall(self.posx + 16)
        ):
            self.posx += globals.VELX

    def getPosition(self):
        return (self.posx, self.posy)

    def resetPos(self):
        self.posx = (globals.SCREEN_W / 2) - 8

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
