import pygame
import math
import random
import os

class EnhancedTitle:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.screen_width = width
        self.screen_height = height
        
        # Title text
        self.title_text = "TOMB BOUND"
        
        # Colors
        self.gold = (255, 215, 0)
        self.dark_gold = (184, 134, 11)
        self.light_gold = (255, 223, 100)
        self.sand_color = (194, 178, 128)
        self.dark_brown = (101, 67, 33)
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        
        # Animation variables
        self.time = 0
        self.pulse_speed = 0.05
        self.glow_intensity = 0
        self.particle_timer = 0
        self.particles = []
        
        # Load fonts
        try:
            # Try to load a more thematic font if available
            font_path = os.path.join('fonts', 'ancient.ttf')
            if os.path.exists(font_path):
                self.main_font = pygame.font.Font(font_path, 80)
                self.shadow_font = pygame.font.Font(font_path, 80)
                self.small_font = pygame.font.Font(font_path, 30)
            else:
                # Fallback to default fonts
                self.main_font = pygame.font.Font(None, 80)
                self.shadow_font = pygame.font.Font(None, 80)
                self.small_font = pygame.font.Font(None, 30)
        except:
            # Further fallback
            self.main_font = pygame.font.SysFont('Arial', 80)
            self.shadow_font = pygame.font.SysFont('Arial', 80)
            self.small_font = pygame.font.SysFont('Arial', 30)
        
        # Load decorative elements
        self.decorations = []
        try:
            # Try to load decorative images
            decoration_paths = [
                os.path.join('decorations', 'skull.png'),
                os.path.join('decorations', 'torch.png'),
                os.path.join('decorations', 'scarab.png')
            ]
            
            for path in decoration_paths:
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    # Scale to appropriate size
                    img = pygame.transform.scale(img, (60, 60))
                    self.decorations.append(img)
        except:
            # No decorations if loading fails
            pass
        
        # Create surfaces for the title components
        self.create_title_surfaces()
        
    def create_title_surfaces(self):
        # Main title text with gradient
        self.title_surface = self.create_gradient_text(self.main_font, self.title_text, 
                                                      self.light_gold, self.dark_gold)
        
        # Shadow for depth
        self.shadow_surface = self.shadow_font.render(self.title_text, True, self.black)
        
        # Glow surface (will be updated during animation)
        self.glow_surface = pygame.Surface((self.title_surface.get_width() + 20, 
                                           self.title_surface.get_height() + 20), 
                                          pygame.SRCALPHA)
        
        # Subtitle
        self.subtitle_surface = self.small_font.render("EXPLORE THE ANCIENT DEPTHS", True, self.sand_color)
        
    def create_gradient_text(self, font, text, color1, color2):
        # Create initial text surface
        base = font.render(text, True, color1)
        width, height = base.get_size()
        
        # Create surface for gradient text
        gradient_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Draw gradient
        for y in range(height):
            # Calculate gradient color for this line
            ratio = y / height
            r = color1[0] * (1 - ratio) + color2[0] * ratio
            g = color1[1] * (1 - ratio) + color2[1] * ratio
            b = color1[2] * (1 - ratio) + color2[2] * ratio
            color = (int(r), int(g), int(b))
            
            # Draw a line of this color
            pygame.draw.line(gradient_surface, color, (0, y), (width, y))
        
        # Apply text as a mask
        gradient_surface.blit(base, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        return gradient_surface
    
    def update_glow(self):
        # Clear the glow surface
        self.glow_surface.fill((0, 0, 0, 0))
        
        # Calculate glow intensity (pulsing effect)
        self.glow_intensity = abs(math.sin(self.time * self.pulse_speed)) * 0.5 + 0.5
        
        # Draw multiple versions of the text with increasing size and decreasing alpha
        original_width, original_height = self.title_surface.get_size()
        max_glow = 10
        
        for i in range(1, max_glow + 1):
            size = i / max_glow
            alpha = int(255 * (1 - size) * self.glow_intensity)
            
            # Skip if barely visible
            if alpha < 20:
                continue
                
            # Create a larger surface for this glow layer
            glow_layer = pygame.Surface((original_width + i*2, original_height + i*2), pygame.SRCALPHA)
            
            # Create a copy of the title with the glow color
            glow_text = self.main_font.render(self.title_text, True, self.light_gold)
            glow_text.set_alpha(alpha)
            
            # Position in the center of the larger surface
            x = (glow_layer.get_width() - original_width) // 2
            y = (glow_layer.get_height() - original_height) // 2
            
            # Draw the glow text
            glow_layer.blit(glow_text, (x, y))
            
            # Add this layer to the main glow surface
            self.glow_surface.blit(glow_layer, (0, 0))
    
    def update_particles(self):
        # Add new particles occasionally
        self.particle_timer += 1
        if self.particle_timer >= 5:  # Every 5 frames
            self.particle_timer = 0
            
            # Add 1-3 new particles
            for _ in range(random.randint(1, 3)):
                # Position near the title
                title_width = self.title_surface.get_width()
                x = random.randint(self.screen_width//2 - title_width//2, 
                                  self.screen_width//2 + title_width//2)
                y = random.randint(80, 120)
                
                # Random movement
                speed_x = random.uniform(-0.5, 0.5)
                speed_y = random.uniform(-1.5, -0.5)
                
                # Random size and color
                size = random.randint(2, 5)
                color = random.choice([self.light_gold, self.gold, self.sand_color])
                
                # Random lifetime
                lifetime = random.randint(30, 90)
                
                # Add particle [x, y, speed_x, speed_y, size, color, lifetime]
                self.particles.append([x, y, speed_x, speed_y, size, color, lifetime])
        
        # Update existing particles
        for particle in self.particles[:]:
            # Move particle
            particle[0] += particle[2]  # x position
            particle[1] += particle[3]  # y position
            
            # Decrease lifetime
            particle[6] -= 1
            
            # Remove if lifetime is over
            if particle[6] <= 0:
                self.particles.remove(particle)
    
    def update(self):
        # Update time
        self.time += 1
        
        # Update glow effect
        self.update_glow()
        
        # Update particles
        self.update_particles()
    
    def draw(self):
        # Calculate title position (center of screen)
        title_x = self.screen_width // 2 - self.title_surface.get_width() // 2
        title_y = 80  # Position from top
        
        # Draw decorative elements if available
        if self.decorations:
            # Left decoration
            if len(self.decorations) > 0:
                left_x = title_x - self.decorations[0].get_width() - 20
                left_y = title_y + self.title_surface.get_height() // 2 - self.decorations[0].get_height() // 2
                self.screen.blit(self.decorations[0], (left_x, left_y))
            
            # Right decoration
            if len(self.decorations) > 1:
                right_x = title_x + self.title_surface.get_width() + 20
                right_y = title_y + self.title_surface.get_height() // 2 - self.decorations[1].get_height() // 2
                self.screen.blit(self.decorations[1], (right_x, right_y))
        
        # Draw horizontal decorative lines
        line_y = title_y + self.title_surface.get_height() + 10
        line_width = self.title_surface.get_width() + 100
        line_x = self.screen_width // 2 - line_width // 2
        
        # Draw main line
        pygame.draw.line(self.screen, self.gold, 
                        (line_x, line_y), 
                        (line_x + line_width, line_y), 3)
        
        # Draw smaller accent lines
        pygame.draw.line(self.screen, self.dark_gold, 
                        (line_x + 20, line_y + 5), 
                        (line_x + line_width - 20, line_y + 5), 1)
        
        # Draw particles
        for particle in self.particles:
            # Extract particle properties
            x, y, _, _, size, color, lifetime = particle
            
            # Adjust alpha based on lifetime
            alpha = min(255, lifetime * 3)
            
            # Draw the particle
            particle_surface = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (*color, alpha), (size, size), size)
            self.screen.blit(particle_surface, (x - size, y - size))
        
        # Draw glow effect
        glow_x = title_x - 10  # Offset to account for glow size
        glow_y = title_y - 10
        self.screen.blit(self.glow_surface, (glow_x, glow_y))
        
        # Draw shadow (offset slightly)
        shadow_offset = 3
        self.screen.blit(self.shadow_surface, (title_x + shadow_offset, title_y + shadow_offset))
        
        # Draw main title
        self.screen.blit(self.title_surface, (title_x, title_y))
        
        # Draw subtitle
        subtitle_x = self.screen_width // 2 - self.subtitle_surface.get_width() // 2
        subtitle_y = title_y + self.title_surface.get_height() + 20
        self.screen.blit(self.subtitle_surface, (subtitle_x, subtitle_y))
        
        # Draw hieroglyphic-style border elements
        self.draw_border_elements()
    
    def draw_border_elements(self):
        # Draw corner elements
        corner_size = 30
        margin = 20
        
        # Define hieroglyphic-like symbols
        symbols = [
            # Simple eye symbol
            lambda surface, x, y, size: pygame.draw.ellipse(surface, self.gold, 
                                                          (x, y, size, size//2), 2),
            # Ankh-like symbol
            lambda surface, x, y, size: (
                pygame.draw.line(surface, self.gold, (x+size//2, y), (x+size//2, y+size), 2),
                pygame.draw.ellipse(surface, self.gold, (x, y, size, size//2), 2)
            ),
            # Pyramid
            lambda surface, x, y, size: pygame.draw.polygon(surface, self.gold, 
                                                          [(x, y+size), (x+size//2, y), (x+size, y+size)], 2)
        ]
        
        # Draw symbols in corners
        corners = [
            (margin, margin),  # Top-left
            (self.screen_width - margin - corner_size, margin),  # Top-right
            (margin, self.screen_height - margin - corner_size),  # Bottom-left
            (self.screen_width - margin - corner_size, self.screen_height - margin - corner_size)  # Bottom-right
        ]
        
        for i, (x, y) in enumerate(corners):
            symbol = symbols[i % len(symbols)]
            symbol(self.screen, x, y, corner_size)
