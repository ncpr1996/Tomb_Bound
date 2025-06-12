import pygame
import random
import sys
import os
import json
import math
import audio_manager  # Import our custom audio manager

# Initialize pygame
pygame.init()
pygame.font.init()

# Initialize audio manager
audio = audio_manager.initialize()

# Import game components
from game_over_screen import GameOverScreen
from enhanced_title import EnhancedTitle

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 600
GROUND_HEIGHT = 560  # Further adjusted to ensure character and traps touch the ground
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
LIGHT_BLUE = (173, 216, 230)
LIGHT_GRAY = (200, 200, 200)
HIGHLIGHT_COLOR = (255, 215, 0)  # Gold color for highlighting
FPS = 60

# Set all text to use white color
TEXT_COLOR = WHITE
TEXT_SHADOW_COLOR = DARK_GRAY

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tomb Bound")
clock = pygame.time.Clock()

# Load fonts
try:
    title_font = pygame.font.Font(None, 60)  # Larger font for titles
    main_font = pygame.font.Font(None, 36)   # Main font for most text
    score_font = pygame.font.Font(None, 26)  # Smaller font for scores
except:
    # Fallback to system font if custom font loading fails
    title_font = pygame.font.SysFont('Arial', 60)
    main_font = pygame.font.SysFont('Arial', 36)
    score_font = pygame.font.SysFont('Arial', 26)

# Function to render text with border
def render_text_with_border(font, text, text_color, border_color):
    # Render the text in the main color
    text_surface = font.render(text, True, text_color)
    
    # Create a slightly larger surface for the border
    w, h = text_surface.get_size()
    border_surface = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
    
    # Render the border by drawing the text in border color at offset positions
    for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
        border_text = font.render(text, True, border_color)
        border_surface.blit(border_text, (1 + dx, 1 + dy))
    
    # Draw the main text on top
    border_surface.blit(text_surface, (1, 1))
    
    return border_surface

# Button class for menu navigation
class Button:
    def __init__(self, x, y, width, height, text, font=main_font, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.action = action
        self.hovered = False
        self.clicked = False
        self.active = True
        
        # Animation properties
        self.hover_scale = 1.0
        self.target_scale = 1.0
        self.scale_speed = 0.05
        
    def update(self, mouse_pos, mouse_clicked):
        # Store previous hover state
        prev_hovered = self.hovered
        
        # Check if mouse is over button
        self.hovered = self.rect.collidepoint(mouse_pos)
        
        # Handle hover animation
        if self.hovered:
            self.target_scale = 1.1  # Grow when hovered
        else:
            self.target_scale = 1.0  # Normal size when not hovered
            
        # Smoothly animate scale
        if self.hover_scale != self.target_scale:
            if self.hover_scale < self.target_scale:
                self.hover_scale = min(self.hover_scale + self.scale_speed, self.target_scale)
            else:
                self.hover_scale = max(self.hover_scale - self.scale_speed, self.target_scale)
        
        # Handle click
        if self.hovered and mouse_clicked and self.active:
            self.clicked = True
            # Play click sound from menu category
            audio.play_sound('click', 'menu')
            return True
        
        # Play hover sound when first hovering
        if self.hovered and not prev_hovered:
            audio.play_sound('hover', 'menu')
            
        self.clicked = False
        return False
        
    def draw(self, surface):
        # Calculate scaled dimensions
        scaled_width = int(self.rect.width * self.hover_scale)
        scaled_height = int(self.rect.height * self.hover_scale)
        
        # Calculate position to keep button centered during scaling
        x_offset = (scaled_width - self.rect.width) // 2
        y_offset = (scaled_height - self.rect.height) // 2
        
        # Draw button background with hover effect
        button_rect = pygame.Rect(
            self.rect.x - x_offset, 
            self.rect.y - y_offset, 
            scaled_width, 
            scaled_height
        )
        
        # Draw button with gradient effect
        if self.hovered:
            # Brighter gradient when hovered
            color_top = (80, 80, 120)
            color_bottom = (40, 40, 80)
        else:
            # Normal gradient
            color_top = (60, 60, 100)
            color_bottom = (30, 30, 60)
            
        # Draw gradient background
        for i in range(button_rect.height):
            progress = i / button_rect.height
            color = (
                int(color_top[0] * (1 - progress) + color_bottom[0] * progress),
                int(color_top[1] * (1 - progress) + color_bottom[1] * progress),
                int(color_top[2] * (1 - progress) + color_bottom[2] * progress)
            )
            pygame.draw.line(surface, color, 
                            (button_rect.left, button_rect.top + i),
                            (button_rect.right, button_rect.top + i))
        
        # Draw border (thicker when hovered)
        border_thickness = 3 if self.hovered else 2
        border_color = HIGHLIGHT_COLOR if self.hovered else GRAY
        pygame.draw.rect(surface, border_color, button_rect, border_thickness, border_radius=10)
        
        # Render text with border
        text_color = HIGHLIGHT_COLOR if self.hovered else TEXT_COLOR
        text_surf = render_text_with_border(self.font, self.text, text_color, BLACK)
        
        # Center text on button
        text_rect = text_surf.get_rect(center=button_rect.center)
        surface.blit(text_surf, text_rect)
        
    def set_text(self, new_text):
        self.text = new_text

# Toggle button for settings
class ToggleButton(Button):
    def __init__(self, x, y, width, height, text, font=main_font, action=None, state=False):
        super().__init__(x, y, width, height, text, font, action)
        self.state = state
        self.update_text()
        
    def update(self, mouse_pos, mouse_clicked):
        if super().update(mouse_pos, mouse_clicked):
            self.state = not self.state
            self.update_text()
            return True
        return False
        
    def update_text(self):
        status = "ON" if self.state else "OFF"
        self.text = f"{self.action}: {status}"
        
    def set_state(self, state):
        if self.state != state:
            self.state = state
            self.update_text()

# Slider for volume controls
class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, current_val, label):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.current_val = current_val
        self.label = label
        self.active = False
        self.hovered = False
        
        # Calculate handle position
        self.handle_width = 20
        self.handle_height = height + 10
        self.update_handle_pos()
        
    def update_handle_pos(self):
        # Calculate position based on current value
        value_range = self.max_val - self.min_val
        if value_range == 0:
            position = 0
        else:
            position = (self.current_val - self.min_val) / value_range
        
        handle_x = self.rect.x + int(position * self.rect.width) - self.handle_width // 2
        self.handle_rect = pygame.Rect(handle_x, self.rect.y - 5, self.handle_width, self.handle_height)
        
    def update(self, mouse_pos, mouse_pressed):
        prev_hovered = self.hovered
        self.hovered = self.handle_rect.collidepoint(mouse_pos) or self.rect.collidepoint(mouse_pos)
        
        # Play hover sound when first hovering
        if self.hovered and not prev_hovered:
            audio.play_sound('hover', 'menu')
        
        # Check for click on handle
        if mouse_pressed[0]:
            if self.handle_rect.collidepoint(mouse_pos) or self.active:
                self.active = True
            elif self.rect.collidepoint(mouse_pos):
                # Clicked directly on the slider bar
                self.set_value_from_mouse_x(mouse_pos[0])
                self.active = True
                # Play click sound
                audio.play_sound('click', 'menu')
        else:
            self.active = False
            
        # Update position if active
        if self.active:
            self.set_value_from_mouse_x(mouse_pos[0])
            
        return self.active
            
    def set_value_from_mouse_x(self, mouse_x):
        # Calculate value based on mouse position
        position = (mouse_x - self.rect.x) / self.rect.width
        position = max(0, min(1, position))  # Clamp between 0 and 1
        
        # Convert position to value
        old_val = self.current_val
        self.current_val = self.min_val + position * (self.max_val - self.min_val)
        
        # Update handle position
        self.update_handle_pos()
        
        # Return True if value changed significantly
        return abs(old_val - self.current_val) > 0.01
        
    def draw(self, surface):
        # Draw label above the slider with enough space
        label_text = f"{self.label}: {int(self.current_val * 100)}%"
        label_surf = render_text_with_border(main_font, label_text, TEXT_COLOR, BLACK)
        label_rect = label_surf.get_rect(midtop=(self.rect.centerx, self.rect.y - 40))
        surface.blit(label_surf, label_rect)
        
        # Draw slider background
        pygame.draw.rect(surface, DARK_GRAY, self.rect, border_radius=5)
        
        # Draw filled portion
        fill_width = int((self.current_val - self.min_val) / (self.max_val - self.min_val) * self.rect.width)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
        pygame.draw.rect(surface, LIGHT_BLUE, fill_rect, border_radius=5)
        
        # Draw handle
        handle_color = HIGHLIGHT_COLOR if self.hovered or self.active else WHITE
        pygame.draw.rect(surface, handle_color, self.handle_rect, border_radius=5)
        pygame.draw.rect(surface, BLACK, self.handle_rect, 2, border_radius=5)
        
    def set_value(self, value):
        self.current_val = max(self.min_val, min(self.max_val, value))
        self.update_handle_pos()

