import time
import arcade
import arcade.gui

SCREEN_TITLE = "Dino T-Rex"
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 500

CHARACTER_SCALING = 1   #for penis.png 0.07
ENEMY_SCALING = 0.8
TILE_SCALING = 1
HEALTH_SCALING = 0.8

PLAYER_MOVEMENT_SPEED = 5
PLAYER_JUMP_SPEED = 19
GRAVITY = 1.2           #1.2 - standart
ENEMY_MOVEMENT_SPEED = 5


#quit method
class QuitButton(arcade.gui.UIFlatButton):
    def on_click(self, event: arcade.gui.UIOnClickEvent):
        arcade.exit()


#start game screen
class StartGameView(arcade.View):
    def __init__(self):
        super().__init__()
        print("Start game screen")

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        self.v_box = arcade.gui.UIBoxLayout()

        #start button
        start_button = arcade.gui.UIFlatButton(text="Start Game", width=200)
        self.v_box.add(start_button.with_space_around(bottom=20))

        #quit button
        quit_button = QuitButton(text="Quit", width=200)
        self.v_box.add(quit_button)

        start_button.on_click = self.on_click_start

        self.manager.add(
            arcade.gui.UIAnchorWidget(anchor_x="center_x", anchor_y="center_y", child=self.v_box)
        )


    def on_click_start(self, event):
        game_view = MyGame()
        game_view.setup()
        self.window.show_view(game_view)


    def on_draw(self):
        self.clear()
        self.manager.draw()
        arcade.draw_text("Main menu", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100, arcade.color.WHITE, 30, anchor_x="center",)



#game
class MyGame(arcade.View):
    def __init__(self):
        super().__init__()

        self.scene = None
        self.background = None
        self.player_sprite = None
        self.enemy_sprite = None
        self.ground = None
        self.physics_engine = None
        self.camera = None
        self.gui_camera = None
        self.score = 0
        self.high_score = 0
        self.health = 3

        self.num_platform = 0
        self.num_cactus = 0

        self.jump_sound = arcade.load_sound("resources/sounds/jump.wav")
        self.score_sound = arcade.load_sound("resources/sounds/update_score.wav")
        self.lose_sound = arcade.load_sound("resources/sounds/lose.wav")
        print("Load sounds")

        arcade.set_background_color(arcade.csscolor.GAINSBORO)


    def setup(self):
        #create camera
        self.camera = arcade.Camera(self.window.width, self.window.height)
        self.gui_camera = arcade.Camera(self.window.width, self.window.height)
        print("Cerate camera")

        #create scene
        self.scene = arcade.Scene()

        #textures
        self.background = arcade.load_texture("resources/images/background.png")
        print("Load background")

        #player sprite
        dino = "resources/images/dino.png"
        self.player_sprite = arcade.Sprite(dino, CHARACTER_SCALING)
        self.player_sprite.center_x = 200
        self.player_sprite.center_y = 210
        self.scene.add_sprite("Player", self.player_sprite)
        print("Spawn player sprite")

        #health sprites
        for coordinate_x in range(30, 180, 50):
            self.hp_full = arcade.Sprite("resources/images/hp_full.png", HEALTH_SCALING)
            self.hp_full.center_x = coordinate_x
            self.hp_full.center_y = 370
            self.scene.add_sprite("Health", self.hp_full)
        print("Spawn health sprites")


        #enemy sprite                               500 points - one cactus
        for self.cactus_coordinate_x in range(500, 11500, 500):
            coordinate_list = [[self.cactus_coordinate_x, 185]]
            self.num_cactus += 1

            for coordinate in coordinate_list:
                self.cactus = arcade.Sprite("resources/images/cactus.png", ENEMY_SCALING)
                self.cactus.position = coordinate
                self.scene.add_sprite("Enemy", self.cactus)
        
        print(f"Spawn enemy sprites")


        #ground sprite                         400 points - one platform, 5000 points - 10 platforms
        for platform_coordinate in range(800, 12000, 400):
            self.num_platform += 1

            for x in range(250, platform_coordinate, 500):
                self.ground = arcade.Sprite("resources/images/ground.png", TILE_SCALING)
                self.ground.center_x = x
                self.ground.center_y = 75
                self.scene.add_sprite("Walls", self.ground)
        
        print(f"Spawn ground sprite\ncactuses: [{self.num_cactus}]\nplatforms: [{self.num_platform}]")
            

        #physics engine
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant = GRAVITY, walls = self.scene["Walls"]
        )


    #render screen
    def on_draw(self):
        self.clear()
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)
        self.camera.use()
        self.scene.draw()
        self.gui_camera.use()


        score_text = f"Score: {round(self.score)}"
        
        if int(self.score) > int(self.high_score):
            best_score_text = f"Best: {round(self.score)}"
        else:
            best_score_text = f"Best: {self.high_score}"

        arcade.draw_text(score_text, 10, 470, arcade.csscolor.BLACK, 18)
        arcade.draw_text(best_score_text, 10, 440, arcade.csscolor.BLACK, 18)
        arcade.draw_text(f"Lifes: {self.health}", 10, 410, arcade.csscolor.BLACK, 18)


    #key-log
    def on_key_press(self, key, modifiers):

        #move up
        if key == arcade.key.UP or key == arcade.key.SPACE:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                arcade.play_sound(self.jump_sound)
        #move down
        elif key == arcade.key.DOWN:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        #show pause
        elif key == arcade.key.ESCAPE:
            pause = GamePauseView(self)
            self.window.show_view(pause)
        

        #"""!!!must be off!!!"""
        #elif key == arcade.key.LEFT:
        #    self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        #elif key == arcade.key.RIGHT:
        #    self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        

    def on_key_release(self, key, modifiers):
        #move up
        if key == arcade.key.UP or key == arcade.key.SPACE:
            self.player_sprite.change_y = 0
        #move down
        elif key == arcade.key.DOWN:
            self.player_sprite.change_y = 0
        

        #"""!!!must be off!!!"""
        #elif key == arcade.key.LEFT:
        #    self.player_sprite.change_x = -0
        #elif key == arcade.key.RIGHT:
        #    self.player_sprite.change_x = 0
    

    #camera settings 
    def center_camera_to_player(self):
        self.screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        self.screen_center_y = 0

        # Don't let camera travel past 0
        if self.screen_center_x < 0:
            self.screen_center_x = 0
        if self.screen_center_y < 0:
            self.screen_center_y = 0
        player_centered = self.screen_center_x, self.screen_center_y

        self.camera.move_to(player_centered)

    
    #check cactus and player
    def hit_player(self):
        cactus_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene["Enemy"]
        )

        for cactus in cactus_hit_list:
            arcade.play_sound(self.lose_sound)
            time.sleep(0.3)

            self.health -= 1
            print(f"Heath: {self.health}")
            if self.health == 0:
                game_over = GameOverView()
                self.window.show_view(game_over)
            else:
                self.player_sprite.center_x = 50
                self.score = 0
    

    #move palyer and update score
    def mpaus(self):
        #move player
        self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        #update score
        self.score += self.player_sprite.center_x / 10000

        #read score
        with open("resources/highscore.txt") as file_score:
            self.high_score = file_score.readline()

        #check score
        with open("resources/highscore.txt", "w") as f:
            if int(round(self.score)) > int(float(self.high_score)):
                f.write(str(int(self.score)))
            else:
                f.write(self.high_score)
        
        #play score sound
        for sound in range(500, 10500, 500):
            if sound == int(round(self.score)):
                arcade.play_sound(self.score_sound)
        
    
    #regenerate map 
    def uodate_screen_textures_and_map(self):
        if self.screen_center_x > self.cactus_coordinate_x:
            pass #soon


    #update functions
    def on_update(self, delta_time):
        self.physics_engine.update()
        self.center_camera_to_player()
        self.hit_player()
        self.mpaus()



