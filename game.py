from ursina import *
import random, math

try:
    from ursina.shaders import unlit_shader
except Exception:
    unlit_shader = None

app = Ursina()
window.color = (0.09, 0.10, 0.13, 1)
scene.fog_density = 0

# ======================
# 基本設定
# ======================
GRID_W, GRID_H = 18, 18
TILE = 1
MAX_INFRACTION = 3
CLASS_DEADLINE = 185

MODE_WALK = "WALK"
MODE_RIDE = "RIDE"

PATROL = "PATROL"
INVESTIGATE = "INVESTIGATE"
CHASE = "CHASE"

ALERT_GREEN = "GREEN"
ALERT_YELLOW = "YELLOW"
ALERT_RED = "RED"

# 地形
ROAD = "road"
BUILDING = "building"
GRASS = "grass"
HIDEOUT = "hideout"
DORM = "dorm"
CLASSROOM = "classroom"
CHARGE = "charge"

tiles = {}
blocked = set()
roadblock_entities = []
npcs = []
classrooms = [(14, 3), (3, 14), (14, 14)]
visited_classrooms = set()
game_time = 0
phase = 1
last_message = "Reach every classroom, then return to dorm."


def grid_to_world(x, z):
    return Vec3(x - GRID_W // 2, 0, z - GRID_H // 2)


def world_to_grid(pos):
    return int(round(pos.x + GRID_W // 2)), int(round(pos.z + GRID_H // 2))


def in_bounds(x, z):
    return 0 <= x < GRID_W and 0 <= z < GRID_H


def dist_grid(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def visual_kwargs():
    return {"shader": unlit_shader} if unlit_shader else {}


def rgb(r, g, b, a=1):
    return (r / 255, g / 255, b / 255, a)


def solid_cube(**kwargs):
    return Entity(model="cube", **visual_kwargs(), **kwargs)


def random_free_cell():
    while True:
        x, z = random.randrange(GRID_W), random.randrange(GRID_H)
        tile = tiles.get((x, z))
        if (x, z) not in blocked and (not tile or tile.tile_type not in (BUILDING, CLASSROOM, DORM, CHARGE)):
            return (x, z)


# ======================
# 地圖
# ======================
def tile_color(tile_type):
    if tile_type == ROAD:
        return rgb(88, 90, 96)
    if tile_type == BUILDING:
        return rgb(74, 79, 92)
    if tile_type == GRASS:
        return rgb(57, 135, 76)
    if tile_type == HIDEOUT:
        return rgb(65, 170, 205)
    if tile_type == DORM:
        return rgb(230, 145, 58)
    if tile_type == CLASSROOM:
        return rgb(235, 205, 84)
    if tile_type == CHARGE:
        return rgb(88, 220, 115)
    return color.white


def add_marker(x, z, marker_color, height=0.18):
    solid_cube(
        scale=(0.52, height, 0.52),
        position=grid_to_world(x, z) + Vec3(0, 0.14, 0),
        color=marker_color
    )


def make_map():
    solid_cube(
        scale=(GRID_W + 1.5, 0.04, GRID_H + 1.5),
        position=Vec3(-0.5, -0.08, -0.5),
        color=rgb(28, 32, 40)
    )

    for x in range(GRID_W):
        for z in range(GRID_H):
            t = ROAD

            # 草皮區
            if 5 <= x <= 8 and 5 <= z <= 8:
                t = GRASS

            # 教學大樓禁騎區
            if 10 <= x <= 12 and 4 <= z <= 8:
                t = BUILDING

            # 安全區
            if (x, z) in [(2, 2), (15, 15)]:
                t = HIDEOUT

            # 宿舍
            if (x, z) == (1, 16):
                t = DORM

            # 教室
            if (x, z) in classrooms:
                t = CLASSROOM

            # 偷充電車棚
            if (x, z) == (16, 1):
                t = CHARGE

            e = solid_cube(
                scale=(1, 0.08, 1),
                position=grid_to_world(x, z),
                color=tile_color(t),
                collider="box"
            )
            e.tile_type = t
            tiles[(x, z)] = e

            if t == BUILDING:
                solid_cube(
                    scale=(0.86, 0.42, 0.86),
                    position=grid_to_world(x, z) + Vec3(0, 0.28, 0),
                    color=rgb(50, 54, 66)
                )
            elif t == GRASS and random.random() < 0.35:
                add_marker(x, z, rgb(96, 180, 80), 0.12)
            elif t in (CLASSROOM, DORM, HIDEOUT, CHARGE):
                add_marker(x, z, tile_color(t), 0.34)


def add_roadblocks():
    global last_message
    if roadblock_entities:
        return

    for cell in [(8, 2), (8, 3), (9, 11), (10, 11), (4, 8), (13, 13)]:
        blocked.add(cell)
        world = grid_to_world(*cell)
        roadblock_entities.append(solid_cube(
            scale=(0.9, 0.5, 0.25),
            position=world + Vec3(0, 0.28, 0),
            color=rgb(210, 60, 55),
            collider="box"
        ))
    last_message = "Phase 2: surprise inspection. Roadblocks are active."


# ======================
# 玩家
# ======================
class Player(Entity):
    def __init__(self):
        super().__init__(
            model="cube",
            **visual_kwargs(),
            color=rgb(245, 245, 245),
            scale=(0.55, 0.55, 0.55),
            position=grid_to_world(1, 16) + Vec3(0, 0.4, 0),
            collider="box"
        )
        self.body = solid_cube(parent=self, scale=(0.7, 0.45, 0.45), position=(0, 0.2, 0), color=rgb(245, 245, 245))
        self.bag = solid_cube(parent=self, scale=(0.32, 0.32, 0.22), position=(-0.3, 0.18, -0.15), color=rgb(55, 95, 220))
        self.scooter = solid_cube(parent=self, scale=(0.95, 0.12, 0.22), position=(0, -0.18, 0), color=rgb(35, 35, 42))
        self.front_light = solid_cube(parent=self, scale=(0.18, 0.14, 0.16), position=(0, -0.08, 0.2), color=rgb(255, 230, 120))
        self.mode = MODE_WALK
        self.battery = 100
        self.infraction = 0
        self.speed = 3.0
        self.adrenaline = 0
        self.fatigue = 0
        self.caught_cooldown = 0
        self.scooter_confiscated = False

    def grid_pos(self):
        return world_to_grid(self.position)

    def current_tile(self):
        return tiles.get(self.grid_pos())

    def update(self):
        # 切換步行 / 騎車
        if held_keys["r"] and self.battery > 0 and not self.scooter_confiscated:
            self.mode = MODE_RIDE
        if held_keys["f"]:
            self.mode = MODE_WALK

        base_speed = 3 if self.mode == MODE_WALK else 6
        tile = self.current_tile()

        if tile and tile.tile_type == GRASS:
            base_speed *= 0.72 if self.mode == MODE_WALK else 0.48

        if self.fatigue > 0:
            self.fatigue -= time.dt
            base_speed *= 0.55

        if self.adrenaline > 0:
            self.adrenaline -= time.dt
            base_speed *= 1.6
            if self.adrenaline <= 0:
                self.fatigue = 2.5

        self.speed = base_speed

        # 移動
        move = Vec3(
            held_keys["d"] - held_keys["a"],
            0,
            held_keys["w"] - held_keys["s"]
        )

        if move.length() > 0:
            move = move.normalized()

            # 草皮：騎車會打滑
            if tile and tile.tile_type == GRASS and self.mode == MODE_RIDE:
                if random.random() < 0.03:
                    slip = Vec3(random.choice([-1, 1]), 0, random.choice([-1, 1]))
                    move = slip.normalized()

            next_pos = self.position + move * self.speed * time.dt
            gx, gz = world_to_grid(next_pos)

            if in_bounds(gx, gz) and (gx, gz) not in blocked:
                self.position = next_pos
                if move.length() > 0:
                    self.rotation_y = math.degrees(math.atan2(move.x, move.z))

        # 騎車耗電
        if self.mode == MODE_RIDE:
            self.battery -= 6 * time.dt
            if self.battery <= 0:
                self.battery = 0
                self.mode = MODE_WALK

        if self.scooter_confiscated:
            self.mode = MODE_WALK

        self.scooter.enabled = self.mode == MODE_RIDE and not self.scooter_confiscated
        self.front_light.enabled = self.mode == MODE_RIDE and not self.scooter_confiscated

        # 車棚充電
        tile = self.current_tile()
        if tile and tile.tile_type == CHARGE and not self.scooter_confiscated:
            self.battery = min(100, self.battery + 25 * time.dt)

        if self.caught_cooldown > 0:
            self.caught_cooldown -= time.dt

    def make_noise_radius(self):
        if self.mode == MODE_WALK:
            return 2.5
        return 7.5

    def caught(self):
        if self.caught_cooldown > 0:
            return

        gx, gz = self.grid_pos()
        tile = tiles.get((gx, gz))
        penalty = 1

        # 教學大樓內騎車被抓：重罰
        if tile and tile.tile_type == BUILDING and self.mode == MODE_RIDE:
            penalty = 2
            self.scooter_confiscated = True

        self.infraction += penalty
        self.caught_cooldown = 2

        # 被抓後強制下車
        self.mode = MODE_WALK
        self.adrenaline = 0
        self.fatigue = 2

        # 傳回宿舍附近
        self.position = grid_to_world(1, 16) + Vec3(0, 0.4, 0)


# ======================
# 路人 NPC
# ======================
class Pedestrian(Entity):
    def __init__(self):
        cell = random_free_cell()
        super().__init__(
            model="cube",
            **visual_kwargs(),
            color=random.choice([rgb(230, 110, 145), rgb(95, 190, 220), rgb(235, 205, 100)]),
            scale=(0.38, 0.6, 0.38),
            position=grid_to_world(*cell) + Vec3(0, 0.36, 0),
            collider="box"
        )
        self.target = random_free_cell()
        self.speed = random.uniform(0.75, 1.15)

    def update(self):
        if dist_grid(world_to_grid(self.position), self.target) == 0:
            self.target = random_free_cell()

        target_world = grid_to_world(*self.target) + Vec3(0, 0.36, 0)
        direction = target_world - self.position
        if direction.length() > 0.05:
            self.position += direction.normalized() * self.speed * time.dt

        if distance(self.position, player.position) < 0.55:
            player.fatigue = max(player.fatigue, 0.7)
            if player.mode == MODE_RIDE:
                player.battery = max(0, player.battery - 10 * time.dt)


def spawn_festival_crowd():
    global last_message
    if npcs:
        return
    for _ in range(18):
        npcs.append(Pedestrian())
    last_message = "Phase 3: festival crowd. Avoid pedestrians on the way back."


# ======================
# 教官 AI
# ======================
class Instructor(Entity):
    def __init__(self, patrol_points):
        super().__init__(
            model="cube",
            **visual_kwargs(),
            color=rgb(215, 55, 55),
            scale=(0.55, 0.65, 0.55),
            position=grid_to_world(*patrol_points[0]) + Vec3(0, 0.4, 0),
            collider="box"
        )
        self.cap = solid_cube(parent=self, scale=(0.7, 0.15, 0.7), position=(0, 0.45, 0), color=rgb(40, 40, 45))
        self.beacon = solid_cube(parent=self, scale=(0.26, 0.2, 0.26), position=(0, 0.68, 0), color=color.green)
        self.vision_marker = solid_cube(
            scale=(0.18, 0.04, 2.5),
            position=self.position + Vec3(0, 0.08, 1.25),
            color=rgb(255, 230, 60)
        )
        self.state = PATROL
        self.patrol_points = patrol_points
        self.patrol_index = 0
        self.target_pos = patrol_points[0]
        self.speed = 2.2
        self.vision_range = 5
        self.vision_angle = 70
        self.forward_dir = Vec3(0, 0, 1)
        self.investigate_timer = 0
        self.support_cooldown = 0

    def grid_pos(self):
        return world_to_grid(self.position)

    def update(self):
        if self.support_cooldown > 0:
            self.support_cooldown -= time.dt
        self.sense_player()
        self.act()
        self.update_look()

    def update_look(self):
        if self.state == PATROL:
            self.beacon.color = color.green
            self.color = rgb(215, 55, 55)
        elif self.state == INVESTIGATE:
            self.beacon.color = color.yellow
            self.color = rgb(230, 150, 45)
        else:
            self.beacon.color = color.red
            self.color = rgb(255, 40, 35)

        self.vision_marker.position = self.position + self.forward_dir * 1.55 + Vec3(0, 0.08, 0)
        self.vision_marker.rotation_y = math.degrees(math.atan2(self.forward_dir.x, self.forward_dir.z))
        self.vision_marker.enabled = self.state != CHASE

    def sense_player(self):
        p_pos = player.position
        to_player = p_pos - self.position
        d = to_player.length()

        # 安全區：教官失去追捕狀態
        tile = player.current_tile()
        if tile and tile.tile_type == HIDEOUT:
            self.state = PATROL
            return

        # 聽到電動車
        if d < player.make_noise_radius() and player.mode == MODE_RIDE and self.state != CHASE:
            self.state = INVESTIGATE
            self.target_pos = player.grid_pos()
            self.investigate_timer = 2.5

        # 視線錐偵測
        if 0.01 < d < self.vision_range:
            dir_to_player = to_player.normalized()
            dot_value = self.forward_dir.dot(dir_to_player)
            angle = math.degrees(math.acos(max(-1, min(1, dot_value))))

            # 騎車更容易被抓，走路要很近才會被注意
            suspicious = player.mode == MODE_RIDE or d < 2.0

            if angle < self.vision_angle / 2 and suspicious:
                self.state = CHASE
                player.adrenaline = max(player.adrenaline, 2.0)
                call_support(self)

    def act(self):
        self.speed = 2.15 if self.state == PATROL else 2.65 if self.state == INVESTIGATE else 3.35

        if self.state == PATROL:
            self.patrol()

        elif self.state == INVESTIGATE:
            self.move_to_grid(self.target_pos)
            self.investigate_timer -= time.dt
            if self.investigate_timer <= 0:
                self.state = PATROL

        elif self.state == CHASE:
            self.chase_player()

        # 抓到
        if distance(self.position, player.position) < 0.7:
            player.caught()
            self.state = PATROL

    def patrol(self):
        target = self.patrol_points[self.patrol_index]
        self.move_to_grid(target)

        if dist_grid(self.grid_pos(), target) == 0:
            self.patrol_index = (self.patrol_index + 1) % len(self.patrol_points)

    def chase_player(self):
        # 預測座標：往玩家前方堵
        px, pz = player.grid_pos()

        predict = (px, pz)
        if held_keys["w"]:
            predict = (px, pz + 2)
        elif held_keys["s"]:
            predict = (px, pz - 2)
        elif held_keys["a"]:
            predict = (px - 2, pz)
        elif held_keys["d"]:
            predict = (px + 2, pz)

        predict = (
            max(0, min(GRID_W - 1, predict[0])),
            max(0, min(GRID_H - 1, predict[1]))
        )

        self.move_to_grid(predict)

    def move_to_grid(self, grid_pos):
        if grid_pos in blocked:
            grid_pos = self.grid_pos()
        target_world = grid_to_world(*grid_pos) + Vec3(0, 0.4, 0)
        direction = target_world - self.position

        if direction.length() < 0.05:
            return

        self.forward_dir = direction.normalized()
        self.position += self.forward_dir * self.speed * time.dt


def call_support(source):
    if source.support_cooldown > 0:
        return
    source.support_cooldown = 3
    sx, sz = source.grid_pos()
    px, pz = player.grid_pos()
    intercept = (
        max(0, min(GRID_W - 1, px + (1 if px >= sx else -1) * 2)),
        max(0, min(GRID_H - 1, pz + (1 if pz >= sz else -1) * 2))
    )

    for other in instructors:
        if other is source:
            continue
        if dist_grid(other.grid_pos(), source.grid_pos()) <= 9:
            other.state = INVESTIGATE
            other.target_pos = intercept
            other.investigate_timer = 3.5


def current_alert_level():
    if any(i.state == CHASE for i in instructors):
        return ALERT_RED
    if any(i.state == INVESTIGATE for i in instructors):
        return ALERT_YELLOW
    return ALERT_GREEN


def set_phase(new_phase):
    global phase
    if new_phase <= phase:
        return
    phase = new_phase

    if phase == 2:
        add_roadblocks()
        instructors.append(Instructor([(2, 9), (7, 9), (7, 15), (2, 15)]))
    elif phase == 3:
        spawn_festival_crowd()
        instructors.append(Instructor([(11, 15), (16, 15), (16, 5), (11, 5)]))


# ======================
# UI
# ======================
info = Text(position=(-0.86, 0.45), scale=1.18, background=True)
info.color = color.black
hint = Text(
    text="WASD Move | R Ride | F Walk | Blue Hideout clears chase | Green Charge | Finish classes then return Dorm",
    position=(-0.86, -0.47),
    scale=0.9,
    background=True
)
hint.color = color.black

game_over_text = None


def check_progress():
    global game_over_text, last_message

    gx, gz = player.grid_pos()
    tile = tiles.get((gx, gz))

    if tile and tile.tile_type == CLASSROOM:
        if (gx, gz) not in visited_classrooms:
            visited_classrooms.add((gx, gz))
            tile.color = rgb(150, 225, 130)
            last_message = f"Class completed: {len(visited_classrooms)}/{len(classrooms)}"

    all_classes_done = len(visited_classrooms) == len(classrooms)
    if len(visited_classrooms) >= 1:
        set_phase(2)
    if all_classes_done:
        set_phase(3)

    if tile and tile.tile_type == HIDEOUT:
        for instructor in instructors:
            instructor.state = PATROL
        last_message = "Hidden safely. Alert reset."

    if player.infraction >= MAX_INFRACTION:
        end_game("Expelled: Too Many Infractions")

    if player.scooter_confiscated and not all_classes_done:
        end_game("Expelled: Scooter Confiscated Before Class")

    if game_time >= CLASS_DEADLINE and not all_classes_done:
        end_game("Expelled: Late for Required Classes")

    if all_classes_done and tile and tile.tile_type == DORM:
        end_game("Victory: Completed All Classes and Returned to Dorm")


def end_game(msg):
    global game_over_text
    if game_over_text is None:
        game_over_text = Text(text=msg, scale=2.5, origin=(0, 0), background=True)
        application.pause()


def update_ui():
    classroom_status = f"{len(visited_classrooms)}/{len(classrooms)}"
    alert_states = ",".join([i.state for i in instructors])
    remaining = max(0, int(CLASS_DEADLINE - game_time))
    alert = current_alert_level()

    info.text = (
        f"Phase: {phase} | Alert: {alert}\n"
        f"Mode: {player.mode}\n"
        f"Battery: {int(player.battery)}\n"
        f"Infractions: {player.infraction}/{MAX_INFRACTION}\n"
        f"Deadline: {remaining}s\n"
        f"Classes Done: {classroom_status}\n"
        f"Instructors: {alert_states}\n"
        f"{last_message}"
    )


def update():
    global game_time
    game_time += time.dt
    player.update()

    for i in instructors:
        i.update()

    for npc in npcs:
        npc.update()

    check_progress()
    update_ui()


# ======================
# 啟動
# ======================
make_map()

player = Player()

instructors = [
    Instructor([(4, 4), (4, 12), (10, 12), (10, 4)]),
    Instructor([(13, 2), (16, 2), (16, 10), (13, 10)])
]

# 俯視鏡頭
camera.position = (-0.5, 22, -0.5)
camera.rotation_x = 90
camera.orthographic = True
camera.fov = 19

window.title = "Campus Violation Patrol Simulation MVP"
app.run()
