import math

import pygame

from mlgame.game.paia_game import PaiaGame
from mlgame.utils.enum import get_ai_name
from mlgame.view.audio_model import MusicProgressSchema, create_sound_init_data, create_music_init_data
from mlgame.view.decorator import check_game_progress, check_game_result, check_scene_init_data
from mlgame.view.view_model import create_text_view_data, create_asset_init_data, create_image_view_data, \
    create_line_view_data, Scene, create_polygon_view_data, create_rect_view_data, create_scene_progress_data
from .env import *
from .env import HELP_TXT_STYLE, HELP_TXT_COLOR
from .mazeMode import MazeMode


class Dont_touch(PaiaGame):
    def __init__(self, user_num, map_num, time_to_play, dark_mode='dark', map_file=None, *args, **kwargs):
        super().__init__(user_num=user_num)
        # self.game_type = game_type
        sensor_num = 6
        self.user_num = user_num
        if dark_mode == 'dark':
            self.dark_mode = True
        elif dark_mode == 'light':
            self.dark_mode = False
        else:
            self.dark_mode = True
        self.is_single = False
        if self.user_num == 1:
            self.is_single = True
        # self.maze_id = map - 1
        if map_file is None:
            map_file = path.join(MAP_DIR, f"level_{map_num}.tmj")
        self.map_file = map_file
        self.game_end_time = time_to_play
        self.sensor_num = sensor_num
        self.set_game_mode()
        self.is_running = self.isRunning()
        self.map_width = self.game_mode.map.width
        self.map_height = self.game_mode.map.height
        self.scene = Scene(WIDTH, HEIGHT, "#08142b", 0, 0)
        self.origin_car_pos = [0, 0]

    # self.origin_car_pos = self.game_mode.car_info[0]["center"]

    def update(self, cmd_dict):
        self.frame_count += 1
        self.game_mode.handle_event()
        self.game_mode.update_sprite(cmd_dict)
        if not self.isRunning():
            self.is_running = False
            return "RESET"
        for car in self.game_mode.cars:
            if self.origin_car_pos != [0, 0]:
                break
            self.origin_car_pos = car.get_info()["center"]

    def get_data_from_game_to_player(self):
        scene_info = self.get_scene_info
        player_info = {}
        # pygame -> box2D
        end_p = self.game_mode.pygame_to_box2d(self.game_mode.end_point.get_info()["coordinate"], self.map_height / PPM)
        check_points_coodinate = []
        for cp in self.game_mode.check_points:
            check_points_coodinate.append(
                self.game_mode.pygame_to_box2d(cp.get_info()["coordinate"], self.map_height / PPM))
        for car in self.game_mode.car_info:
            # type of car is dictionary
            player_info[get_ai_name(int(car["id"]))] = {
                "frame": scene_info["frame"],
                "status": car["status"],
                "x": car["coordinate"][0],
                "y": car["coordinate"][1],
                "angle": (car["angle"] * 180 / math.pi) % 360,
                "R_sensor": car["r_sensor_value"]["distance"],
                "L_sensor": car["l_sensor_value"]["distance"],
                "F_sensor": car["f_sensor_value"]["distance"],
                "B_sensor": car["b_sensor_value"]["distance"],
                "L_T_sensor": car["l_t_sensor_value"]["distance"],
                "R_T_sensor": car["r_t_sensor_value"]["distance"],
                "crash_count": car["crash_times"],
                "end_x": end_p[0],
                "end_y": end_p[1],
                "check_points": check_points_coodinate
            }
        return player_info

    def reset(self):
        self.frame_count = 0
        self.set_game_mode()
        # self.game_mode.sound_controller.play_music()

    def isRunning(self):
        return self.game_mode.isRunning()

    @property
    def get_scene_info(self):
        """
        Get the scene information
        """
        scene_info = {
            "frame": self.game_mode.frame,
        }

        for car in self.game_mode.car_info:
            # type of car is dictionary
            scene_info[str(car["id"]) + "P_position"] = car["topleft"]
        return scene_info

    @check_scene_init_data
    def get_scene_init_data(self) -> dict:
        """
        Get the scene and object information for drawing on the web
        """
        game_info = {
            "scene": self.scene.__dict__, "assets": [], "background": [],
            "map_width": self.game_mode.map.tileWidth * 20, "map_height": self.game_mode.map.tileHeight * 20
        }

        game_info["assets"].append(create_asset_init_data("target", 40, 40, TARGET_PATH, TARGET_URL))
        if self.dark_mode:
            bg_path = path.join(ASSET_IMAGE_DIR, BG_IMG)
            bg_url = BG_URL
            game_info["assets"].append(create_asset_init_data("bg_img", 600, 600, bg_path, bg_url))
        else:
            bg_path = path.join(ASSET_IMAGE_DIR, L_BG_IMG)
            bg_url = L_BG_URL
            game_info["assets"].append(create_asset_init_data("bg_img", 600, 600, bg_path, bg_url))
        bar_path = path.join(ASSET_IMAGE_DIR, BAR_IMG)
        bar_url = BAR_URL
        game_info["assets"].append(create_asset_init_data("bar_img", 600, 600, bar_path, bar_url))
        for i in range(self.user_num):
            game_info["assets"].append(
                create_asset_init_data(f"car_0{i + 1}", 32, 32, path.join(ASSET_IMAGE_DIR, f"car_0{i + 1}.png"),
                                       f"https://raw.githubusercontent.com/PAIA-Playful-AI-Arena/dont_touch/{version}/asset/image/car_0{i + 1}.png"))
        for i in range(0, 6):
            game_info["assets"].append(create_asset_init_data(f"regularExplosion0{i}", 40, 40,
                                                              path.join(ASSET_IMAGE_DIR, f"regularExplosion0{i}.png"),
                                                              f"https://raw.githubusercontent.com/PAIA-Playful-AI-Arena/dont_touch/{version}/asset/image/regularExplosion0{i}.png"))

        game_info["background"].append(create_image_view_data("bg_img", 0, 0, 640, 640))
        game_info["background"].append(create_image_view_data("bar_img", 640, 0, 160, 640))

        # game_info["background"].append(create_image_view_data("target", 0, 0, 640, 640))

        for wall in self.game_mode.walls:
            vertices = [(wall.body.transform * v) for v in wall.box.shape.vertices]
            vertices = [self.game_mode.transfer_box2d_to_pygame(v) for v in vertices]
            game_info["background"].append(create_polygon_view_data("wall", vertices, PAIA_B))
        for wall in self.game_mode.slant_walls:
            vertices = [(wall.body.transform * v) for v in wall.box.shape.vertices]
            vertices = [self.game_mode.transfer_box2d_to_pygame(v) for v in vertices]
            game_info["background"].append(create_polygon_view_data("wall", vertices, PAIA_B))
        game_info["musics"] = [
            create_music_init_data("bgm", file_path=BGM_PATH, github_raw_url=BGM_URL),

        ]
        game_info["sounds"] = [
            create_sound_init_data("bomb", file_path=BOMB_PATH, github_raw_url=BOMB_URL),

        ]
        return game_info

    @check_game_progress
    def get_scene_progress_data(self) -> dict:
        """
        Get the position of game objects for drawing on the web
        """
        background = []
        object_list = []
        toggle_with_bias = []
        toggle = []
        game_sys_info = {}
        sound = self.game_mode.sound

        game_progress = {
            "frame": self.frame_count,
            "background": [],
            "object_list": [],
            "toggle_with_bias": [],
            "toggle": [],
            "foreground": [],
            "user_info": [],
            "game_sys_info": {}
        }
        game_sys_info = {"view_center_coordinate": [0, 0]}
        for p in self.game_mode.all_points:
            object_list.append(p.get_progress_data())
            # if isinstance(p,End_point):
            #     point_info = p.get_info()
            x, y = self.game_mode.pygame_to_box2d(p.get_info()["coordinate"], self.map_height / PPM)
            toggle_with_bias.append(
                create_rect_view_data("car_coordinate_rect",
                                      p.rect.centerx - 40, p.rect.centery, 90, 20, BLACK))

            toggle_with_bias.append(
                create_text_view_data(
                    f"({x:.2f},{y:.2f})",
                    p.rect.centerx - 40, p.rect.centery,
                    HELP_TXT_COLOR,
                    HELP_TXT_STYLE
                )
            )

        # background.append(create_image_view_data("bar_img", 640, 0, 160, 640))
        # wall

        # text
        background.append(
            create_text_view_data("{0:05d} frames".format(self.frame_count), 658, 30, WHITE, font_style="21px Arial"))
        for car in self.game_mode.car_info:
            background.append(
                create_text_view_data(
                    f"{car['crash_times']}", WIDTH - 108, 104 + 140 * car["id"], WHITE, font_style="20px Arial")
            )

            background.append(
                create_text_view_data(
                    f"{car['check_point']}", WIDTH - 108, 142 + 140 * car["id"], WHITE,
                    font_style="20px Arial"))

            background.append(
                create_text_view_data(
                    "{0:04d} frames".format(car["end_frame"]), WIDTH - 114, 179 + 140 * car["id"], WHITE,
                    font_style="20px Arial"))

            if car["is_running"]:
                # line
                object_list.append(
                    create_line_view_data(
                        "l_sensor", car["center"][0], car["center"][1],
                        self.game_mode.transfer_box2d_to_pygame(car["l_sensor_value"]["coordinate"])[
                            0],
                        self.game_mode.transfer_box2d_to_pygame(car["l_sensor_value"]["coordinate"])[
                            1],
                        SENSOR_R, 5))

                object_list.append(
                    create_line_view_data("l_top_sensor", car["center"][0], car["center"][1],
                                          self.game_mode.transfer_box2d_to_pygame(
                                              car["l_t_sensor_value"]["coordinate"])[
                                              0],
                                          self.game_mode.transfer_box2d_to_pygame(
                                              car["l_t_sensor_value"]["coordinate"])[
                                              1],
                                          SENSOR_R, 5))

                object_list.append(
                    create_line_view_data("r_top_sensor", car["center"][0], car["center"][1],
                                          self.game_mode.transfer_box2d_to_pygame(
                                              car["r_t_sensor_value"]["coordinate"])[
                                              0],
                                          self.game_mode.transfer_box2d_to_pygame(
                                              car["r_t_sensor_value"]["coordinate"])[
                                              1],
                                          SENSOR_B, 5))
                object_list.append(
                    create_line_view_data("r_sensor", car["center"][0], car["center"][1],
                                          self.game_mode.transfer_box2d_to_pygame(car["r_sensor_value"]["coordinate"])[
                                              0],
                                          self.game_mode.transfer_box2d_to_pygame(car["r_sensor_value"]["coordinate"])[
                                              1],
                                          SENSOR_B, 5))
                object_list.append(
                    create_line_view_data("f_sensor", car["center"][0], car["center"][1],
                                          self.game_mode.transfer_box2d_to_pygame(car["f_sensor_value"]["coordinate"])[
                                              0],
                                          self.game_mode.transfer_box2d_to_pygame(car["f_sensor_value"]["coordinate"])[
                                              1],
                                          SENSOR_Y, 5))
                object_list.append(
                    create_line_view_data("b_sensor", car["center"][0], car["center"][1],
                                          self.game_mode.transfer_box2d_to_pygame(car["b_sensor_value"]["coordinate"])[
                                              0],
                                          self.game_mode.transfer_box2d_to_pygame(car["b_sensor_value"]["coordinate"])[
                                              1],
                                          SENSOR_Y, 5))
                # sensor value
                toggle_with_bias.append(
                    create_rect_view_data("sensor_rect", 60 * math.sin(car["angle"]) + car["center"][0] - 25,
                                          60 * math.cos(car["angle"]) + car["center"][1] - 10, 50, 20, BLACK))  # behind
                toggle_with_bias.append(
                    create_rect_view_data("sensor_rect", 60 * math.sin(-car["angle"]) + car["center"][0] - 25,
                                          -60 * math.cos(-car["angle"]) + car["center"][1] - 10, 50, 20,
                                          BLACK))  # front
                toggle_with_bias.append(create_rect_view_data("sensor_rect", 60 * math.sin(
                    -car["angle"] + math.pi / 4) + car["center"][0] - 25, -60 * math.cos(-car["angle"] + math.pi / 4) +
                                                              car["center"][1] - 10, 50, 20, BLACK))
                toggle_with_bias.append(create_rect_view_data("sensor_rect", 60 * math.sin(
                    -car["angle"] + math.pi / 2) + car["center"][0] - 25, -60 * math.cos(-car["angle"] + math.pi / 2) +
                                                              car["center"][1] - 10, 50, 20, BLACK))
                toggle_with_bias.append(create_rect_view_data("sensor_rect", 60 * math.sin(
                    -car["angle"] - math.pi / 4) + car["center"][0] - 25, -60 * math.cos(-car["angle"] - math.pi / 4) +
                                                              car["center"][1] - 10, 50, 20, BLACK))
                toggle_with_bias.append(create_rect_view_data("sensor_rect", 60 * math.sin(
                    -car["angle"] - math.pi / 2) + car["center"][0] - 25, -60 * math.cos(-car["angle"] - math.pi / 2) +
                                                              car["center"][1] - 10, 50, 20, BLACK))

                toggle_with_bias.append(create_text_view_data(f"{car['b_sensor_value']['distance']}",
                                                              60 * math.sin(car["angle"]) +
                                                              car["center"][0] - 20,
                                                              60 * math.cos(car["angle"]) +
                                                              car["center"][1] - 10, SENSOR_Y,
                                                              font_style="20px Arial"))
                toggle_with_bias.append(create_text_view_data(f"{car['f_sensor_value']['distance']}",
                                                              60 * math.sin(-car["angle"]) +
                                                              car["center"][0] - 20,
                                                              -60 * math.cos(-car["angle"]) +
                                                              car["center"][1] - 10, SENSOR_Y,
                                                              font_style="20px Arial"))
                toggle_with_bias.append(create_text_view_data(f"{car['r_t_sensor_value']['distance']}",
                                                              60 * math.sin(
                                                                  -car["angle"] + math.pi / 4) +
                                                              car["center"][0] - 20, -60 * math.cos(
                        -car["angle"] + math.pi / 4) + car["center"][1] - 10, SENSOR_B, font_style="20px Arial"))
                toggle_with_bias.append(create_text_view_data(f"{car['r_sensor_value']['distance']}",
                                                              60 * math.sin(
                                                                  -car["angle"] + math.pi / 2) +
                                                              car["center"][0] - 20, -60 * math.cos(
                        -car["angle"] + math.pi / 2) + car["center"][1] - 10, SENSOR_B, font_style="20px Arial"))
                toggle_with_bias.append(create_text_view_data(f"{car['l_t_sensor_value']['distance']}",
                                                              60 * math.sin(
                                                                  -car["angle"] - math.pi / 4) +
                                                              car["center"][0] - 20, -60 * math.cos(
                        -car["angle"] - math.pi / 4) + car["center"][1] - 10, SENSOR_R, font_style="20px Arial"))
                toggle_with_bias.append(create_text_view_data(f"{car['l_sensor_value']['distance']}",
                                                              60 * math.sin(
                                                                  -car["angle"] - math.pi / 2) +
                                                              car["center"][0] - 20, -60 * math.cos(
                        -car["angle"] - math.pi / 2) + car["center"][1] - 10, SENSOR_R, font_style="20px Arial"))

                # 車子座標
                toggle_with_bias.append(
                    create_rect_view_data("car_coordinate_rect",
                                          car["topleft"][0] - 20, car["center"][1] + 5, 90, 20, BLACK))

                toggle_with_bias.append(
                    create_text_view_data(
                        f"({car['coordinate'][0]:.1f},{car['coordinate'][1]:.1f})",
                        car["topleft"][0] - 20, car["center"][1] + 5,
                        HELP_TXT_COLOR,
                        HELP_TXT_STYLE
                    )
                )
            object_list.append(
                create_image_view_data(car["image"], car["topleft"][0], car["topleft"][1], car["size"][0],
                                       car["size"][1],
                                       car["angle"])
            )
        game_progress = create_scene_progress_data(
            frame=self.frame_count,
            background=background,
            object_list=object_list,
            foreground=[],
            toggle=toggle,
            toggle_with_bias=toggle_with_bias,
            musics=[MusicProgressSchema(music_id=f"bgm").__dict__],
            sounds=sound, game_sys_info=game_sys_info
        )
        return game_progress

    @check_game_result
    def get_game_result(self):
        """
        Get the game result for the web
        """
        scene_info = self.get_scene_info
        result = self.game_mode.result
        rank = []
        for user in self.game_mode.ranked_user:
            if self.game_mode.check_point_num:
                pass_percent = round(user.check_point / self.game_mode.check_point_num, 5) * 100
                remain_point = self.game_mode.check_point_num - user.check_point
            else:
                pass_percent = 0
                remain_point = 0
            same_rank = {"player_num": str(user.car_no + 1) + "P",
                         "rank": self.game_mode.ranked_user.index(user) + 1,
                         # "frame_limit": self.game_end_time,
                         "used_frame": user.end_frame,
                         # "frame_percent": round(user.end_frame / self.game_end_time * 100, 3),
                         "total_checkpoints": self.game_mode.check_point_num,
                         "check_points": user.check_point,
                         # "remain_points": remain_point,
                         # "pass_percent": pass_percent,
                         "crash_count": user.collide_times,
                         "score": 10000 * user.check_point - 0.001 * user.end_frame - 10 * user.collide_times
                         }
            rank.append(same_rank)
        print({"frame_used": scene_info["frame"],
               "status": self.game_mode.state,
               "attachment": rank,
               })
        return {"frame_used": scene_info["frame"],
                "status": self.game_mode.state,
                "attachment": rank,
                }

        pass

    def get_keyboard_command(self):
        """
        Get the command according to the pressed keys
        """
        if not self.isRunning():
            return {"1P": "RESET",
                    "2P": "RESET",
                    "3P": "RESET",
                    "4P": "RESET"
                    }
        key_pressed_list = pygame.key.get_pressed()
        cmd_1P = {"left_PWM": 0, "right_PWM": 0}
        cmd_2P = {"left_PWM": 0, "right_PWM": 0}
        cmd_3P = {"left_PWM": 0, "right_PWM": 0}
        cmd_4P = {"left_PWM": 0, "right_PWM": 0}

        if key_pressed_list[pygame.K_UP]:
            cmd_1P["left_PWM"] = 100
            cmd_1P["right_PWM"] = 100
        elif key_pressed_list[pygame.K_DOWN]:
            cmd_1P["left_PWM"] = -100
            cmd_1P["right_PWM"] = -100
        if key_pressed_list[pygame.K_LEFT]:
            cmd_1P["right_PWM"] += 100
        elif key_pressed_list[pygame.K_RIGHT]:
            cmd_1P["left_PWM"] += 100

        if key_pressed_list[pygame.K_w]:
            cmd_2P["left_PWM"] = 100
            cmd_2P["right_PWM"] = 100
        elif key_pressed_list[pygame.K_s]:
            cmd_2P["left_PWM"] = -100
            cmd_2P["right_PWM"] = -100
        elif key_pressed_list[pygame.K_a]:
            cmd_2P["right_PWM"] += 100
        elif key_pressed_list[pygame.K_d]:
            cmd_2P["left_PWM"] += 100

        return {"1P": cmd_1P,
                "2P": cmd_2P,
                "3P": cmd_3P,
                "4P": cmd_4P}

    def set_game_mode(self):

        self.game_mode = MazeMode(self.user_num, self.map_file, self.game_end_time, self.sensor_num)
        # self.game_type = "MAZE"