#game pause screen
class GamePauseView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        print("Pause screen")
        
        self.game_view = game_view
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        arcade.set_background_color(arcade.csscolor.INDIGO)

        self.v_box = arcade.gui.UIBoxLayout()

        #continue button
        continue_button = arcade.gui.UIFlatButton(text="Continue Game", width=200)
        self.v_box.add(continue_button.with_space_around(bottom=20))

        #restart button
        restart_button = arcade.gui.UIFlatButton(text="Restart Game", width=200)
        self.v_box.add(restart_button.with_space_around(bottom=20))

        #quit button
        quit_button = QuitButton(text="Quit", width=200)
        self.v_box.add(quit_button)

        continue_button.on_click = self.on_click_continue
        restart_button.on_click = self.on_click_restart

        self.manager.add(
            arcade.gui.UIAnchorWidget(anchor_x="center_x", anchor_y="center_y", child=self.v_box)
        )


    def on_click_continue(self, event):
        self.window.show_view(self.game_view)
        arcade.set_background_color(arcade.csscolor.GAINSBORO)


    def on_click_restart(self, event):
        game_view = MyGame()
        game_view.setup()
        self.window.show_view(game_view)


    def on_draw(self):
        self.clear()
        self.manager.draw()
        arcade.draw_text("Game paused", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 130, arcade.color.WHITE, 30, anchor_x="center",)




#game over screen
class GameOverView(arcade.View):
    def __init__(self):
        super().__init__()
        print("Game over screen")

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        arcade.set_background_color(arcade.csscolor.DARK_SLATE_GREY)

        self.v_box = arcade.gui.UIBoxLayout()

        #restart button
        restart_button = arcade.gui.UIFlatButton(text="Restart Game", width=200)
        self.v_box.add(restart_button.with_space_around(bottom=20))

        #quit button
        quit_button = QuitButton(text="Quit", width=200)
        self.v_box.add(quit_button)

        restart_button.on_click = self.on_click_restart

        self.manager.add(
            arcade.gui.UIAnchorWidget(anchor_x="center_x", anchor_y="center_y", child=self.v_box)
        )


    def on_click_restart(self, event):
        game_view = MyGame()
        game_view.setup()
        self.window.show_view(game_view)


    def on_draw(self):
        self.clear()
        self.manager.draw()
        arcade.draw_text("Game over", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100, arcade.color.WHITE, 30, anchor_x="center",)



def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = StartGameView()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()
    print("Game ended successfully")