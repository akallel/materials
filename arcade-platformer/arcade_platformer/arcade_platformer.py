#
# Arcade Platformer
#
# Demonstrating the capbilities of arcade in a platformer game
# Supporting the Arcade Platformer article on https://realpython.com
#
# All game artwork and sounds, except the tile map and victory sound, from www.kenney.nl
#

# Import libraries
import arcade
from os import path, chdir
from time import sleep

from constants import *

# Global variables
# Assets path
assets_path = path.join(path.dirname(path.abspath(__file__)), "..", "assets")

# Classes

# Enemy class


class Enemy(arcade.AnimatedWalkingSprite):
    """An enemy sprite with basic walking movement
    """

    def __init__(self, pos_x, pos_y):
        super().__init__(CHARACTER_SCALING, center_x=pos_x, center_y=pos_y)

        # Where are the player images stored?
        texture_path = path.join(assets_path, "images", "enemies")

        # Setup the appropriate textures
        walking_texture_path = [
            path.join(texture_path, "slimePurple.png"),
            path.join(texture_path, "slimePurple_move.png"),
        ]
        standing_texture_path = path.join(texture_path, "slimePurple.png")

        # Load them all now
        self.walk_left_textures = [
            arcade.load_texture(texture)
            for texture in walking_texture_path
        ]

        self.walk_right_textures = [
            arcade.load_texture(
                texture,  mirrored=True
            )
            for texture in walking_texture_path
        ]

        self.stand_left_textures = [
            arcade.load_texture(
                standing_texture_path, mirrored=True
            )
        ]
        self.stand_right_textures = [
            arcade.load_texture(standing_texture_path, )
        ]

        # Set the enemy defaults
        self.state = arcade.FACE_LEFT
        self.change_x = -PLAYER_MOVE_SPEED // 2


# Title view
class TitleView(arcade.View):
    """TitleView shows a title screen and prompts the user to begin the game.
    There is a way to show instructions and start the game.
    """

    def __init__(self):
        # Initialize the parent
        super().__init__()

        # Find the folder contain our images
        title_image_path = path.join(assets_path, "images", "title_image.png")

        # Load our title image
        self.title_image = arcade.load_texture(title_image_path)

        # Set our display timer
        self.display_timer = 3.0

        # Are we showing the instructions?
        self.show_instructions = False

    def on_update(self, delta_time):
        """Processes our timer to toggle the instructions
        
        Arguments:
            delta_time {float} -- time passed since last update
        """

        # First, count down the time
        self.display_timer -= delta_time

        # If the timer has run out, we toggle the instructions
        if self.display_timer < 0:

            # Toggle whether to show the instructions
            self.show_instructions = not self.show_instructions

            # And reset the timer so the instructions flash slowly
            self.display_timer = 1.0

    def on_draw(self):
        """Draws everything to the screen
        """

        # Start the rendering loop
        arcade.start_render()

        # Draw a rectangle filled with our title image
        arcade.draw_texture_rectangle(
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            self.title_image,
        )

        # Should we show our instructions?
        if self.show_instructions:
            arcade.draw_text(
                "Enter to Start | I for Instructions",
                100,
                220,
                arcade.color.INDIGO,
                40,
            )

    def on_key_press(self, key, modifiers):
        """Resume the game when the user presses ESC again
        
        Arguments:
            key {int} -- Which key was pressed
            modifiers {int} -- What modifiers were active
        """
        if key == arcade.key.RETURN:
            game_view = PlatformerView()
            game_view.setup()
            self.window.show_view(game_view)
        elif key == arcade.key.I:
            instructions_view = InstructionsView()
            self.window.show_view(instructions_view)


