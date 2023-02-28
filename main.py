import pyxel
import json
import copy

from arkaway import globals
from arkaway.ball import Ball
from arkaway.paddle import Paddle
from os import path
from random import randint


def centerText(text, posy, color):
    '''Centra un texto en pantalla'''
    pyxel.text(
        (globals.SCREEN_W / 2) - ((len(text) * 4) / 2),
        posy, text, color
    )


class App():
    def __init__(self):
        self.paddle = None
        self.ball = None
        self.best_score = 0
        self.new_best_score = False

        # 1: Main Screen. 2: Playing. 3: Game Over. 4: Win screen
        self.game_state = 1

        # 1: Normal. 2: Endless
        self.game_mode = 1
        self.prev_game_mode = 1
        self.move_ball = False
        self.paused = False
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

        pyxel.init(globals.SCREEN_W, globals.SCREEN_H, title="Arkaway",
                   display_scale=3, capture_scale=3, capture_sec=20,
                   quit_key=pyxel.KEY_Q)
        pyxel.load('assets.pyxres')
        pyxel.run(self.update, self.draw)

    def update(self):

        # Primero comprobamos si la bola se sale por abajo
        if self.move_ball and not self.paused:
            ballPos = self.ball.getPosition()
            if ballPos[1] >= globals.SCREEN_H:
                globals.lives -= 1
                self.ball.resetBall()
                self.paddle.resetPos()
                self.move_ball = False

        if globals.lives == 0:
            self.game_state = 3
            self.move_ball = False

        if (
            pyxel.btnp(pyxel.KEY_SPACE) or
            (pyxel.btnp(pyxel.KEY_RETURN) and self.game_state != 2) or
            pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)
        ):
            if self.game_state == 1:
                self.start_frame = pyxel.frame_count
                self.reset()

                if self.game_mode == 1:
                    self.level = 0
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
            elif self.game_state == 3 or self.game_state == 4:
                self.ball = None
                self.paddle = None
                globals.lives = 3
                self.move_ball = False
                self.game_state = 1

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

        if self.game_state == 2:
            if (
                pyxel.btnp(pyxel.KEY_RETURN) or
                pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START)
            ):
                if self.paused:
                    self.paused = False
                else:
                    self.paused = True

            if self.paused and (
                (
                    pyxel.btn(pyxel.KEY_ESCAPE) or
                    pyxel.btn(pyxel.GAMEPAD1_BUTTON_BACK)
                )
            ):
                self.level = 0
                self.reset()
                self.game_mode = 1
                self.game_state = 1
                self.paused = False

            if not self.paused:
                self.paddle.update()

            if self.move_ball:
                if not self.paused:
                    self.ball.update()
            else:
                padPos = self.paddle.getPosition()
                self.ball.setPosition(padPos[0] + 6, padPos[1] - 4)

            level_complete = self.levelComplete()
            if level_complete and self.game_mode == 1 and self.game_state == 2:
                if self.level < len(self.maps) - 1:
                    self.level += 1
                    self.setMap()
                else:
                    self.game_state = 4

            if self.game_mode == 2 and self.move_ball and not self.paused:
                if (
                    (pyxel.frame_count - self.start_frame) %
                    self.newLineAt == 0
                ):
                    self.genRandLine()

                if (
                    globals.score > 0 and
                    globals.score % 500 == 0 and
                    self.newLineAt > 60
                ):
                    self.newLineAt -= 15

        _best_score = 'normal'
        if self.game_mode == 2:
            _best_score = 'endless'

        if self.game_state == 3 or self.game_state == 4:
            self.prev_game_mode = self.game_mode
            if globals.score > self.best_score[_best_score]:
                self.best_score[_best_score] = globals.score
                self.new_best_score = True
                self.saveScore()

    def draw(self):
        pyxel.cls(0)

        cur_tilemap = 0
        _best_score = 'normal'
        if self.game_mode == 2:
            _best_score = 'endless'

        if self.game_state == 1:
            pyxel.bltm(0, 0, 1, 0, 0, globals.SCREEN_W, globals.SCREEN_H)
            pyxel.blt(40, self.sel_cur_pos, 0, 40, 8, 4, 4, 0)
            pyxel.text(48, 64, 'Normal', 9)
            pyxel.text(48, 72, 'Endless', 9)
            centerText('2023 Son Link', globals.SCREEN_H - 24, 7)
            centerText('Make with   and Pyxel', globals.SCREEN_H - 16, 7)
            pyxel.blt((globals.SCREEN_W / 2) - 2, globals.SCREEN_H - 16,
                      0, 49, 9, 5, 5, 0)

        elif self.game_state == 2:
            tile_y = 3
            tile_x = 1

            if self.game_mode == 1:
                pyxel.bltm(0, 0, 0, 0, 0, globals.SCREEN_W, globals.SCREEN_H)

            elif self.game_mode == 2:
                pyxel.bltm(0, 0, 2, 0, 0, globals.SCREEN_W, globals.SCREEN_H)
                cur_tilemap = 2
                tile_x = 3

            pyxel.text(2, 2, 'SCORE', 9)
            pyxel.text(2, 9, str(globals.score), 10)

            pyxel.text(36, 2, 'lives', 9)
            lives_start = 36

            if globals.lives < 5:
                for i in range(globals.lives):
                    pyxel.blt(lives_start, 9, 0, 49, 9, 5, 5, 0)
                    lives_start += 8
            else:
                pyxel.blt(lives_start, 9, 0, 49, 9, 5, 5, 0)
                pyxel.text(lives_start + 6, 9, f'x{globals.lives}', 10)

            pyxel.text(68, 2, 'BEST', 9)

            if globals.score > self.best_score[_best_score]:
                pyxel.text(68, 9, str(globals.score), 10)
            else:
                pyxel.text(68, 9, str(self.best_score[_best_score]), 10)

            if self.game_mode == 1:
                pyxel.text(98, 2, 'LEVEL', 9)
                pyxel.text(98, 9, str(self.level + 1), 10)

            for y in range(len(globals.cur_map)):
                for x in range(self.line_len):
                    sprite = globals.cur_map[y][x]
                    if sprite == 0:
                        pyxel.tilemap(cur_tilemap).pset(tile_x, tile_y, (7, 1))
                    else:
                        pyxel.tilemap(cur_tilemap).pset(tile_x, tile_y,
                                                        (sprite, 0))
                    tile_x += 1

                tile_x = 1
                if self.game_mode == 2:
                    tile_x = 3

                tile_y += 1

            self.ball.draw()
            self.paddle.draw()

            if self.paused:
                pyxel.rect((globals.SCREEN_W/2) - 20, 56, 40, 16, 0)
                centerText('PAUSE', 62, 9)

        elif self.game_state == 3:
            pyxel.bltm(0, 0, 1, 0, 0, globals.SCREEN_W, 32)
            centerText('GAME OVER', 40, 8)
            centerText(f'SCORE: {globals.score}', 52, 9)

            if self.new_best_score:
                centerText('NEW RECORD', 64, 11)

        elif self.game_state == 4:
            pyxel.bltm(0, 0, 1, 0, 0, globals.SCREEN_W, 32)
            centerText('WIN!', 40, 11)
            centerText(f'SCORE: {globals.score}', 52, 9)
            if self.new_best_score:
                centerText('NEW RECORD', 64, 11)

    def setMap(self):
        globals.cur_map = copy.deepcopy(self.maps[self.level])
        self.ball.cur_map = globals.cur_map

    def saveScore(self):
        with open('scores.json', 'w') as save:
            json.dump(self.best_score, save, sort_keys=True, indent=4)
            save.close()

    def getScore(self):
        try:
            with open('scores.json', 'r') as f:
                self.best_score = json.load(f)
        except FileNotFoundError:
            self.best_score = {
                "endless": 0,
                "normal": 0
            }

            self.saveScore()

    def levelComplete(self):
        no_empty_tiles = 0

        for y in range(len(globals.cur_map)):
            for x in range(self.line_len):
                sprite = globals.cur_map[y][x]
                if sprite > 0 and sprite < 12:
                    no_empty_tiles += 1

        if no_empty_tiles > 0:
            return False
        return True

    def genRandLine(self):
        line = []

        for x in range(9):
            line.append(randint(1, 11))

        globals.cur_map.insert(0, line)

    def reset(self):
        tile_y = 3

        for y in range(len(globals.cur_map)):
            tile_x = 1
            if self.prev_game_mode == 2:
                tile_x = 3

            for x in range(self.line_len):
                if self.prev_game_mode == 1:
                    pyxel.tilemap(0).pset(x + tile_x, tile_y, (7, 1))
                else:
                    pyxel.tilemap(2).pset(x + tile_x, tile_y, (7, 1))

            tile_y += 1

        globals.cur_map = []

        self.paddle = Paddle(self.game_mode)
        self.ball = Ball(self.paddle, self.game_mode)
        self.paddle.vel = globals.VELX
        self.ball.resetBall()
        self.paddle.resetPos()
        self.move_ball = False
        self.new_best_score = False
        globals.score = 0
        self.getScore()


App()
