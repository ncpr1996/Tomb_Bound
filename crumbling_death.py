import pygame
import random
import math

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
        
        # Return True if fragment is still visible
        return self.alpha > 0
    
    def draw(self, surface):
        # Create a surface for the fragment
        fragment_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        
        # Draw the fragment shape
        if self.shape == 'rect':
            # Draw a rectangle with rotation
            rect = pygame.Rect(0, 0, self.size, self.size)
            rect.center = (self.size, self.size)
            
            # Create a temporary surface for rotation
            temp_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.rect(temp_surf, self.color + (self.alpha,), rect)
            
            # Rotate the surface
            rotated_surf = pygame.transform.rotate(temp_surf, self.rotation)
            
            # Blit to fragment surface
            fragment_surf.blit(rotated_surf, 
                             (self.size - rotated_surf.get_width() // 2,
                              self.size - rotated_surf.get_height() // 2))
            
        else:  # 'poly'
            # Draw a polygon with rotation
            rotated_points = []
            for x, y in self.points:
                # Rotate point
                angle = math.radians(self.rotation)
                rx = x * math.cos(angle) - y * math.sin(angle)
                ry = x * math.sin(angle) + y * math.cos(angle)
                # Translate to center
                rotated_points.append((rx + self.size, ry + self.size))
            
            pygame.draw.polygon(fragment_surf, self.color + (self.alpha,), rotated_points)
        
        # Draw the fragment on the main surface
        surface.blit(fragment_surf, (self.x - self.size, self.y - self.size))

class DustParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.uniform(1, 3)
        self.color = (
            random.randint(100, 150),
            random.randint(80, 120),
            random.randint(60, 100)
        )
        self.velocity_x = random.uniform(-1, 1)
        self.velocity_y = random.uniform(-3, -0.5)
        self.gravity = random.uniform(0.05, 0.1)
        self.lifetime = random.randint(30, 90)
        self.alpha = random.randint(150, 255)
        self.fade_speed = self.alpha / self.lifetime
    
    def update(self):
        # Apply gravity
        self.velocity_y += self.gravity
        
        # Update position
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Fade out
        self.alpha -= self.fade_speed
        
        # Return True if particle is still visible
        return self.alpha > 0
    
    def draw(self, surface):
        # Draw the dust particle
        pygame.draw.circle(
            surface, 
            self.color + (int(self.alpha),), 
            (int(self.x), int(self.y)), 
            self.size
        )

class CrumblingDeath:
    def __init__(self, screen, player_rect, player_image):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Store player information
        self.player_rect = player_rect.copy()
        self.player_image = player_image.copy() if player_image else None
        
        # Animation state
        self.state = 'freeze'  # 'freeze', 'stone', 'crack', 'crumble', 'dust', 'done'
        self.timer = 0
        self.freeze_duration = 30  # 0.5 seconds at 60 FPS
        self.stone_duration = 20   # ~0.33 seconds
        self.crack_duration = 30   # 0.5 seconds
        self.crumble_duration = 60 # 1 second
        self.dust_duration = 120   # 2 seconds
        
        # Fragments and particles
        self.fragments = []
        self.dust_particles = []
        
        # Screen shake
        self.shake_amount = 0
        self.shake_decay = 0.9
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        
        # Create stone version of player
        self.stone_image = self.create_stone_image()
        
        # Create crack overlay
        self.crack_image = self.create_crack_image()
        self.crack_alpha = 0
        
        # Generate fragments
        self.generate_fragments()
    
    def create_stone_image(self):
        if not self.player_image:
            # Create a default stone image if player image is not available
            stone_image = pygame.Surface((self.player_rect.width, self.player_rect.height), pygame.SRCALPHA)
            stone_image.fill((150, 150, 150, 255))
            return stone_image
        
        # Create a copy of the player image
        stone_image = self.player_image.copy()
        
        # Convert to grayscale with a stone-like tint
        for x in range(stone_image.get_width()):
            for y in range(stone_image.get_height()):
                color = stone_image.get_at((x, y))
                if color.a > 0:  # Only process non-transparent pixels
                    # Convert to grayscale
                    gray = (color.r + color.g + color.b) // 3
                    # Add stone tint (slightly brownish gray)
                    stone_image.set_at((x, y), (
                        min(255, gray + 20),  # More red for brown tint
                        min(255, gray + 10),  # Less green
                        min(255, gray),       # Even less blue
                        color.a
                    ))
        
        return stone_image
    
    def create_crack_image(self):
        # Create a transparent surface for cracks
        crack_image = pygame.Surface((self.player_rect.width, self.player_rect.height), pygame.SRCALPHA)
        
        # Generate random crack patterns
        center_x = self.player_rect.width // 2
        center_y = self.player_rect.height // 2
        
        # Create main cracks from center
        for _ in range(random.randint(4, 7)):
            start_x = center_x
            start_y = center_y
            angle = random.uniform(0, 2 * math.pi)
            length = random.uniform(0.5, 1.0) * self.player_rect.width
            
            # Draw branching cracks
            self.draw_crack(crack_image, start_x, start_y, angle, length, 2)
        
        return crack_image
    
    def draw_crack(self, surface, x, y, angle, length, thickness, depth=0):
        if depth > 3 or length < 5:  # Limit recursion depth and minimum length
            return
            
        # Calculate end point
        end_x = x + math.cos(angle) * length
        end_y = y + math.sin(angle) * length
        
        # Ensure end point is within bounds
        end_x = max(0, min(surface.get_width() - 1, end_x))
        end_y = max(0, min(surface.get_height() - 1, end_y))
        
        # Draw the crack line
        pygame.draw.line(surface, (0, 0, 0, 200), (x, y), (end_x, end_y), thickness)
        
        # Create branches with some probability
        if random.random() < 0.7:
            branch_angle1 = angle + random.uniform(-0.5, 0.5)
            branch_angle2 = angle + random.uniform(-0.5, 0.5)
            branch_length = length * random.uniform(0.4, 0.7)
            
            self.draw_crack(surface, end_x, end_y, branch_angle1, branch_length, 
                          max(1, thickness-1), depth+1)
            self.draw_crack(surface, end_x, end_y, branch_angle2, branch_length, 
                          max(1, thickness-1), depth+1)
    
    def generate_fragments(self):
        if not self.player_image:
            # Generate default fragments if player image is not available
            player_width = self.player_rect.width
            player_height = self.player_rect.height
            
            # Generate large chunks
            for _ in range(10):
                size = random.randint(5, 15)
                x = self.player_rect.x + random.randint(0, player_width)
                y = self.player_rect.y + random.randint(0, player_height)
                color = (
                    random.randint(120, 180),
                    random.randint(100, 160),
                    random.randint(80, 140)
                )
                velocity_x = random.uniform(-3, 3)
                velocity_y = random.uniform(-8, 0)
                
                self.fragments.append(Fragment(x, y, size, color, velocity_x, velocity_y))
            
            # Generate medium chunks
            for _ in range(20):
                size = random.randint(3, 8)
                x = self.player_rect.x + random.randint(0, player_width)
                y = self.player_rect.y + random.randint(0, player_height)
                color = (
                    random.randint(100, 160),
                    random.randint(80, 140),
                    random.randint(60, 120)
                )
                velocity_x = random.uniform(-2, 2)
                velocity_y = random.uniform(-6, 0)
                
                self.fragments.append(Fragment(x, y, size, color, velocity_x, velocity_y))
            
            # Generate small chunks
            for _ in range(30):
                size = random.randint(1, 4)
                x = self.player_rect.x + random.randint(0, player_width)
                y = self.player_rect.y + random.randint(0, player_height)
                color = (
                    random.randint(80, 140),
                    random.randint(60, 120),
                    random.randint(40, 100)
                )
                velocity_x = random.uniform(-1, 1)
                velocity_y = random.uniform(-4, 0)
                
                self.fragments.append(Fragment(x, y, size, color, velocity_x, velocity_y))
            
            return
        
        # If we have a player image, generate fragments based on it
        # This is more complex and would analyze the player image to create
        # fragments that match the player's appearance
        # For simplicity, we'll use the default approach for now
        player_width = self.player_rect.width
        player_height = self.player_rect.height
        
        # Generate large chunks
        for _ in range(10):
            size = random.randint(5, 15)
            x = self.player_rect.x + random.randint(0, player_width)
            y = self.player_rect.y + random.randint(0, player_height)
            color = (
                random.randint(120, 180),
                random.randint(100, 160),
                random.randint(80, 140)
            )
            velocity_x = random.uniform(-3, 3)
            velocity_y = random.uniform(-8, 0)
            
            self.fragments.append(Fragment(x, y, size, color, velocity_x, velocity_y))
        
        # Generate medium chunks
        for _ in range(20):
            size = random.randint(3, 8)
            x = self.player_rect.x + random.randint(0, player_width)
            y = self.player_rect.y + random.randint(0, player_height)
            color = (
                random.randint(100, 160),
                random.randint(80, 140),
                random.randint(60, 120)
            )
            velocity_x = random.uniform(-2, 2)
            velocity_y = random.uniform(-6, 0)
            
            self.fragments.append(Fragment(x, y, size, color, velocity_x, velocity_y))
        
        # Generate small chunks
        for _ in range(30):
            size = random.randint(1, 4)
            x = self.player_rect.x + random.randint(0, player_width)
            y = self.player_rect.y + random.randint(0, player_height)
            color = (
                random.randint(80, 140),
                random.randint(60, 120),
                random.randint(40, 100)
            )
            velocity_x = random.uniform(-1, 1)
            velocity_y = random.uniform(-4, 0)
            
            self.fragments.append(Fragment(x, y, size, color, velocity_x, velocity_y))
    
    def add_dust_particles(self, count, x, y):
        for _ in range(count):
            self.dust_particles.append(DustParticle(x, y))
    
    def trigger_screen_shake(self, amount=10):
        self.shake_amount = amount
    
    def update_screen_shake(self):
        if self.shake_amount > 0:
            self.shake_offset_x = random.randint(-int(self.shake_amount), int(self.shake_amount))
            self.shake_offset_y = random.randint(-int(self.shake_amount), int(self.shake_amount))
            self.shake_amount *= self.shake_decay
            if self.shake_amount < 0.1:
                self.shake_amount = 0
                self.shake_offset_x = 0
                self.shake_offset_y = 0
    
    def update(self):
        self.timer += 1
        
        # Update screen shake
        self.update_screen_shake()
        
        # Update state based on timer
        if self.state == 'freeze' and self.timer >= self.freeze_duration:
            self.state = 'stone'
            self.timer = 0
        elif self.state == 'stone' and self.timer >= self.stone_duration:
            self.state = 'crack'
            self.timer = 0
        elif self.state == 'crack' and self.timer >= self.crack_duration:
            self.state = 'crumble'
            self.timer = 0
            self.trigger_screen_shake()
        elif self.state == 'crumble' and self.timer >= self.crumble_duration:
            self.state = 'dust'
            self.timer = 0
        elif self.state == 'dust' and self.timer >= self.dust_duration:
            self.state = 'done'
            self.timer = 0
        
        # Update crack alpha
        if self.state == 'crack':
            self.crack_alpha = min(255, int(255 * self.timer / self.crack_duration))
        
        # Update fragments
        if self.state in ['crumble', 'dust']:
            # Update existing fragments
            for fragment in self.fragments[:]:
                if not fragment.update():
                    self.fragments.remove(fragment)
            
            # Add dust particles where fragments hit the ground
            for fragment in self.fragments:
                if fragment.y > self.screen_height - 50 and random.random() < 0.05:
                    self.add_dust_particles(random.randint(1, 3), fragment.x, fragment.y)
        
        # Update dust particles
        for particle in self.dust_particles[:]:
            if not particle.update():
                self.dust_particles.remove(particle)
    
    def draw(self):
        # Apply screen shake offset
        original_rect = self.screen.get_rect()
        shake_rect = original_rect.copy()
        shake_rect.x += self.shake_offset_x
        shake_rect.y += self.shake_offset_y
        
        # Draw based on current state
        if self.state == 'freeze':
            # Draw original player image
            if self.player_image:
                self.screen.blit(self.player_image, self.player_rect)
        
        elif self.state == 'stone':
            # Draw stone version of player
            if self.stone_image:
                self.screen.blit(self.stone_image, self.player_rect)
        
        elif self.state == 'crack':
            # Draw stone with cracks
            if self.stone_image:
                self.screen.blit(self.stone_image, self.player_rect)
            
            # Draw cracks with increasing opacity
            if self.crack_image:
                crack_with_alpha = self.crack_image.copy()
                crack_with_alpha.set_alpha(self.crack_alpha)
                self.screen.blit(crack_with_alpha, self.player_rect)
        
        elif self.state in ['crumble', 'dust', 'done']:
            # Draw all fragments
            for fragment in self.fragments:
                fragment.draw(self.screen)
            
            # Draw all dust particles
            for particle in self.dust_particles:
                particle.draw(self.screen)
    
    def is_finished(self):
        return self.state == 'done'