# Load background images with meaningful names
background_layers = {
    'sky': {'speed': 1.0, 'image': None},
    'wall': {'speed': 2.0, 'image': None},
    'background1': {'speed': 3.0, 'image': None},
    'background2': {'speed': 4.0, 'image': None},
    'pillar': {'speed': 6.0, 'image': None},
    'ground': {'speed': 8.0, 'image': None}  # Match ground speed with initial trap speed
}

# Load each background image
for layer_name in background_layers:
    try:
        img_path = os.path.join('backgrounds', f'{layer_name}.png')
        if os.path.exists(img_path):
            # For sky, use convert() instead of convert_alpha() to ensure no transparency
            if layer_name == 'sky':
                img = pygame.image.load(img_path).convert()
            else:
                img = pygame.image.load(img_path).convert_alpha()
                
            # Scale the image to fit the screen width while maintaining aspect ratio
            # Make images wider to prevent gaps
            aspect_ratio = img.get_width() / img.get_height()
            new_height = SCREEN_HEIGHT
            new_width = int(new_height * aspect_ratio * 1.5)  # Make 50% wider to prevent gaps
            img = pygame.transform.scale(img, (new_width, new_height))
            background_layers[layer_name]['image'] = img
            print(f"Loaded {layer_name} background")
        else:
            print(f"Background image not found: {img_path}")
    except pygame.error as e:
        print(f"Could not load background image {layer_name}.png: {e}")

# Background class for parallax scrolling
class Background:
    def __init__(self, image, speed):
        self.image = image
        self.speed = speed
        self.width = image.get_width()
        # Start with three copies to ensure full coverage
        self.positions = [0, self.width - 20, self.width * 2 - 40]  # Overlap by 20 pixels
    
    def update(self, game_speed):
        # Adjust speed based on current game speed to keep backgrounds in sync with traps
        actual_speed = self.speed * (game_speed / 8.0)
        
        # Move all copies of the background
        for i in range(len(self.positions)):
            self.positions[i] -= actual_speed
            
            # If an image is completely off screen to the left, move it to the right
            if self.positions[i] + self.width < 0:
                # Find the rightmost position
                rightmost = max(self.positions)
                # Place this image to the right of the rightmost one
                self.positions[i] = rightmost + self.width - 20  # Overlap by 20 pixels
    
    def draw(self, surface, offset_x=0, offset_y=0):
        # Draw all copies of the background
        for pos in self.positions:
            surface.blit(self.image, (pos + offset_x, offset_y))
        
        # Draw an extra copy if needed to fill any gaps at the right edge
        rightmost = max(self.positions)
        if rightmost < SCREEN_WIDTH:
            surface.blit(self.image, (rightmost + self.width - 20 + offset_x, offset_y))  # Overlap by 20 pixels

