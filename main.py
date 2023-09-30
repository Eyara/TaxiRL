import random
import tkinter as tk
import tkinter.font as font

import numpy as np


class SquareButton(tk.Button):
    def __init__(self, master=None, **kwargs):
        side = kwargs.pop('side_length', None)
        tk.Button.__init__(self, master, compound='center', **kwargs)
        if side:
            self.config(width=side, height=side)


class TaxiGame:
    """
    0 - road
    1 - taxi
    2 - passenger, start point
    3 - passenger, finish point
    4 - wall/buildings
    5 - traffic light - green light
    6 - traffic light - red light
    """

    def __init__(self):
        self._w, self._h = 4, 4
        self._grid_field = [[0 for x in range(self._w)] for y in range(self._h)]
        self._grid_field[2][1] = 1
        self._grid_field[0][1] = 2

        self.generate_new_point(self.index_2d(1), 4, False)
        self.generate_new_point(self.index_2d(1), 5, False)

        self._root = None
        self._step_remaining = 2
        self._stop_threshold = 300
        self._was_success_step = False
        self._was_run_red_light = False
        self._score = 0
        self._action_list = [0, 1, 2, 3, 4]
        self._state_num = self._w * self._h

    def index_2d(self, v):
        for i, x in enumerate(self._grid_field):
            if v in x:
                return i, x.index(v)

    def update_taxi(self, old_pos, new_pos, is_gui=True):
        self._was_success_step = False
        self._was_run_red_light = False

        new_field_point = self._grid_field[new_pos[0]][new_pos[1]]

        if new_field_point == 2:
            self.generate_new_point(new_pos, 3, is_gui)
        elif new_field_point == 3:
            self.generate_new_point(new_pos, 2, is_gui)
        elif new_field_point == 5:
            self.generate_new_point(new_pos, 5, is_gui)
        elif new_field_point == 6:
            self._was_run_red_light = True
            self.generate_new_point(new_pos, 5, is_gui)

        self._grid_field[old_pos[0]][old_pos[1]] = 0
        self._grid_field[new_pos[0]][new_pos[1]] = 1

        if is_gui:
            self.set_button(old_pos[0], old_pos[1])
            self.set_button(new_pos[0], new_pos[1])

        self._step_remaining -= 1
        self.recalculate_score()

    def recalculate_score(self):
        if self._was_success_step:
            self._score += 25
        else:
            self._score -= 1

        if self._was_run_red_light:
            self._score -= 20

    def generate_new_point(self, new_pos, point_type, is_gui=True):
        # TODO use a better approach in future
        existing_values = [self.index_2d(1), self.index_2d(2), self.index_2d(3), self.index_2d(4), self.index_2d(5),
                           self.index_2d(6)]
        while True:
            point_new = (random.choice(list(range(0, self._h))), random.choice(list(range(0, self._w))))
            if point_new not in existing_values:
                break

        self._grid_field[point_new[0]][point_new[1]] = point_type

        if is_gui:
            self.set_button(point_new[0], point_new[1])

        if point_type == 2:
            self._was_success_step = True
            self._step_remaining = abs(new_pos[0] - point_new[0]) + abs(new_pos[1] - point_new[1]) + 1

    def toggle_traffic_light(self, is_gui=False):
        green_light = self.index_2d(5)
        result_light = self.index_2d(6) if green_light is None else green_light
        result_point = 5 if green_light is None else 6

        self._grid_field[result_light[0]][result_light[1]] = result_point

        if is_gui:
            self.set_button(result_light[0], result_light[1])

    def step(self, action):
        # WASD (not in the specified order)
        taxi_index_f, taxi_index_s = self.index_2d(1)
        new_taxi_index_f = taxi_index_f
        new_taxi_index_s = taxi_index_s
        # left
        if action == 0:
            if taxi_index_s - 1 >= 0:
                new_taxi_index_s = taxi_index_s - 1

        # right
        if action == 1:
            if taxi_index_s + 1 < self._w:
                new_taxi_index_s = taxi_index_s + 1

        # up
        if action == 2:
            if taxi_index_f - 1 >= 0:
                new_taxi_index_f = taxi_index_f - 1

        # down
        if action == 3:
            if taxi_index_f + 1 < self._h:
                new_taxi_index_f = taxi_index_f + 1

        if (new_taxi_index_f, new_taxi_index_s) == self.index_2d(4):
            new_taxi_index_f = taxi_index_f
            new_taxi_index_s = taxi_index_s

        self.update_taxi((taxi_index_f, taxi_index_s), (new_taxi_index_f, new_taxi_index_s), False)
        self.toggle_traffic_light()

        return np.array(self._grid_field).flatten(), self._score, True if self._was_success_step else False, \
            True if self._step_remaining < -1 * self._stop_threshold else False, None

    # Only for a manual testing
    def keydown(self, e):
        # WASD (not in the specified order) and space
        if e.keycode in (32, 65, 68, 83, 87):
            taxi_index_f, taxi_index_s = self.index_2d(1)
            new_taxi_index_f = taxi_index_f
            new_taxi_index_s = taxi_index_s
            # A key, movement to left
            if e.keycode == 65:
                if taxi_index_s - 1 >= 0:
                    new_taxi_index_s = taxi_index_s - 1
            # D key, movement to right
            if e.keycode == 68:
                if taxi_index_s + 1 < self._w:
                    new_taxi_index_s = taxi_index_s + 1
            # W key, movement to up
            if e.keycode == 87:
                if taxi_index_f - 1 >= 0:
                    new_taxi_index_f = taxi_index_f - 1
            # S key, movement to down
            if e.keycode == 83:
                if taxi_index_f + 1 < self._h:
                    new_taxi_index_f = taxi_index_f + 1

            if (new_taxi_index_f, new_taxi_index_s) == self.index_2d(4):
                new_taxi_index_f = taxi_index_f
                new_taxi_index_s = taxi_index_s

            self.toggle_traffic_light(True)
            self.update_taxi((taxi_index_f, taxi_index_s), (new_taxi_index_f, new_taxi_index_s), True)

    def set_back_color(self, button, r, c):
        if self._grid_field[r][c] == 1:
            button.configure(background="yellow")
        elif self._grid_field[r][c] == 4:
            button.configure(background="black")
        elif self._grid_field[r][c] == 5:
            button.configure(background="green")
        elif self._grid_field[r][c] == 6:
            button.configure(background="red")
        else:
            button.configure(background="white")

    def set_text(self, button, r, c):
        if self._grid_field[r][c] == 2:
            button.configure(text="P")
        elif self._grid_field[r][c] == 3:
            button.configure(text="F")
        else:
            button.configure(text="")

    def set_button(self, r, c):
        btn = SquareButton(side_length=200, font=font.Font(size=30))
        self.set_back_color(btn, r, c)
        self.set_text(btn, r, c)
        btn.grid(row=r, column=c)

    def create_env(self):
        self._root = tk.Tk()
        self._root.title("Taxi game")
        self._root.geometry("800x800")
        self.draw_field()

    def set_grid_field(self, grid):
        self._grid_field = grid

    def create_replay_env(self):
        self._root = tk.Tk()
        self._root.title("Taxi game's replay")
        self._root.geometry("800x800")

    def get_root(self):
        return self._root

    def run_mainloop(self):
        self._root.mainloop()

    def reset(self):
        # self.create_env()
        self._score = 0

        old_pas_idx = self.index_2d(2)
        old_fin_idx = self.index_2d(3)

        if old_pas_idx is not None:
            self._grid_field[old_pas_idx[0]][old_pas_idx[1]] = 0

        if old_fin_idx is not None:
            self._grid_field[old_fin_idx[0]][old_fin_idx[1]] = 0

        self.generate_new_point(self.index_2d(1), 2, False)

        pas_idx = self.index_2d(2)
        taxi_idx = self.index_2d(1)
        self._step_remaining = abs(pas_idx[0] - taxi_idx[0]) + abs(pas_idx[1] - taxi_idx[1]) + 1
        return np.array(self._grid_field).flatten(), None

    def get_action_num(self):
        return len(self._action_list)

    def get_action_sample(self):
        return random.choice(self._action_list)

    def draw_field(self, is_replay_mode=False):
        for c in range(self._h):
            self._root.columnconfigure(index=c, weight=1)
        for r in range(self._w):
            self._root.rowconfigure(index=r, weight=1)

        for r in range(self._h):
            for c in range(self._w):
                self.set_button(r, c)

        if is_replay_mode is False:
            self._root.bind("<KeyPress>", self.keydown)
            self._root.mainloop()


if __name__ == '__main__':
    tg = TaxiGame()
    tg.create_env()