# Instructions view
class InstructionsView(arcade.View):
    def __init__(self):
        super().__init__()

        # Find the folder contain our images
        instructions_image_path = path.join(
            assets_path, "images", "instructions_image.png"
        )

        # Load our title image
        self.instructions_image = arcade.load_texture(instructions_image_path)

    def on_draw(self):
        """Draws everything to the screen
        """

        # Start the rendering loop
        arcade.start_render()

        # Draw a rectangle filled with our title image
        arcade.draw_texture_rectangle(
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            self.instructions_image,
        )

    def on_key_press(self, key, modifiers):
        """Resume the game when the user presses ESC again
        
        Arguments:
            key {int} -- Which key was pressed
            modifiers {int} -- What modifiers were active
        """
        if key == arcade.key.RETURN:
            game_view = PlatformerView()
            game_view.setup()
            self.window.show_view(game_view)

        elif key == arcade.key.ESCAPE:
            title_view = TitleView()
            self.window.show_view(title_view)


# Pause view, used when the player pauses the game
class PauseView(arcade.View):
    """Shown when the game is paused
    """

    def __init__(self, game_view):
        # Initialize the parent
        super().__init__()

        # Store a reference to the underlying view
        self.game_view = game_view

        # Store a semi-transparent color to use as an overlay
        self.fill_color = arcade.make_transparent_color(
            arcade.color.WHITE, transparency=150
        )

    def on_draw(self):
        """Draw the underlying screen, blurred, then the Paused text
        """

        # First, draw the underlying view
        # This also calls start_render(), so no need to do it again
        self.game_view.on_draw()

        # Now create a filled rect that covers the current viewport
        # We get the viewport size from the game view
        arcade.draw_lrtb_rectangle_filled(
            self.game_view.view_left,
            self.game_view.view_left + SCREEN_WIDTH,
            self.game_view.view_bottom + SCREEN_HEIGHT,
            self.game_view.view_bottom,
            self.fill_color,
        )

        # Now show the Pause text
        arcade.draw_text(
            "PAUSED - ESC TO CONTINUE",
            self.game_view.view_left + 180,
            self.game_view.view_bottom + 300,
            arcade.color.INDIGO,
            40,
        )

    def on_key_press(self, key, modifiers):
        """Resume the game when the user presses ESC again
        
        Arguments:
            key {int} -- Which key was pressed
            modifiers {int} -- What modifiers were active
        """
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.game_view)


# Victory View, shown when the player completes a level successfully
class VictoryView(arcade.View):
    """Shown when a level is completed
    """

    def __init__(self, game_view, victory_sound):
        # Initialize the parent
        super().__init__()

        # Store a reference to the underlying view
        self.game_view = game_view

        # Play the victory sound
        arcade.play_sound(victory_sound)

        # Store a semi-transparent color to use as an overlay
        self.fill_color = arcade.make_transparent_color(
            arcade.color.WHITE, transparency=150
        )

    def on_draw(self):
        """Draw the underlying screen, blurred, then the victory text
        """

        # First, draw the underlying view
        # This also calls start_render(), so no need to do it again
        self.game_view.on_draw()

        # Now create a filled rect that covers the current viewport
        # We get the viewport size from the game view
        arcade.draw_lrtb_rectangle_filled(
            self.game_view.view_left,
            self.game_view.view_left + SCREEN_WIDTH,
            self.game_view.view_bottom + SCREEN_HEIGHT,
            self.game_view.view_bottom,
            self.fill_color,
        )

        # Now show the victory text
        arcade.draw_text(
            "SUCCESS! Press Enter for next level...",
            self.game_view.view_left + 90,
            self.game_view.view_bottom + 300,
            arcade.color.INDIGO,
            40,
        )

    def on_key_press(self, key, modifiers):
        """Start the next level when the user presses Enter
        
        Arguments:
            key {int} -- Which key was pressed
            modifiers {int} -- What modifiers were active
        """
        if key == arcade.key.ENTER:
            self.game_view.level += 1
            self.game_view.setup()
            self.window.show_view(self.game_view)