# Heart class for health display
class Heart(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Create heart shapes
        self.full_heart = pygame.Surface((30, 30), pygame.SRCALPHA)  # Larger hearts
        self.empty_heart = pygame.Surface((30, 30), pygame.SRCALPHA)
        
        # Draw a red heart shape
        pygame.draw.polygon(self.full_heart, (255, 0, 0), 
                           [(15, 9), (21, 3), (27, 9), (27, 15), (15, 27), (3, 15), (3, 9), (9, 3)])
        
        # Draw a gray heart outline
        pygame.draw.polygon(self.empty_heart, (100, 100, 100), 
                           [(15, 9), (21, 3), (27, 9), (27, 15), (15, 27), (3, 15), (3, 9), (9, 3)], 2)
        
        self.image = self.full_heart
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.is_full = True
    
    def update(self, is_full=None):
        if is_full is not None and is_full != self.is_full:
            self.is_full = is_full
            self.image = self.full_heart if is_full else self.empty_heart
# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        # Health system
        self.max_health = 3
        self.health = self.max_health
        self.is_hurt = False
        self.hurt_timer = 0
        self.hurt_duration = 30  # Frames to show hurt animation
        self.is_dead = False
        self.dead_timer = 0
        self.dead_duration = 240  # Significantly increased frames to show dead animation longer
        
        # Disintegration effect variables
        self.disintegrating = False
        self.disintegration_timer = 0
        self.disintegration_duration = 15  # Frames to show disintegration (0.25 seconds at 60 FPS)
        self.opacity = 255  # Full opacity to start
        
        # Animation variables
        self.current_frame = 0
        self.animation_speed = 0.08  # Faster animation speed for smoother transitions
        self.animation_timer = 0
        self.current_animation = 'idle'  # Current animation state
        
        # Jump mechanics
        self.velocity = 0
        self.jump_power = -22  # Enhanced jump power for easier gameplay
        self.gravity = 0.9  # Slightly reduced gravity for longer jumps
        self.is_jumping = False
        
        # Load player animations
        self.idle_frames = []
        self.run_frames = []
        self.jump_frames = []
        self.hurt_frames = []
        self.dead_frames = []
        
        # Function to split sprite sheets into frames
        def split_sprite_sheet(sheet_path, frame_count):
            frames = []
            try:
                # Load the sprite sheet
                sheet = pygame.image.load(sheet_path).convert_alpha()
                sheet_width = sheet.get_width()
                sheet_height = sheet.get_height()
                
                # Calculate frame width (total width divided by number of frames)
                frame_width = sheet_width // frame_count
                
                # Extract each frame
                for i in range(frame_count):
                    # Create a new surface for the frame
                    frame = pygame.Surface((frame_width, sheet_height), pygame.SRCALPHA)
                    # Copy the specific portion of the sprite sheet
                    frame.blit(sheet, (0, 0), (i * frame_width, 0, frame_width, sheet_height))
                    # Scale the frame to desired size (maintain aspect ratio)
                    scale_factor = 180 / frame_width  # Larger character size
                    new_width = 180
                    new_height = int(sheet_height * scale_factor)
                    frame = pygame.transform.scale(frame, (new_width, new_height))
                    frames.append(frame)
                
                print(f"Loaded {frame_count} frames from {sheet_path}")
            except pygame.error as e:
                print(f"Could not load animation from {sheet_path}: {e}")
            
            return frames
        
        # Load idle animation (6 frames)
        self.idle_frames = split_sprite_sheet(os.path.join('player', 'Idle.png'), 6)
        
        # Load run animation (8 frames)
        self.run_frames = split_sprite_sheet(os.path.join('player', 'Run.png'), 8)
        
        # Load jump animation (10 frames)
        self.jump_frames = split_sprite_sheet(os.path.join('player', 'Jump.png'), 10)
        
        # Load hurt animation (3 frames)
        self.hurt_frames = split_sprite_sheet(os.path.join('player', 'Hurt.png'), 3)
        
        # No Dead.png file, so use the last hurt frame for death
        self.dead_frames = []
        if self.hurt_frames:
            self.dead_frames = [self.hurt_frames[-1]]
        
        # Set initial image
        if self.idle_frames:
            self.image = self.idle_frames[0]
        elif self.run_frames:
            self.image = self.run_frames[0]
        else:
            # Fallback to rectangle if images couldn't be loaded
            self.image = pygame.Surface((40, 60))
            self.image.fill(BLACK)
        
        self.rect = self.image.get_rect()
        self.rect.bottom = GROUND_HEIGHT
        self.rect.left = 50
        
        # Animation variables
        self.current_frame = 0
        self.animation_speed = 0.15
        self.animation_timer = 0
        self.current_animation = 'idle'  # Current animation state
        
        # Jump mechanics
        self.velocity = 0
        self.jump_power = -15
        self.gravity = 0.8
        self.is_jumping = False
    
    def update(self):
        # Handle hurt state
        if self.is_hurt:
            self.hurt_timer += 1
            if self.hurt_timer >= self.hurt_duration:
                self.is_hurt = False
                self.hurt_timer = 0
            self.animate_hurt()
            return
        
        # Handle dead state
        if self.is_dead:
            # Call animate_dead which handles disintegration
            self.animate_dead()
            return
        
        # Apply gravity
        if self.is_jumping:
            self.velocity += self.gravity
            self.rect.y += self.velocity
            
            # Use jump animation
            self.animate_jump()
            
            # Check if landed
            if self.rect.bottom >= GROUND_HEIGHT:
                self.rect.bottom = GROUND_HEIGHT
                self.is_jumping = False
                self.velocity = 0
                self.current_frame = 0  # Reset animation frame
        else:
            # Make sure player is on the ground
            self.rect.bottom = GROUND_HEIGHT
            # Use run animation when not jumping
            self.animate_run()
    
    def update_start_screen(self):
        # Use idle animation for the start screen
        self.animate_idle()
    
    def animate_idle(self):
        if not self.idle_frames:
            return
            
        # Update animation frame
        self.animation_timer += 1
        if self.animation_timer >= FPS * self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.idle_frames)
            
            # Store the old rect position
            old_bottom = self.rect.bottom
            old_left = self.rect.left
            
            # Update image
            self.image = self.idle_frames[self.current_frame]
            
            # Reset the rect with the new image and restore position
            self.rect = self.image.get_rect()
            self.rect.bottom = old_bottom
            self.rect.left = old_left
    
    def animate_run(self):
        if not self.run_frames:
            return
            
        # Update animation frame at a consistent rate
        self.animation_timer += 1
        if self.animation_timer >= FPS * self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.run_frames)
            
            # Store the old rect position
            old_bottom = self.rect.bottom
            old_left = self.rect.left
            
            # Update image
            self.image = self.run_frames[self.current_frame]
            
            # Reset the rect with the new image and restore position
            self.rect = self.image.get_rect()
            self.rect.bottom = old_bottom
            self.rect.left = old_left
    
    def animate_jump(self):
        if not self.jump_frames:
            return
            
        # Store the old rect position
        old_bottom = self.rect.bottom
        old_left = self.rect.left
        
        # For jump animation, use different frames based on the jump phase
        # Going up: use first half of frames
        # Going down: use second half of frames
        if self.velocity < 0:  # Going up
            frame_index = min(int(abs(self.velocity) / 3), len(self.jump_frames) // 2 - 1)
        else:  # Going down
            frame_index = min(len(self.jump_frames) // 2 + int(self.velocity / 3), len(self.jump_frames) - 1)
        
        self.image = self.jump_frames[frame_index]
        
        # Reset the rect with the new image and restore position
        self.rect = self.image.get_rect()
        self.rect.bottom = old_bottom
        self.rect.left = old_left
    
    def animate_hurt(self):
        if not self.hurt_frames:
            return
            
        # Store the old rect position
        old_bottom = self.rect.bottom
        old_left = self.rect.left
        
        # Use a single frame for hurt animation to avoid the "5 people" issue
        # The hurt timer determines which frame to show
        if self.hurt_timer < self.hurt_duration / 3:
            frame_index = 0
        elif self.hurt_timer < 2 * self.hurt_duration / 3:
            frame_index = 1
        else:
            frame_index = 2
            
        self.image = self.hurt_frames[frame_index]
        
        # Reset the rect with the new image and restore position
        self.rect = self.image.get_rect()
        self.rect.bottom = old_bottom
        self.rect.left = old_left
    
    def animate_dead(self):
        # Use crumbling death effect if enabled
        if self.is_dead and hasattr(self, 'crumbling') and self.crumbling:
            if hasattr(self, 'crumbling_death'):
                # Update the crumbling death effect
                self.crumbling_death.update()
                
                # If crumbling animation is finished, remove player
                if self.crumbling_death.is_finished():
                    print("Player completely removed from game")
                    self.kill()  # Remove player from all sprite groups
                    self.image = None
                    return
        # Simple fade away effect
        elif self.is_dead and hasattr(self, 'disintegrating') and self.disintegrating:
            # Increment the timer
            self.disintegration_timer += 1
            
            # Calculate opacity based on timer (fade out quickly)
            self.opacity = max(0, 255 - (255 * self.disintegration_timer / self.disintegration_duration))
            
            # Apply fading effect to player sprite
            if self.hurt_frames:
                # Use the last hurt frame
                self.image = self.hurt_frames[-1].copy()
                # Apply fading
                self.image.set_alpha(int(self.opacity))
            
            # Position the character
            self.rect.bottom = GROUND_HEIGHT
            self.rect.left = 50
            
            # If disintegration is complete, make the player invisible
            if self.disintegration_timer >= self.disintegration_duration:
                print("Player completely removed from game")
                self.kill()  # Remove player from all sprite groups
                # Set image to None to ensure it's completely gone
                self.image = None
                return
        else:
            # Regular death animation (non-disintegrating)
            if not self.hurt_frames:
                return
                
            # Use the last hurt frame for death
            self.image = self.hurt_frames[-1]
            
            # Create a new rect for the position
            self.rect = self.image.get_rect()
            
            # Position the character
            self.rect.bottom = GROUND_HEIGHT
            self.rect.left = 50
    
    def jump(self):
        if not self.is_jumping and not self.is_hurt and not self.is_dead:
            self.is_jumping = True
            self.velocity = self.jump_power
            # Play jump sound from player category (or no sound if not available)
            audio.play_sound('jump', 'player')
    
    def take_damage(self):
        if not self.is_hurt and not self.is_dead:
            self.health -= 1
            self.is_hurt = True
            self.hurt_timer = 0
            
            # Check if player is dead
            if self.health <= 0:
                self.health = 0  # Ensure health doesn't go below zero
                self.is_dead = True
                self.dead_timer = 0
                
                # Start crumbling death effect instead of disintegration
                try:
                    from crumbling_death import CrumblingDeath
                    self.crumbling = True
                    self.crumbling_death = CrumblingDeath(pygame.display.get_surface(), self.rect, self.image)
                    print("Using crumbling death effect")
                except ImportError:
                    # Fallback to original disintegration effect
                    self.disintegrating = True
                    self.disintegration_timer = 0
                    self.opacity = 255  # Reset opacity to full
                    print("Crumbling death not available, using disintegration")
                except Exception as e:
                    # Fallback to original disintegration effect
                    self.disintegrating = True
                    self.disintegration_timer = 0
                    self.opacity = 255  # Reset opacity to full
                    print(f"Error initializing crumbling death: {e}")
                
                # Death sound is played in the collision handler
                return True  # Player died
            else:
                # Only play hurt sound if not dead
                audio.play_sound('hurt', 'game')
        
        return False  # Player still alive
# Particle effect for trap destruction
class DestroyEffect(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.particles = []
        self.timer = 0
        self.max_time = 30  # How long the effect lasts in frames
        
        # Create particles
        for _ in range(15):  # Number of particles
            # Random particle properties
            size = random.randint(3, 8)
            speed_x = random.uniform(-3, 3)
            speed_y = random.uniform(-6, -1)  # Negative for upward movement
            color = random.choice([(255, 100, 0), (255, 50, 0), (200, 0, 0)])  # Orange/red colors
            
            # Add particle [x, y, size, speed_x, speed_y, color, lifetime]
            lifetime = random.randint(15, self.max_time)
            self.particles.append([x, y, size, speed_x, speed_y, color, lifetime])
        
        # Create a rect for sprite management
        self.rect = pygame.Rect(x, y, 1, 1)
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
    
    def update(self):
        self.timer += 1
        if self.timer >= self.max_time:
            self.kill()
            return
        
        # Update each particle
        for particle in self.particles:
            # Apply gravity
            particle[4] += 0.2  # Increase y speed (gravity)
            
            # Move particle
            particle[0] += particle[3]  # x position
            particle[1] += particle[4]  # y position
            
            # Decrease lifetime
            particle[6] -= 1
    
    def draw(self, screen):
        # Draw each particle
        for particle in self.particles:
            if particle[6] > 0:  # If particle is still alive
                pygame.draw.circle(screen, particle[5], (int(particle[0]), int(particle[1])), particle[2])

# Trap class (obstacles)
class Trap(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        # Choose a random trap image from the available options
        trap_options = ['trap1.png', 'trap2.png', 'trap3.png']
        chosen_trap = random.choice(trap_options)
        
        # Try to load the trap image
        try:
            self.image = pygame.image.load(f'traps/{chosen_trap}').convert_alpha()
            
            # Scale the image to an appropriate size based on which trap it is (smaller than before)
            if chosen_trap == 'trap1.png':
                self.image = pygame.transform.scale(self.image, (90, 80))
            elif chosen_trap == 'trap2.png':
                self.image = pygame.transform.scale(self.image, (85, 75))
            else:  # trap3.png
                self.image = pygame.transform.scale(self.image, (80, 70))
                
        except pygame.error:
            # Fallback to a rectangle if image loading fails
            print(f"Could not load trap image {chosen_trap}. Using fallback.")
            self.image = pygame.Surface((60, 90))
            self.image.fill(BLACK)
        
        self.rect = self.image.get_rect()
        self.rect.bottom = GROUND_HEIGHT  # Ensure trap touches the ground
        self.rect.left = SCREEN_WIDTH
        
        # Add mild speed variation to each trap (±5% of base speed)
        speed_variation = random.uniform(0.95, 1.05)
        self.speed = speed * speed_variation
        
        # Store which trap type this is for collision detection
        self.trap_type = chosen_trap
        
        # Add subtle vertical bobbing motion
        self.bob_height = random.randint(0, 3)  # Reduced bobbing height
        self.bob_speed = random.uniform(0.03, 0.08)  # Slower bobbing
        self.bob_offset = random.uniform(0, 6.28)
        self.original_y = self.rect.y
        self.time = random.random() * 10
        
    def update(self):
        # Move the trap to the left
        self.rect.x -= self.speed
        
        # Apply subtle bobbing motion if enabled
        if self.bob_height > 0:
            self.time += self.bob_speed
            self.rect.y = self.original_y + math.sin(self.time + self.bob_offset) * self.bob_height
        
        # Remove if off screen
        if self.rect.right < 0:
            self.kill()
            
        # Always ensure trap is on the ground
        self.rect.bottom = GROUND_HEIGHT

# Settings manager to save/load game settings
class SettingsManager:
    def __init__(self):
        self.settings = {
            'sound_enabled': True,
            'music_enabled': True,  # Added music_enabled setting
            'music_volume': 0.5,
            'fullscreen': False,  # Ensure fullscreen is False by default
            'high_score': 0,
            'high_score_name': 'Unknown'
        }
        self.settings_file = 'game_settings.json'
        self.load_settings()
        
    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    # Update settings with loaded values
                    self.settings.update(loaded_settings)
                    print("Settings loaded successfully")
        except Exception as e:
            print(f"Error loading settings: {e}")
            
    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f)
                print("Settings saved successfully")
        except Exception as e:
            print(f"Error saving settings: {e}")
            
    def get(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)
        
    def set(self, key, value):
        """Set a setting value and save"""
        self.settings[key] = value
        self.save_settings()
        
    def update_high_score(self, score, name):
        """Update high score if the new score is higher"""
        if score > self.settings.get('high_score', 0):
            self.settings['high_score'] = score
            self.settings['high_score_name'] = name
            self.save_settings()
            return True
        return False
# Menu system for the game
class MenuSystem:
    def __init__(self, screen, settings_manager):
        self.screen = screen
        self.settings = settings_manager
        self.current_menu = 'main'  # 'main', 'settings', 'credits', 'name_input'
        self.player_name = ""
        self.input_active = True
        
        # Create enhanced title renderer
        try:
            from enhanced_title import EnhancedTitle
            self.title_renderer = EnhancedTitle(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
            print("Enhanced title renderer loaded successfully")
        except ImportError:
            print("Enhanced title module not found, using standard title")
            self.title_renderer = None
        except Exception as e:
            print(f"Error initializing enhanced title: {e}")
            self.title_renderer = None
        
        # Create backgrounds for menu
        self.backgrounds = []
        layer_order = ['sky', 'wall', 'background1', 'background2', 'pillar', 'ground']
        for layer_name in layer_order:
            if background_layers[layer_name]['image'] is not None:
                self.backgrounds.append(
                    Background(
                        background_layers[layer_name]['image'], 
                        background_layers[layer_name]['speed']
                    )
                )
        
        # Create buttons for main menu
        button_width = 250
        button_height = 60
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        button_spacing = 80
        
        # Main menu buttons
        self.main_menu_buttons = [
            Button(button_x, 200, button_width, button_height, "Start Game", action="start"),
            Button(button_x, 200 + button_spacing, button_width, button_height, "Settings", action="settings"),
            Button(button_x, 200 + button_spacing * 2, button_width, button_height, "Credits", action="credits"),
            Button(button_x, 200 + button_spacing * 3, button_width, button_height, "Quit Game", action="quit")
        ]
        
        # Settings menu controls
        self.settings_buttons = [
            ToggleButton(button_x, 200, button_width, button_height, "", action="Music", 
                        state=self.settings.get('music_enabled', True)),
            Button(button_x, 200 + button_spacing * 3, button_width, button_height, "Back", action="back")
        ]
        
        # Create slider for music volume
        self.music_slider = Slider(
            SCREEN_WIDTH // 2 - 150, 
            200 + button_spacing, 
            300, 
            20, 
            0.0, 
            1.0, 
            self.settings.get('music_volume', 0.5),
            "Music Volume"
        )
        
        # Credits menu button
        self.credits_buttons = [
            Button(button_x, SCREEN_HEIGHT - 100, button_width, button_height, "Back", action="back")
        ]
        
        # Name input box
        self.name_input_box = pygame.Rect(SCREEN_WIDTH // 2 - 150, 250, 300, 50)
        self.name_confirm_button = Button(
            SCREEN_WIDTH // 2 - button_width // 2,
            350,
            button_width,
            button_height,
            "Confirm",
            action="confirm_name"
        )
    
    def update(self, events):
        """Update menu state based on events"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        key_pressed = None
        
        # Process events
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True
            elif event.type == pygame.KEYDOWN:
                key_pressed = event.key
                
                # Handle keyboard navigation
                if self.current_menu == 'main':
                    if event.key == pygame.K_UP:
                        self.navigate_buttons(self.main_menu_buttons, -1)
                    elif event.key == pygame.K_DOWN:
                        self.navigate_buttons(self.main_menu_buttons, 1)
                    elif event.key == pygame.K_RETURN:
                        self.activate_focused_button(self.main_menu_buttons)
                    # Number key shortcuts
                    elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                        index = event.key - pygame.K_1
                        if 0 <= index < len(self.main_menu_buttons):
                            return self.handle_button_action(self.main_menu_buttons[index].action)
                
                # Handle name input
                if self.current_menu == 'name_input' and self.input_active:
                    if event.key == pygame.K_RETURN and self.player_name.strip():
                        return self.handle_button_action('confirm_name')
                    elif event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    elif len(self.player_name) < 15:  # Limit name length
                        if event.unicode.isalnum() or event.unicode.isspace():
                            self.player_name += event.unicode
        
        # Update backgrounds (slow movement for menu)
        for bg in self.backgrounds:
            bg.update(1.0)
        
        # Update menu based on current state
        if self.current_menu == 'main':
            return self.update_main_menu(mouse_pos, mouse_clicked)
        elif self.current_menu == 'settings':
            return self.update_settings_menu(mouse_pos, mouse_clicked)
        elif self.current_menu == 'credits':
            return self.update_credits_menu(mouse_pos, mouse_clicked)
        elif self.current_menu == 'name_input':
            return self.update_name_input(mouse_pos, mouse_clicked)
    
    def navigate_buttons(self, buttons, direction):
        """Navigate buttons with keyboard"""
        # Find currently focused button
        focused_index = -1
        for i, button in enumerate(buttons):
            if button.hovered:
                focused_index = i
                break
        
        # If no button is focused, focus the first one
        if focused_index == -1:
            if direction > 0:
                focused_index = 0
            else:
                focused_index = len(buttons) - 1
        else:
            # Move focus
            focused_index = (focused_index + direction) % len(buttons)
        
        # Update button hover states
        for i, button in enumerate(buttons):
            button.hovered = (i == focused_index)
        
        # Play hover sound from menu category
        audio.play_sound('hover', 'menu')
    
    def activate_focused_button(self, buttons):
        """Activate the currently focused button"""
        for button in buttons:
            if button.hovered:
                return self.handle_button_action(button.action)
    
    def update_main_menu(self, mouse_pos, mouse_clicked):
        """Update main menu state"""
        for button in self.main_menu_buttons:
            if button.update(mouse_pos, mouse_clicked):
                return self.handle_button_action(button.action)
        return None
    
    def update_settings_menu(self, mouse_pos, mouse_clicked):
        """Update settings menu state"""
        # Update music toggle button
        if self.settings_buttons[0].update(mouse_pos, mouse_clicked):
            # Toggle music
            audio.toggle_music()
            self.settings_buttons[0].set_state(audio.music_enabled)
            self.settings.set('music_enabled', audio.music_enabled)
        
        # Update music volume slider
        mouse_pressed = pygame.mouse.get_pressed()
        if self.music_slider.update(mouse_pos, mouse_pressed):
            # Update music volume
            audio.set_music_volume(self.music_slider.current_val)
            self.settings.set('music_volume', self.music_slider.current_val)
        
        # Update back button
        if self.settings_buttons[1].update(mouse_pos, mouse_clicked):
            return self.handle_button_action('back')
            
        return None
    
    def update_credits_menu(self, mouse_pos, mouse_clicked):
        """Update credits menu state"""
        # Update scroll position if not already initialized
        if not hasattr(self, 'credits_scroll_pos'):
            self.credits_scroll_pos = SCREEN_HEIGHT
            self.credits_scroll_speed = 2
        
        for button in self.credits_buttons:
            if button.update(mouse_pos, mouse_clicked):
                return self.handle_button_action(button.action)
        return None
    
    def update_name_input(self, mouse_pos, mouse_clicked):
        """Update name input screen"""
        # Check for click on input box
        if mouse_clicked:
            self.input_active = self.name_input_box.collidepoint(mouse_pos)
        
        # Update confirm button
        if self.name_confirm_button.update(mouse_pos, mouse_clicked) and self.player_name.strip():
            return self.handle_button_action('confirm_name')
            
        return None
    
    def handle_button_action(self, action):
        """Handle button actions"""
        if action == 'start':
            # Go to name input screen
            self.current_menu = 'name_input'
        elif action == 'settings':
            # Go to settings menu
            self.current_menu = 'settings'
        elif action == 'credits':
            # Go to credits screen
            self.current_menu = 'credits'
        elif action == 'quit':
            # Quit game
            return 'quit'
        elif action == 'back':
            # Go back to main menu
            self.current_menu = 'main'
        elif action == 'confirm_name':
            # Start game with entered name
            if self.player_name.strip():
                return {'action': 'start_game', 'player_name': self.player_name}
        
        return None
    
    def draw(self):
        """Draw the current menu"""
        # Draw backgrounds
        for bg in self.backgrounds:
            bg.draw(self.screen)
        
        # Draw menu content based on current state
        if self.current_menu == 'main':
            self.draw_main_menu()
        elif self.current_menu == 'settings':
            self.draw_settings_menu()
        elif self.current_menu == 'credits':
            self.draw_credits_menu()
        elif self.current_menu == 'name_input':
            self.draw_name_input()
    
    def draw_main_menu(self):
        """Draw main menu"""
        # Draw enhanced game title using the title renderer
        if hasattr(self, 'title_renderer'):
            self.title_renderer.update()
            self.title_renderer.draw()
        else:
            # Fallback to simple title if renderer not available
            title_text = render_text_with_border(title_font, "TOMB BOUND", HIGHLIGHT_COLOR, BLACK)
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 80))
        
        # Draw buttons
        for button in self.main_menu_buttons:
            button.draw(self.screen)
        
        # Draw high score
        high_score = self.settings.get('high_score', 0) // 10
        high_score_name = self.settings.get('high_score_name', 'Unknown')
        if high_score > 0:
            high_score_text = render_text_with_border(
                score_font, 
                f"High Score: {high_score:04d} by {high_score_name}", 
                TEXT_COLOR, 
                BLACK
            )
            self.screen.blit(high_score_text, 
                           (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, SCREEN_HEIGHT - 50))
    
    def draw_settings_menu(self):
        """Draw settings menu with centered layout and proper alignment"""
        # Draw title
        title_text = render_text_with_border(title_font, "SETTINGS", TEXT_COLOR, BLACK)
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 80))
        
        # Calculate positions for centered layout
        center_x = SCREEN_WIDTH // 2
        button_width = 250
        control_spacing = 120  # Increased spacing between controls
        current_y = 180
        
        # Sound Settings Section
        section_title = render_text_with_border(main_font, "Audio Settings", HIGHLIGHT_COLOR, BLACK)
        self.screen.blit(section_title, (center_x - section_title.get_width() // 2, current_y))
        current_y += 60  # Spacing after section title
        
        # Draw music toggle
        self.settings_buttons[0].rect.x = center_x - button_width // 2
        self.settings_buttons[0].rect.y = current_y
        self.settings_buttons[0].draw(self.screen)
        current_y += control_spacing
        
        # Draw music volume slider
        slider_width = 300
        self.music_slider.rect.x = center_x - slider_width // 2
        self.music_slider.rect.y = current_y
        self.music_slider.draw(self.screen)
        
        # Draw back button at the bottom with enough space
        back_button_y = SCREEN_HEIGHT - 100
        self.settings_buttons[1].rect.x = center_x - button_width // 2
        self.settings_buttons[1].rect.y = back_button_y
        self.settings_buttons[1].draw(self.screen)
    
    def draw_credits_menu(self):
        """Draw credits screen with automatic scrolling animation"""
        # Draw title
        title_text = render_text_with_border(title_font, "CREDITS", TEXT_COLOR, BLACK)
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 80))
        
        # Initialize scroll position if not already set
        if not hasattr(self, 'credits_scroll_pos'):
            self.credits_scroll_pos = SCREEN_HEIGHT  # Start from bottom
            self.credits_scroll_speed = 2  # Pixels per frame - match pause menu speed
        
        # Updated credits content
        credits = [
            ["Tomb Bound", HIGHLIGHT_COLOR, title_font],
            ["", WHITE, main_font],  # Empty line for spacing
            ["Developer", HIGHLIGHT_COLOR, main_font],
            ["N Chandra Prakash Reddy", WHITE, main_font],
            ["Tirupati, Andhra Pradesh, India", WHITE, main_font],
            ["", WHITE, main_font],  # Empty line for spacing
            ["Programming Language", HIGHLIGHT_COLOR, main_font],
            ["Python 3", WHITE, main_font],
            ["", WHITE, main_font],  # Empty line for spacing
            ["Game Library", HIGHLIGHT_COLOR, main_font],
            ["Pygame", WHITE, main_font],
            ["", WHITE, main_font],  # Empty line for spacing
            ["Development Tool", HIGHLIGHT_COLOR, main_font],
            ["Amazon Q Developer", WHITE, main_font],
            ["", WHITE, main_font],  # Empty line for spacing
            ["2D Assets", HIGHLIGHT_COLOR, main_font],
            ["Craftpix", WHITE, main_font],
            ["", WHITE, main_font],  # Empty line for spacing
            ["Music and Sound Effects", HIGHLIGHT_COLOR, main_font],
            ["Pixabay", WHITE, main_font],
            ["", WHITE, main_font],  # Empty line for spacing
            ["Thank you for playing this game!", HIGHLIGHT_COLOR, main_font]
        ]
        
        # Calculate total height of credits
        line_spacing = 40
        total_height = len(credits) * line_spacing
        
        # Update scroll position
        self.credits_scroll_pos -= self.credits_scroll_speed
        
        # Reset position if credits have scrolled completely off screen
        if self.credits_scroll_pos < -total_height:
            self.credits_scroll_pos = SCREEN_HEIGHT
        
        # Create a clipping area to prevent text from appearing behind the back button
        button_area_height = 100  # Height of the area reserved for the back button
        
        # Draw scrolling credits
        y_pos = self.credits_scroll_pos
        
        for line in credits:
            text, color, font = line
            if text:  # Skip empty strings in y position calculation
                text_surf = render_text_with_border(font, text, color, BLACK)
                # Only draw if within visible area and not overlapping with button area
                if 120 < y_pos < SCREEN_HEIGHT - button_area_height:
                    self.screen.blit(text_surf, (SCREEN_WIDTH // 2 - text_surf.get_width() // 2, y_pos))
            y_pos += line_spacing
        
        # Draw back button (fixed position)
        for button in self.credits_buttons:
            button.rect.y = SCREEN_HEIGHT - 80
            button.draw(self.screen)
    
    def draw_name_input(self):
        """Draw name input screen"""
        # Draw title
        title_text = render_text_with_border(title_font, "ENTER YOUR NAME", TEXT_COLOR, BLACK)
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 80))
        
        # Draw input box
        color = HIGHLIGHT_COLOR if self.input_active else LIGHT_GRAY
        pygame.draw.rect(self.screen, DARK_GRAY, self.name_input_box, border_radius=5)
        pygame.draw.rect(self.screen, color, self.name_input_box, 3, border_radius=5)
        
        # Draw current name
        name_text = render_text_with_border(main_font, self.player_name, TEXT_COLOR, BLACK)
        self.screen.blit(name_text, (self.name_input_box.x + 10, self.name_input_box.y + 10))
        
        # Draw blinking cursor if input is active
        if self.input_active and pygame.time.get_ticks() % 1000 < 500:
            cursor_x = self.name_input_box.x + 10 + name_text.get_width()
            pygame.draw.line(self.screen, TEXT_COLOR, 
                           (cursor_x, self.name_input_box.y + 10),
                           (cursor_x, self.name_input_box.y + 40), 2)
        
        # Draw confirm button
        self.name_confirm_button.draw(self.screen)
        
        # Draw instruction
        instruction_text = render_text_with_border(
            score_font, 
            "Enter your name and press Confirm to start", 
            TEXT_COLOR, 
            BLACK
        )
        self.screen.blit(instruction_text, 
                       (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, 420))
# Game class
class Game:
    def __init__(self):
        # Initialize settings manager
        self.settings_manager = SettingsManager()
        
        # Initialize menu system
        self.menu_system = MenuSystem(screen, self.settings_manager)
        
        # Apply saved settings
        audio.set_music_volume(self.settings_manager.get('music_volume', 0.5))
        audio.sound_enabled = True  # Always enable sound effects
        audio.music_enabled = self.settings_manager.get('music_enabled', True)
        
        # Always use windowed mode
        pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Game state
        self.game_state = 'menu'  # 'menu', 'playing', 'paused', 'game_over'
        self.paused = False
        self.pause_menu_state = 'main'  # 'main', 'settings', 'credits'
        self.player = Player()
        self.all_sprites = pygame.sprite.Group()
        self.traps = pygame.sprite.Group()
        self.hearts = pygame.sprite.Group()
        self.effects = pygame.sprite.Group()  # Group for visual effects
        self.all_sprites.add(self.player)
        
        # Screen shake effect
        self.screen_shake_amount = 0
        self.screen_shake_duration = 0
        self.screen_shake_decay = 0.9
        
        # Create pause menu buttons
        button_width = 250
        button_height = 60
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        button_spacing = 70
        
        self.pause_buttons = {
            'main': [
                Button(button_x, 200, button_width, button_height, "Resume Game", action="resume"),
                Button(button_x, 200 + button_spacing, button_width, button_height, "Settings", action="settings"),
                Button(button_x, 200 + button_spacing * 2, button_width, button_height, "Credits", action="credits"),
                Button(button_x, 200 + button_spacing * 3, button_width, button_height, "Quit Game", action="quit")
            ],
            'settings': [
                Button(button_x, SCREEN_HEIGHT - 100, button_width, button_height, "Back", action="back")
            ],
            'credits': [
                Button(button_x, SCREEN_HEIGHT - 100, button_width, button_height, "Back", action="back")
            ]
        }
        
        # Create slider for music volume in pause menu
        self.pause_music_slider = Slider(
            SCREEN_WIDTH // 2 - 150, 
            250, 
            300, 
            20, 
            0.0, 
            1.0, 
            self.settings_manager.get('music_volume', 0.5),
            "Music Volume"
        )
        
        # Create toggle for music in pause menu
        self.pause_music_toggle = ToggleButton(
            button_x, 
            180, 
            button_width, 
            button_height, 
            "", 
            action="Music",
            state=self.settings_manager.get('music_enabled', True)
        )
        
        # Create hearts for health display
        for i in range(self.player.max_health):
            heart = Heart(SCREEN_WIDTH - 50 - (i * 35), 40)  # Adjusted position to be below player name
            self.hearts.add(heart)
            self.all_sprites.add(heart)
        
        self.speed = 5  # Initial speed (slower to start)
        self.score = 0
        self.high_score = self.settings_manager.get('high_score', 0)
        self.player_name = ""  # Player name will be entered at start
        self.high_score_name = self.settings_manager.get('high_score_name', 'Unknown')
        self.game_over = False
        self.show_game_over = False  # Flag to control when to show game over screen
        self.spawn_timer = 0
        
        # Credits scrolling variables for pause menu
        self.pause_credits_scroll_pos = SCREEN_HEIGHT  # Start from bottom
        self.pause_credits_scroll_speed = 2  # Pixels per frame - increased to match main menu
        
        # Enhanced game over screen
        try:
            from game_over_screen import GameOverScreen
            self.game_over_screen = None  # Will be initialized when game over occurs
            self.has_game_over_screen = True
            print("Enhanced game over screen loaded successfully")
        except ImportError:
            print("Enhanced game over screen module not found, using standard game over screen")
            self.has_game_over_screen = False
        except Exception as e:
            print(f"Error initializing enhanced game over screen: {e}")
            self.has_game_over_screen = False
        
        # Create parallax backgrounds with different speeds
        self.backgrounds = []
        
        # Create backgrounds in the correct order (from back to front)
        layer_order = ['sky', 'wall', 'background1', 'background2', 'pillar', 'ground']
        for layer_name in layer_order:
            if background_layers[layer_name]['image'] is not None:
                self.backgrounds.append(
                    Background(
                        background_layers[layer_name]['image'], 
                        background_layers[layer_name]['speed']
                    )
                )
    
    def reset_game(self):
        """Reset the game state without changing player name"""
        # Keep the player name
        player_name = self.player_name
        
        # Reset game objects
        self.player = Player()
        self.all_sprites = pygame.sprite.Group()
        self.traps = pygame.sprite.Group()
        self.hearts = pygame.sprite.Group()
        self.effects = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        
        # Create hearts for health display
        for i in range(self.player.max_health):
            heart = Heart(SCREEN_WIDTH - 50 - (i * 35), 40)
            self.hearts.add(heart)
            self.all_sprites.add(heart)
        
        # Reset game variables
        self.speed = 4  # Reduced initial speed for easier start
        self.score = 0
        self.game_over = False
        self.show_game_over = False
        self.spawn_timer = 0
        
        # Restore player name
        self.player_name = player_name
        
        # Set game state to playing
        self.game_state = 'playing'
        
        # Start playing background music
        audio.play_music()
    
    def start_game(self, player_name):
        """Start a new game with the given player name"""
        self.player_name = player_name
        self.reset_game()
    
    def update_pause_menu(self, events):
        """Handle pause menu interactions"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True
        
        # Handle current pause menu state
        if self.pause_menu_state == 'main':
            # Update main pause menu buttons
            for button in self.pause_buttons['main']:
                if button.update(mouse_pos, mouse_clicked):
                    self.handle_pause_button_action(button.action)
        
        elif self.pause_menu_state == 'settings':
            # Update settings buttons
            for button in self.pause_buttons['settings']:
                if button.update(mouse_pos, mouse_clicked):
                    self.handle_pause_button_action(button.action)
            
            # Update music toggle
            if self.pause_music_toggle.update(mouse_pos, mouse_clicked):
                audio.toggle_music()
                self.settings_manager.set('music_enabled', audio.music_enabled)
            
            # Update music volume slider
            mouse_pressed = pygame.mouse.get_pressed()
            if self.pause_music_slider.update(mouse_pos, mouse_pressed):
                audio.set_music_volume(self.pause_music_slider.current_val)
                self.settings_manager.set('music_volume', self.pause_music_slider.current_val)
        
        elif self.pause_menu_state == 'credits':
            # Update credits buttons
            for button in self.pause_buttons['credits']:
                if button.update(mouse_pos, mouse_clicked):
                    self.handle_pause_button_action(button.action)
                    
            # Reset scroll position if we're leaving credits
            if mouse_clicked and any(button.rect.collidepoint(mouse_pos) for button in self.pause_buttons['credits']):
                self.pause_credits_scroll_pos = SCREEN_HEIGHT
    
    def handle_pause_button_action(self, action):
        """Handle pause menu button actions"""
        if action == 'resume':
            self.game_state = 'playing'
            audio.unpause_music()
        elif action == 'settings':
            self.pause_menu_state = 'settings'
        elif action == 'credits':
            self.pause_menu_state = 'credits'
            # Reset credits scroll position when entering credits
            self.pause_credits_scroll_pos = SCREEN_HEIGHT
        elif action == 'quit':
            self.game_state = 'menu'
            self.menu_system = MenuSystem(screen, self.settings_manager)
        elif action == 'back':
            self.pause_menu_state = 'main'
    def run(self):
        # Start playing background music
        audio.play_music()
        
        # Main game loop
        running = True
        while running:
            # Process events
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    # Handle ESC key for pause menu
                    if event.key == pygame.K_ESCAPE and self.game_state == 'playing':
                        self.game_state = 'paused'
                        self.pause_menu_state = 'main'
                        audio.pause_music()
                    elif event.key == pygame.K_ESCAPE and self.game_state == 'paused':
                        self.game_state = 'playing'
                        audio.unpause_music()
                
                if self.game_state == 'playing':
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE and not self.game_over:
                            self.player.jump()
                        if event.key == pygame.K_r and self.game_over:
                            # Reset game without going to start screen
                            self.reset_game()
                        elif event.key == pygame.K_m and self.game_over:
                            # Return to main menu
                            self.game_state = 'menu'
                            # Restart the music instead of stopping it
                            audio.play_music()
                            self.menu_system = MenuSystem(screen, self.settings_manager)
                        # Audio controls - only apply when not in game over state
                        elif event.key == pygame.K_m and not self.game_over:
                            # Toggle music
                            audio.toggle_music()
                            self.settings_manager.set('music_enabled', audio.music_enabled)
                        if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                            # Increase music volume
                            audio.set_music_volume(audio.music_volume + 0.1)
                            self.settings_manager.set('music_volume', audio.music_volume)
                        if event.key == pygame.K_MINUS:
                            # Decrease music volume
                            audio.set_music_volume(audio.music_volume - 0.1)
                            self.settings_manager.set('music_volume', audio.music_volume)
                    
                    # Handle delayed game over sound and screen
                    if event.type == pygame.USEREVENT and self.game_over:
                        # After red screen effect, play game over sound
                        audio.play_sound('game_over', 'game')
                        pygame.time.set_timer(pygame.USEREVENT, 0)  # Cancel the timer
                    
                    # Handle delayed game over screen display
                    if event.type == pygame.USEREVENT + 1 and self.game_over:
                        self.show_game_over = True
                        pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # Cancel the timer
            
            # Update game state
            if self.game_state == 'menu':
                # Update menu system
                result = self.menu_system.update(events)
                
                # Handle menu actions
                if result == 'quit':
                    running = False
                elif result and isinstance(result, dict) and result['action'] == 'start_game':
                    self.start_game(result['player_name'])
            
            elif self.game_state == 'playing':
                if not self.game_over:
                    self.update_game()
                else:
                    # Game over - make sure all hearts are empty
                    for heart in self.hearts:
                        heart.update(False)
            
            elif self.game_state == 'paused':
                # Handle pause menu
                self.update_pause_menu(events)
            
            # Draw everything
            self.draw()
            
            # Cap the frame rate
            clock.tick(FPS)
        
        # Save settings before quitting
        self.settings_manager.save_settings()
        pygame.quit()
        sys.exit()
    
    def update_game(self):
        """Update game state during gameplay"""
        # Update screen shake
        if self.screen_shake_duration > 0:
            self.screen_shake_duration -= 1
            if self.screen_shake_duration <= 0:
                self.screen_shake_amount = 0
            else:
                self.screen_shake_amount *= self.screen_shake_decay
        
        # Update backgrounds
        for bg in self.backgrounds:
            bg.update(self.speed)  # Pass current game speed to backgrounds
        
        # Update sprites
        self.all_sprites.update()
        
        # Update effects
        self.effects.update()
        
        # Update hearts based on player health
        for i, heart in enumerate(self.hearts):
            heart.update(i < self.player.health)
        
        # Spawn traps with randomized timing and spacing
        self.spawn_timer += 1
        
        # More balanced spawn intervals
        base_interval = max(140 - (self.score // 1000), 90)  # Slower progression, higher minimum
        
        # Moderate randomness that doesn't make the game too unpredictable
        variation = random.randint(-20, 40)  # Asymmetric to favor longer gaps
        
        # Occasionally add a longer gap to give players a breather
        if random.random() < 0.25:  # 25% chance (increased from 15%)
            variation += random.randint(60, 100)  # Longer breathing room
            
        spawn_interval = base_interval + variation
        
        # Ensure minimum interval isn't too short
        spawn_interval = max(spawn_interval, 70)  # Higher minimum interval
        
        if self.spawn_timer > spawn_interval:
            # Check if there's enough distance from the last trap
            can_spawn = True
            
            # Ensure enough space between traps for comfortable jumping
            min_distance = 350 + (self.speed - 8) * 15  # Significantly increased minimum distance
            
            # Check all existing traps to ensure proper spacing
            for trap in self.traps:
                # Don't spawn if any trap is too close to the right edge
                if trap.rect.x > SCREEN_WIDTH - min_distance:
                    can_spawn = False
                    break
            
            # Only spawn if there's enough space
            if can_spawn:
                self.spawn_trap()
                # Reset timer with moderate randomness
                self.spawn_timer = random.randint(0, 15)
        
        # Check collisions
        # Create a smaller hitbox for the player for more accurate collisions
        player_hitbox = pygame.Rect(
            self.player.rect.x + self.player.rect.width * 0.3,
            self.player.rect.y + self.player.rect.height * 0.2,
            self.player.rect.width * 0.4,
            self.player.rect.height * 0.7
        )
        
        for trap in self.traps:
            # Create a custom hitbox for each trap type
            if hasattr(trap, 'trap_type'):
                if trap.trap_type == 'trap1.png':
                    trap_hitbox = pygame.Rect(
                        trap.rect.x + trap.rect.width * 0.35,
                        trap.rect.y + trap.rect.height * 0.2,
                        trap.rect.width * 0.3,
                        trap.rect.height * 0.7
                    )
                elif trap.trap_type == 'trap2.png':
                    trap_hitbox = pygame.Rect(
                        trap.rect.x + trap.rect.width * 0.3,
                        trap.rect.y + trap.rect.height * 0.25,
                        trap.rect.width * 0.4,
                        trap.rect.height * 0.6
                    )
                elif trap.trap_type == 'trap3.png':
                    trap_hitbox = pygame.Rect(
                        trap.rect.x + trap.rect.width * 0.25,
                        trap.rect.y + trap.rect.height * 0.3,
                        trap.rect.width * 0.5,
                        trap.rect.height * 0.5
                    )
                else:
                    # Default hitbox for other trap types
                    trap_hitbox = pygame.Rect(
                        trap.rect.x + trap.rect.width * 0.2,
                        trap.rect.y + trap.rect.height * 0.25,
                        trap.rect.width * 0.6,
                        trap.rect.height * 0.6
                    )
            else:
                # Default hitbox if trap_type is not available
                trap_hitbox = pygame.Rect(
                    trap.rect.x + trap.rect.width * 0.25,
                    trap.rect.y + trap.rect.height * 0.25,
                    trap.rect.width * 0.5,
                    trap.rect.height * 0.5
                )
            
            # Use a more precise collision detection
            if player_hitbox.colliderect(trap_hitbox):
                # Calculate the actual overlap area
                overlap_width = min(player_hitbox.right, trap_hitbox.right) - max(player_hitbox.left, trap_hitbox.left)
                overlap_height = min(player_hitbox.bottom, trap_hitbox.bottom) - max(player_hitbox.top, trap_hitbox.top)
                overlap_area = overlap_width * overlap_height
                
                # Only count as collision if overlap area is significant
                if overlap_area > 50:  # Minimum overlap threshold
                    # Create destruction effect at trap position
                    effect = DestroyEffect(trap.rect.centerx, trap.rect.centery)
                    self.effects.add(effect)
                    
                    # Player takes damage
                    if self.player.take_damage():
                        # Player died
                        self.game_over = True
                        # Make sure all hearts are empty
                        for heart in self.hearts:
                            heart.update(False)
                        audio.pause_music()  # Pause background music
                        
                        # Play death sound only (not hurt sound)
                        audio.play_sound('death', 'game')
                        
                        # Initialize enhanced game over screen if available
                        if self.has_game_over_screen:
                            from game_over_screen import GameOverScreen
                            self.game_over_screen = GameOverScreen(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
                        
                        # Apply screen shake for dramatic effect
                        self.screen_shake_amount = 10
                        self.screen_shake_duration = 30  # frames
                        
                        # Show red overlay immediately for game over
                        red_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                        red_overlay.fill((255, 0, 0, 150))  # Brighter red with more opacity
                        screen.blit(red_overlay, (0, 0))
                        pygame.display.flip()  # Update the display immediately to show red flash
                        
                        # First timer for red screen effect
                        pygame.time.set_timer(pygame.USEREVENT, 500)  # 0.5 second delay with red screen
                        
                        # Second timer for game over screen
                        pygame.time.set_timer(pygame.USEREVENT + 1, 1000)  # 1 second delay for game over screen
                        
                        # Update high score if needed
                        self.settings_manager.update_high_score(self.score, self.player_name)
                    else:
                        # Player hurt but not dead
                        audio.play_sound('hurt')
                    
                    # Always remove the trap that caused damage
                    trap.kill()
                    break
        
        # Update score
        self.score += 1
        
        # Increase difficulty over time - more gradual acceleration
        if self.score % 300 == 0:  # More frequent speed increases
            self.speed += 0.5  # Smaller speed increments for smoother acceleration
    
    def spawn_trap(self):
        """Create a new trap"""
        # Randomly decide if we should spawn a special trap pattern
        pattern_chance = min(0.03 + (self.score / 15000), 0.15)  # Reduced chance, slower progression
        
        if random.random() < pattern_chance:
            # Special trap pattern - choose a pattern type
            pattern_type = random.choice(['double', 'staggered'])  # Removed 'triple' pattern
            
            if pattern_type == 'double':
                # Two traps with enough space to jump between them
                trap1 = Trap(self.speed)
                self.traps.add(trap1)
                self.all_sprites.add(trap1)
                
                # Second trap follows with enough space to jump over
                trap2 = Trap(self.speed * 0.95)  # Slightly slower
                trap2.rect.x = SCREEN_WIDTH + random.randint(350, 450)  # Significantly increased spacing
                self.traps.add(trap2)
                self.all_sprites.add(trap2)
                
            elif pattern_type == 'staggered':
                # Two traps with different heights but enough space between them
                trap1 = Trap(self.speed)
                self.traps.add(trap1)
                self.all_sprites.add(trap1)
                
                # Second trap follows at a comfortable jumping distance
                trap2 = Trap(self.speed)
                trap2.rect.x = SCREEN_WIDTH + random.randint(400, 500)  # Much more space
                self.traps.add(trap2)
                self.all_sprites.add(trap2)
        else:
            # Standard single trap
            trap = Trap(self.speed)
            self.traps.add(trap)
            self.all_sprites.add(trap)
    def draw(self):
        """Draw the game"""
        # Apply screen shake if active
        shake_offset_x = 0
        shake_offset_y = 0
        if self.screen_shake_amount > 0:
            shake_offset_x = random.randint(-int(self.screen_shake_amount), int(self.screen_shake_amount))
            shake_offset_y = random.randint(-int(self.screen_shake_amount), int(self.screen_shake_amount))
        
        # Clear the screen
        screen.fill((50, 50, 80))  # Dark blue-gray background
        
        if self.game_state == 'menu':
            # Draw menu
            self.menu_system.draw()
        
        elif self.game_state == 'playing' or self.game_state == 'paused':
            # Draw backgrounds in the correct order (from back to front)
            layer_order = ['sky', 'wall', 'background1', 'background2', 'pillar', 'ground']
            for layer_name in layer_order:
                for bg in self.backgrounds:
                    if bg.image == background_layers[layer_name]['image']:
                        # Apply screen shake to background layers except sky
                        if layer_name != 'sky' and self.screen_shake_amount > 0:
                            bg.draw(screen, offset_x=shake_offset_x, offset_y=shake_offset_y)
                        else:
                            bg.draw(screen)
                        break
            
            # Draw ground line (only if ground image is not loaded)
            if background_layers['ground']['image'] is None:
                pygame.draw.line(screen, BLACK, (0, GROUND_HEIGHT), 
                                (SCREEN_WIDTH, GROUND_HEIGHT), 2)
            
            # Draw sprites
            for sprite in self.all_sprites:
                if sprite == self.player and self.game_over:
                    # Skip drawing the player if game is over and player has been removed
                    if not hasattr(self.player, 'image') or self.player.image is None:
                        continue
                    # Otherwise draw with current opacity
                    screen.blit(self.player.image, self.player.rect)
                else:
                    screen.blit(sprite.image, sprite.rect)
            
            # Draw particle effects
            for effect in self.effects:
                effect.draw(screen)
                
            # Draw the player with fade effect if needed
            if self.game_over and hasattr(self.player, 'crumbling') and self.player.crumbling:
                if hasattr(self.player, 'crumbling_death'):
                    self.player.crumbling_death.draw()
            elif self.game_over and hasattr(self.player, 'disintegrating') and self.player.disintegrating:
                if hasattr(self.player, 'image') and self.player.image is not None:
                    screen.blit(self.player.image, self.player.rect)
                
            # Draw red overlay when player is dead
            if self.game_over and not self.show_game_over:
                # Create a semi-transparent red overlay
                red_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                red_overlay.fill((255, 0, 0, 150))  # Brighter red with more opacity
                screen.blit(red_overlay, (0, 0))
            
            # Draw score (divided by 10 to slow it down) with smaller font and border
            visible_score = self.score // 10
            
            # Format score as 4 digits (0000)
            formatted_score = f"{visible_score:04d}"
            
            # Create a score display with border
            score_text = render_text_with_border(score_font, f"Score: {formatted_score}", TEXT_COLOR, BLACK)
            screen.blit(score_text, (10, 10))
            
            # Draw high score with border (without player name during gameplay)
            high_score = self.settings_manager.get('high_score', 0) // 10
            formatted_high_score = f"{high_score:04d}"
            high_score_text = render_text_with_border(score_font, f"High Score: {formatted_high_score}", TEXT_COLOR, BLACK)
            screen.blit(high_score_text, (10, 40))  # Adjusted position due to smaller font
            
            # Draw player name with border
            name_text = render_text_with_border(score_font, f"Player: {self.player_name}", TEXT_COLOR, BLACK)
            name_x = SCREEN_WIDTH - name_text.get_width() - 20
            name_y = 10
            screen.blit(name_text, (name_x, name_y))
            
            # Draw hearts below the player name
            heart_y = name_y + name_text.get_height() + 5
            for i, heart in enumerate(self.hearts):
                heart.rect.x = SCREEN_WIDTH - 50 - (i * 35)
                heart.rect.y = heart_y
            
            # Show game over screen if needed
            if self.game_over and self.show_game_over:
                if self.has_game_over_screen and self.game_over_screen:
                    # Use enhanced game over screen
                    self.game_over_screen.update()
                    self.game_over_screen.draw()
                else:
                    # Use standard game over screen
                    # Create a semi-transparent overlay
                    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 128))  # Black with 50% transparency
                    screen.blit(overlay, (0, 0))
                    
                    # Game over text with border
                    game_over_text = render_text_with_border(title_font, "Game Over!", TEXT_COLOR, BLACK)
                    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
                    
                    # Restart instruction with border
                    restart_text = render_text_with_border(main_font, "Press R to restart", TEXT_COLOR, BLACK)
                    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
                    
                    # Menu instruction with border
                    menu_text = render_text_with_border(main_font, "Press M for main menu", TEXT_COLOR, BLACK)
                    screen.blit(menu_text, (SCREEN_WIDTH // 2 - menu_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
                    
                    # New high score notification with border
                    if self.score == self.settings_manager.get('high_score', 0) and self.score > 0:
                        high_score_text = render_text_with_border(main_font, "NEW HIGH SCORE!", (255, 255, 0), BLACK)  # Yellow text with black border
                        screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 90))
            
            # Draw pause menu if game is paused
            if self.game_state == 'paused':
                self.draw_pause_menu()
        
        # Update the display
        pygame.display.flip()
        
    def draw_pause_menu(self):
        """Draw the pause menu overlay"""
        # Create a semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Black with transparency
        screen.blit(overlay, (0, 0))
        
        # Draw pause menu title with enhanced effect
        title_text = render_text_with_border(title_font, "PAUSED", HIGHLIGHT_COLOR, BLACK)
        
        # Add pulsing effect to the pause title
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.003)) * 0.2 + 0.8
        scaled_width = int(title_text.get_width() * pulse)
        scaled_height = int(title_text.get_height() * pulse)
        scaled_title = pygame.transform.smoothscale(title_text, (scaled_width, scaled_height))
        
        # Position the title
        title_x = SCREEN_WIDTH // 2 - scaled_title.get_width() // 2
        title_y = 80 - (scaled_height - title_text.get_height()) // 2  # Adjust for scaling
        screen.blit(scaled_title, (title_x, title_y))
        
        # Draw appropriate pause menu content based on state
        if self.pause_menu_state == 'main':
            # Draw main pause menu buttons
            for button in self.pause_buttons['main']:
                button.draw(screen)
                
        elif self.pause_menu_state == 'settings':
            # Draw settings title
            settings_title = render_text_with_border(main_font, "SETTINGS", TEXT_COLOR, BLACK)
            screen.blit(settings_title, (SCREEN_WIDTH // 2 - settings_title.get_width() // 2, 150))
            
            # Draw music toggle
            self.pause_music_toggle.rect.y = 220
            self.pause_music_toggle.draw(screen)
            
            # Draw music volume slider with more space
            self.pause_music_slider.rect.y = 320
            self.pause_music_slider.draw(screen)
            
            # Draw back button
            for button in self.pause_buttons['settings']:
                button.draw(screen)
                
        elif self.pause_menu_state == 'credits':
            # Draw credits title
            credits_title = render_text_with_border(main_font, "CREDITS", TEXT_COLOR, BLACK)
            screen.blit(credits_title, (SCREEN_WIDTH // 2 - credits_title.get_width() // 2, 80))
            
            # Updated credits content with formatting
            credits = [
                ["Tomb Bound", HIGHLIGHT_COLOR, title_font],
                ["", WHITE, main_font],  # Empty line for spacing
                ["Developer", HIGHLIGHT_COLOR, main_font],
                ["N Chandra Prakash Reddy", WHITE, main_font],
                ["Tirupati, Andhra Pradesh, India", WHITE, main_font],
                ["", WHITE, main_font],  # Empty line for spacing
                ["Programming Language", HIGHLIGHT_COLOR, main_font],
                ["Python 3", WHITE, main_font],
                ["", WHITE, main_font],  # Empty line for spacing
                ["Game Library", HIGHLIGHT_COLOR, main_font],
                ["Pygame", WHITE, main_font],
                ["", WHITE, main_font],  # Empty line for spacing
                ["Development Tool", HIGHLIGHT_COLOR, main_font],
                ["Amazon Q Developer", WHITE, main_font],
                ["", WHITE, main_font],  # Empty line for spacing
                ["2D Assets", HIGHLIGHT_COLOR, main_font],
                ["Craftpix", WHITE, main_font],
                ["", WHITE, main_font],  # Empty line for spacing
                ["Music and Sound Effects", HIGHLIGHT_COLOR, main_font],
                ["Pixabay", WHITE, main_font],
                ["", WHITE, main_font],  # Empty line for spacing
                ["Thank you for playing this game!", HIGHLIGHT_COLOR, main_font]
            ]
            
            # Calculate total height of credits
            line_spacing = 40
            total_height = len(credits) * line_spacing
            
            # Update scroll position
            self.pause_credits_scroll_pos -= self.pause_credits_scroll_speed
            
            # Reset position if credits have scrolled completely off screen
            if self.pause_credits_scroll_pos < -total_height:
                self.pause_credits_scroll_pos = SCREEN_HEIGHT
            
            # Create a clipping area to prevent text from appearing behind the back button
            button_area_height = 100  # Height of the area reserved for the back button
            
            # Draw scrolling credits
            y_pos = self.pause_credits_scroll_pos
            
            for line in credits:
                text, color, font = line
                if text:  # Skip empty strings in y position calculation
                    text_surf = render_text_with_border(font, text, color, BLACK)
                    # Only draw if within visible area and not overlapping with button area
                    if 120 < y_pos < SCREEN_HEIGHT - button_area_height:
                        screen.blit(text_surf, (SCREEN_WIDTH // 2 - text_surf.get_width() // 2, y_pos))
                y_pos += line_spacing
            
            # Draw back button (fixed position)
            for button in self.pause_buttons['credits']:
                button.rect.y = SCREEN_HEIGHT - 80
                button.draw(screen)

# Fragment class from crumbling_death.py for death animation
class Fragment:
    def __init__(self, x, y, size, color, velocity_x=0, velocity_y=0):
        self.x = x
        self.y = y
        self.size = size
        self.original_size = size
        self.color = color
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-5, 5)
        self.gravity = random.uniform(0.2, 0.4)
        self.fade_speed = random.uniform(2, 5)
        self.alpha = 255
        self.shape = random.choice(['rect', 'poly'])
        
        # For polygon fragments
        if self.shape == 'poly':
            self.points = []
            point_count = random.randint(3, 6)
            for i in range(point_count):
                angle = 2 * math.pi * i / point_count
                dist = size * random.uniform(0.5, 1.0)
                self.points.append((
                    math.cos(angle) * dist,
                    math.sin(angle) * dist
                ))
    
    def update(self):
        # Apply gravity
        self.velocity_y += self.gravity
        
        # Update position
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Update rotation
        self.rotation += self.rotation_speed
        
        # Fade out
        self.alpha -= self.fade_speed
        if self.alpha < 0:
            self.alpha = 0
        
        # Shrink slightly
        self.size = max(0, self.size - 0.1)
        
        return self.alpha > 0 and self.size > 0
    
    def draw(self, surface):
        if self.alpha <= 0:
            return
            
        # Create a temporary surface for this fragment
        temp_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        
        # Get color with alpha
        color_with_alpha = (*self.color, self.alpha)
        
        # Draw the fragment
        if self.shape == 'rect':
            # Draw a rectangle
            rect = pygame.Rect(0, 0, self.size, self.size)
            rect.center = (self.size, self.size)
            pygame.draw.rect(temp_surface, color_with_alpha, rect)
        else:
            # Draw a polygon
            points = []
            for px, py in self.points:
                # Scale points based on current size ratio
                scale = self.size / self.original_size
                points.append((
                    self.size + px * scale,
                    self.size + py * scale
                ))
            pygame.draw.polygon(temp_surface, color_with_alpha, points)
        
        # Rotate the surface
        rotated = pygame.transform.rotate(temp_surface, self.rotation)
        
        # Blit to the main surface
        rect = rotated.get_rect()
        rect.center = (int(self.x), int(self.y))
        surface.blit(rotated, rect)

# Run the game
if __name__ == "__main__":
    game = Game()
    game.run()