# Game Over View, shown when the game is over
class GameOverView(arcade.View):
    """Shown when a level is completed
    """

    def __init__(self, game_view):
        # Initialize the parent
        super().__init__()

        # Store a reference to the underlying view
        self.game_view = game_view

        # Store a semi-transparent color to use as an overlay
        self.fill_color = arcade.make_transparent_color(
            arcade.color.WHITE, transparency=150
        )

    def on_draw(self):
        """Draw the underlying screen, blurred, then the victory text
        """

        # First, draw the underlying view
        # This also calls start_render(), so no need to do it again
        self.game_view.on_draw()

        # Now create a filled rect that covers the current viewport
        # We get the viewport size from the game view
        arcade.draw_lrtb_rectangle_filled(
            self.game_view.view_left,
            self.game_view.view_left + SCREEN_WIDTH,
            self.game_view.view_bottom + SCREEN_HEIGHT,
            self.game_view.view_bottom,
            self.fill_color,
        )

        # Now show the game over text
        arcade.draw_text(
            "Game Over!",
            self.game_view.view_left + 360,
            self.game_view.view_bottom + 330,
            arcade.color.INDIGO,
            40,
        )
        arcade.draw_text(
            "Enter to restart, ESC to exit",
            self.game_view.view_left + 190,
            self.game_view.view_bottom + 280,
            arcade.color.INDIGO,
            40,
        )

    def on_key_press(self, key, modifiers):
        """Start the next level when the user presses Enter
        
        Arguments:
            key {int} -- Which key was pressed
            modifiers {int} -- What modifiers were active
        """
        if key == arcade.key.ENTER:
            # Reset the current level
            self.game_view.setup()
            self.window.show_view(self.game_view)

        elif key == arcade.key.ESCAPE:
            exit(0)


class PlatformerView(arcade.View):
    """PlatformerView class. Derived from arcade.View, provides all functionality
    from arcade.Window, plus managing different views for our game.
    """

    def __init__(self):
        # First initialize the parent
        super().__init__()

        # These lists will hold different sets of sprites
        self.coins_list = None
        self.background_list = None
        self.walls_list = None
        self.ladders_list = None
        self.goals_list = None
        self.enemies_list = None

        # One sprite for the player, no more is needed
        self.player = None

        # We need a physics engine as well
        self.physics_engine = None

        # Someplace to keep score
        self.score = 0

        # Which level are we on?
        self.level = 1

        # Load up our sounds here
        self.coin_sound = arcade.load_sound(
            path.join(assets_path, "sounds", "coin.wav")
        )
        self.jump_sound = arcade.load_sound(
            path.join(assets_path, "sounds", "jump.wav")
        )
        self.victory_sound = arcade.load_sound(
            path.join(assets_path, "sounds", "victory.wav")
        )

        # Track the bottom left corner of the current viewport
        self.view_left = 0
        self.view_bottom = 0

        # Check if a joystick is connected
        joysticks = arcade.get_joysticks()

        if joysticks:
            # If so, get the first one
            self.joystick = joysticks[0]
            self.joystick.open()
        else:
            # If not, flag it so we won't use it
            print("There are no Joysticks")
            self.joystick = None

        # Flag for entering view mode - allows super-user to skim around
        self.view_mode = False

    def setup(self):
        """Sets up the game for the current level
        """

        # Change directory to our assets path
        chdir(assets_path)

        # Get the current map based on the level
        map_name = f"platform_level_{self.level:02}.tmx"
        map_path = path.join(".", map_name)

        # What are the names of the layers?
        wall_layer = "ground"
        coin_layer = "coins"
        goal_layer = "goal"
        background_layer = "background"
        ladders_layer = "ladders"

        # Load the current map
        map = arcade.tilemap.read_tmx(map_path)

        self.coins_list = None
        self.background_list = None
        self.walls_list = None
        self.ladders_list = None
        self.goals_list = None

        # Load the layers
        self.background_list = arcade.tilemap.process_layer(
            map, background_layer, MAP_SCALING
        )
        self.goals_list = arcade.tilemap.process_layer(
            map, goal_layer, MAP_SCALING
        )
        self.walls_list = arcade.tilemap.process_layer(
            map, wall_layer, MAP_SCALING
        )
        self.ladders_list = arcade.tilemap.process_layer(
            map, ladders_layer, MAP_SCALING
        )
        self.coins_list = arcade.tilemap.process_layer(
            map, coin_layer, MAP_SCALING
        )

        # Process moving platforms
        moving_platforms_layer_name = "moving_platforms"
        moving_platforms_list = arcade.tilemap.process_layer(
            map, moving_platforms_layer_name, MAP_SCALING
        )
        for sprite in moving_platforms_list:
            self.walls_list.append(sprite)

        # Set the initial position of each moving platform to the left and/or bottom
        for moving_platform in moving_platforms_list:
            if "boundary_left" in moving_platform.properties:
                moving_platform.left = moving_platform.properties[
                    "boundary_left"
                ]
            if "boundary_bottom" in moving_platform.properties:
                moving_platform.bottom = moving_platform.properties[
                    "boundary_bottom"
                ]

        # Set the background color
        background_color = arcade.color.AERO_BLUE
        if map.background_color:
            background_color = map.background_color
        arcade.set_background_color(background_color)

        # Find the edge of the map to control viewport scrolling
        self.map_width = (map.map_size.width - 1) * map.tile_size.width

        # Create the player sprite, if they're not already setup
        if not self.player:
            self.player = self.create_player_sprite()

        # If we have a player sprite, we need to move it back to the beginning
        else:
            self.player.center_x = PLAYER_START_X
            self.player.center_y = PLAYER_START_Y

        # Setup our enemies
        self.enemies_list = None
        self.create_enemy_sprites()

        # Reset the viewport
        self.view_left = 0
        self.view_bottom = 0

        # Load the physics engine for this map
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, self.walls_list, GRAVITY, self.ladders_list
        )

    def create_enemy_sprites(self):
        """Creates enemy sprites appropriate for the current level
        """

        # No enemies on level 1
        if self.level == 2:
            self.enemies_list = arcade.SpriteList()
            self.enemies_list.append(Enemy(1464, 320))

    def create_player_sprite(self) -> arcade.AnimatedWalkingSprite:
        """Creates the animated player sprite
        
        Returns:
            arcade.AnimatedWalkingSprite -- The properly setup player sprite
        """
        # Where are the player images stored?
        texture_path = path.join(assets_path, "images", "player")

        # Setup the appropriate textures
        walking_paths = [
            path.join(texture_path, f"alienGreen_walk{x}.png") for x in (1, 2)
        ]
        climbing_paths = [
            path.join(texture_path, f"alienGreen_climb{x}.png") for x in (1, 2)
        ]
        standing_path = path.join(texture_path, "alienGreen_stand.png")

        # Load them all now
        walking_right_textures = [
            arcade.load_texture(texture)
            for texture in walking_paths
        ]
        walking_left_textures = [
            arcade.load_texture(
                texture, mirrored=True
            )
            for texture in walking_paths
        ]

        walking_up_textures = [
            arcade.load_texture(texture)
            for texture in climbing_paths
        ]
        walking_down_textures = [
            arcade.load_texture(texture)
            for texture in climbing_paths
        ]

        standing_right_textures = [
            arcade.load_texture(standing_path)
        ]

        standing_left_textures = [
            arcade.load_texture(
                standing_path, mirrored=True
            )
        ]

        # Create the sprite
        player = arcade.AnimatedWalkingSprite()

        # Add the proper textures
        player.stand_left_textures = standing_left_textures
        player.stand_right_textures = standing_right_textures
        player.walk_left_textures = walking_left_textures
        player.walk_right_textures = walking_right_textures
        player.walk_up_textures = walking_up_textures
        player.walk_down_textures = walking_down_textures

        # Set the player defaults
        player.center_x = PLAYER_START_X
        player.center_y = PLAYER_START_Y
        player.state = arcade.FACE_RIGHT
        player.lives = PLAYER_LIVES

        return player

    def on_key_press(self, key: int, modifiers: int):
        """Processes key presses
        
        Arguments:
            key {int} -- Which key was pressed
            modifiers {int} -- Which modifiers were down at the time
        """

        # Check for player left/right movement
        if key in [arcade.key.LEFT, arcade.key.J]:
            if self.view_mode:
                self.view_left -= 20
            else:
                self.player.change_x = -PLAYER_MOVE_SPEED
        elif key in [arcade.key.RIGHT, arcade.key.L]:
            if self.view_mode:
                self.view_left += 20
            else:
                self.player.change_x = PLAYER_MOVE_SPEED

        # Check if player can climb up or down
        elif key in [arcade.key.UP, arcade.key.I]:
            if self.view_mode:
                self.view_bottom += 20
            else:
                if self.physics_engine.is_on_ladder():
                    self.player.change_y = PLAYER_MOVE_SPEED
        elif key in [arcade.key.DOWN, arcade.key.K]:
            if self.view_mode:
                self.view_bottom -= 20
            else:
                if self.physics_engine.is_on_ladder():
                    self.player.change_y = -PLAYER_MOVE_SPEED

        # Check if we can jump
        elif key == arcade.key.SPACE:
            if self.physics_engine.can_jump():
                self.player.change_y = PLAYER_JUMP_SPEED
                # Play the jump sound
                arcade.play_sound(self.jump_sound)

        # Did the user want to pause?
        elif key == arcade.key.ESCAPE:
            # Pass the current view to preserve this view's state
            pause = PauseView(self)
            self.window.show_view(pause)

        # Shortcut to end the game
        elif key == arcade.key.Q:
            # Show the game over screen
            gameover = GameOverView(self)
            self.window.show_view(gameover)

        elif key == arcade.key.V:
            # Toggle view mode
            self.view_mode = not self.view_mode

            # Either save or restore the old view parameters
            if self.view_mode:
                # Just turned it on, save the view parameters
                self.save_view_bottom = self.view_bottom
                self.save_view_left = self.view_left
            else:
                self.view_bottom = self.save_view_bottom
                self.view_left = self.save_view_left

    def on_key_release(self, key: int, modifiers: int):
        """Processes key releases
        
        Arguments:
            key {int} -- The key which was released
            modifiers {int} -- Which modifiers were down at the time
        """

        # Check for player left/right movement
        if key in [
            arcade.key.LEFT,
            arcade.key.J,
            arcade.key.RIGHT,
            arcade.key.L,
        ]:
            self.player.change_x = 0

        # Check if player can climb up or down
        elif key in [
            arcade.key.UP,
            arcade.key.I,
            arcade.key.DOWN,
            arcade.key.K,
        ]:
            if self.physics_engine.is_on_ladder():
                self.player.change_y = 0

    def on_update(self, delta_time: float):
        """Updates the position of all screen objects
        
        Arguments:
            delta_time {float} -- How much time since the last call
        """

        # Are we in view mode? If so, update nothing, but skew the view
        if self.view_mode:
            # Scroll the viewport
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            # Do the scrolling
            arcade.set_viewport(
                self.view_left,
                SCREEN_WIDTH + self.view_left,
                self.view_bottom,
                SCREEN_HEIGHT + self.view_bottom,
            )
            return

        # First, check for joystick movement
        if self.joystick:
            # Check if we're in the dead zone
            if abs(self.joystick.x) > DEAD_ZONE:
                self.player.change_x = self.joystick.x * PLAYER_MOVE_SPEED
            else:
                self.player.change_x = 0

            if abs(self.joystick.y) > DEAD_ZONE:
                if self.physics_engine.is_on_ladder():
                    self.player.change_y = self.joystick.y * PLAYER_MOVE_SPEED
                else:
                    self.player.change_y = 0

            # Did the user press the jump button?
            if self.joystick.buttons[0]:
                if self.physics_engine.can_jump():
                    self.player.change_y = PLAYER_JUMP_SPEED
                    # Play the jump sound
                    arcade.play_sound(self.jump_sound)

        # Update the player animation
        self.player.update_animation(delta_time)

        # Update the animations for our map objects as well
        self.background_list.update_animation(delta_time)

        # Are there enemies? Update them as well
        if self.enemies_list:
            self.enemies_list.update_animation(delta_time)
            for enemy in self.enemies_list:
                enemy.center_x += enemy.change_x
                walls_hit = arcade.check_for_collision_with_list(
                    enemy, self.walls_list
                )
                if len(walls_hit) > 0:
                    enemy.change_x *= -1

        # Update player movement based on the physics engine
        self.physics_engine.update()

        # Restrict user movement so they can't walk off screen
        if self.player.left < 0:
            self.player.left = 0

        # Check if we've picked up a coin
        coins_hit = arcade.check_for_collision_with_list(
            self.player, self.coins_list
        )

        for coin in coins_hit:
            # Add the coin score to our score
            self.score += int(coin.properties["point_value"])

            # Play the coin sound
            arcade.play_sound(self.coin_sound)

            # Remove the coin
            coin.remove_from_sprite_lists()

        # Has Roz collided with an enemy?
        if self.enemies_list:
            enemies_hit = arcade.check_for_collision_with_list(
                self.player, self.enemies_list
            )

            if len(enemies_hit) > 0:
                game_over = GameOverView(self)
                self.window.show_view(game_over)

        # Now check if we're at the ending goal
        goals_hit = arcade.check_for_collision_with_list(
            self.player, self.goals_list
        )

        if len(goals_hit) > 0:
            # Switch to the victory view
            victory_view = VictoryView(self, self.victory_sound)
            self.window.show_view(victory_view)

        # Scroll the viewport if necessary
        self.scroll_viewport()

    def scroll_viewport(self):
        """Scrolls the viewport when the player gets close to the edges
        """

        # By default, don't change anything
        changed_viewport = False

        # Scroll left
        # Find the current left boundary
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN

        # Are we to the left of this boundary? Then we should scroll left
        if self.player.left < left_boundary:
            self.view_left -= left_boundary - self.player.left
            # But don't scroll past the left edge of the map
            if self.view_left < 0:
                self.view_left = 0
            else:
                changed_viewport = True

        # Scroll right
        # Find the current right boundary
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN

        # Are we right of this boundary? Then we should scroll right
        if self.player.right > right_boundary:
            self.view_left += self.player.right - right_boundary
            # Don't scroll past the right edge of the map
            if (
                self.view_left
                > self.map_width - SCREEN_WIDTH  # - RIGHT_VIEWPORT_MARGIN
            ):
                self.view_left = (
                    self.map_width - SCREEN_WIDTH  # - RIGHT_VIEWPORT_MARGIN
                )
            else:
                changed_viewport = True

        # Scroll up
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if self.player.top > top_boundary:
            self.view_bottom += self.player.top - top_boundary
            changed_viewport = True

        # Scroll down
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player.bottom
            changed_viewport = True

        if changed_viewport:
            # Only scroll to integers. Otherwise we end up with pixels that
            # don't line up on the screen
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            # Do the scrolling
            arcade.set_viewport(
                self.view_left,
                SCREEN_WIDTH + self.view_left,
                self.view_bottom,
                SCREEN_HEIGHT + self.view_bottom,
            )

    def on_draw(self):
        """Draws everything
        """

        arcade.start_render()

        # Draw all the sprites
        self.background_list.draw()
        self.walls_list.draw()
        self.coins_list.draw()
        self.goals_list.draw()
        self.ladders_list.draw()
        if self.enemies_list:
            self.enemies_list.draw()
        self.player.draw()

        # Draw the score in the lower left
        score_text = f"Score: {self.score}"

        # First a black background for a shadow effect
        arcade.draw_text(
            score_text,
            10 + self.view_left,
            10 + self.view_bottom,
            color=arcade.csscolor.BLACK,
            font_size=40,
        )
        # Now in white slightly shifted
        arcade.draw_text(
            score_text,
            15 + self.view_left,
            15 + self.view_bottom,
            color=arcade.csscolor.WHITE,
            font_size=40,
        )


# Main
if __name__ == "__main__":
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    title_view = TitleView()
    window.show_view(title_view)
    arcade.run()