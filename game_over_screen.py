import pygame
import math
import random
import os

class GameOverScreen:
    def __init__(self, screen, screen_width, screen_height):
        self.screen = screen
        self.width = screen_width
        self.height = screen_height
        
        # Animation timers and states
        self.time = 0
        self.fade_in = 0  # 0 to 255
        self.particles = []
        self.cracks = []
        
        # Load fonts
        try:
            self.title_font = pygame.font.Font(None, 80)
            self.main_font = pygame.font.Font(None, 36)
        except:
            self.title_font = pygame.font.SysFont('Arial', 80)
            self.main_font = pygame.font.SysFont('Arial', 36)
        
        # Load decorative elements
        self.decorations = []
        try:
            decoration_paths = [
                os.path.join('decorations', 'skull.png'),
                os.path.join('decorations', 'torch.png')
            ]
            
            for path in decoration_paths:
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    img = pygame.transform.scale(img, (60, 60))
                    self.decorations.append(img)
        except Exception as e:
            print(f"Error loading decorations: {e}")
        
        # Create text surfaces
        self.title_text = "GAME OVER"
        self.subtitle_text = "Your Journey Ends Here"
        self.restart_text = "R - RESTART YOUR JOURNEY"
        self.menu_text = "M - RETURN TO MAIN MENU"
        
        # Create gradient surfaces for text
        self.title_surface = self.create_gradient_text(self.title_font, self.title_text, 
                                                     (200, 0, 0), (100, 0, 0))
        self.subtitle_surface = self.create_gradient_text(self.main_font, self.subtitle_text,
                                                        (180, 180, 180), (100, 100, 100))
        
        # Initialize crack effect
        self.generate_cracks()
        
        # Initialize particles
        for _ in range(30):
            self.add_particle()
    
    def create_gradient_text(self, font, text, color1, color2):
        base = font.render(text, True, color1)
        width, height = base.get_size()
        
        gradient_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        for y in range(height):
            ratio = y / height
            r = color1[0] * (1 - ratio) + color2[0] * ratio
            g = color1[1] * (1 - ratio) + color2[1] * ratio
            b = color1[2] * (1 - ratio) + color2[2] * ratio
            color = (int(r), int(g), int(b))
            
            pygame.draw.line(gradient_surface, color, (0, y), (width, y))
        
        gradient_surface.blit(base, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return gradient_surface
    
    def generate_cracks(self):
        # Create crack patterns emanating from center
        center_x, center_y = self.width // 2, self.height // 2
        
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            length = random.randint(50, 200)
            thickness = random.randint(1, 3)
            
            # Create branching cracks
            self.create_crack_branch(center_x, center_y, angle, length, thickness)
    
    def create_crack_branch(self, x, y, angle, length, thickness, depth=0):
        if depth > 3:  # Limit recursion depth
            return
            
        # Calculate end point
        end_x = x + math.cos(angle) * length
        end_y = y + math.sin(angle) * length
        
        # Add this crack segment
        self.cracks.append({
            'start': (x, y),
            'end': (end_x, end_y),
            'thickness': thickness,
            'alpha': random.randint(100, 200)
        })
        
        # Create branches with some probability
        if random.random() < 0.7 and depth < 2:
            branch_angle1 = angle + random.uniform(-0.5, 0.5)
            branch_angle2 = angle + random.uniform(-0.5, 0.5)
            branch_length = length * random.uniform(0.5, 0.8)
            
            self.create_crack_branch(end_x, end_y, branch_angle1, branch_length, 
                                   max(1, thickness-1), depth+1)
            self.create_crack_branch(end_x, end_y, branch_angle2, branch_length, 
                                   max(1, thickness-1), depth+1)
    
    def add_particle(self):
        # Add dust/debris particle
        x = random.randint(0, self.width)
        y = random.randint(0, self.height)
        size = random.randint(1, 4)
        speed_x = random.uniform(-0.5, 0.5)
        speed_y = random.uniform(-0.5, 0.5)
        lifetime = random.randint(100, 200)
        color = random.choice([(100, 100, 100), (150, 150, 150), (200, 200, 200)])
        
        self.particles.append({
            'x': x, 'y': y, 'size': size,
            'speed_x': speed_x, 'speed_y': speed_y,
            'lifetime': lifetime, 'max_lifetime': lifetime,
            'color': color
        })
    
    def update(self):
        self.time += 1
        
        # Update fade-in effect
        if self.fade_in < 255:
            self.fade_in = min(255, self.fade_in + 5)
        
        # Update particles
        for particle in self.particles[:]:
            particle['x'] += particle['speed_x']
            particle['y'] += particle['speed_y']
            particle['lifetime'] -= 1
            
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
                self.add_particle()
        
        # Add new particles occasionally
        if random.random() < 0.1:
            self.add_particle()
    
    def draw(self):
        # Draw background gradient
        bg_surface = pygame.Surface((self.width, self.height))
        for y in range(self.height):
            ratio = y / self.height
            color = (int(20 * (1-ratio)), int(10 * (1-ratio)), int(30 * (1-ratio)))
            pygame.draw.line(bg_surface, color, (0, y), (self.width, y))
        
        bg_surface.set_alpha(self.fade_in)
        self.screen.blit(bg_surface, (0, 0))
        
        # Draw particles
        for particle in self.particles:
            alpha = int(255 * (particle['lifetime'] / particle['max_lifetime']))
            color = particle['color'] + (alpha,)
            
            particle_surf = pygame.Surface((particle['size']*2, particle['size']*2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, color, (particle['size'], particle['size']), particle['size'])
            self.screen.blit(particle_surf, (particle['x'] - particle['size'], particle['y'] - particle['size']))
        
        # Draw cracks
        for crack in self.cracks:
            # Make cracks pulse slightly
            alpha = crack['alpha'] + int(20 * math.sin(self.time * 0.05))
            alpha = max(0, min(255, alpha))
            
            # Draw the crack with alpha
            crack_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.line(crack_surf, (255, 255, 255, alpha), 
                           crack['start'], crack['end'], crack['thickness'])
            self.screen.blit(crack_surf, (0, 0))
        
        # Draw decorative elements if available
        if self.decorations:
            # Position decorations
            if len(self.decorations) > 0:
                # Left decoration with slight animation
                left_x = self.width // 2 - 200 + int(5 * math.sin(self.time * 0.03))
                left_y = self.height // 2 - 100
                self.screen.blit(self.decorations[0], (left_x, left_y))
            
            if len(self.decorations) > 1:
                # Right decoration with slight animation
                right_x = self.width // 2 + 150 + int(5 * math.sin(self.time * 0.03 + math.pi))
                right_y = self.height // 2 - 100
                self.screen.blit(self.decorations[1], (right_x, right_y))
        
        # Draw main title with glow effect
        glow_intensity = abs(math.sin(self.time * 0.05)) * 0.5 + 0.5
        
        # Draw multiple layers for glow effect
        for i in range(1, 10):
            alpha = int(150 * (1 - i/10) * glow_intensity)
            glow_surf = pygame.Surface((self.title_surface.get_width() + i*2, 
                                      self.title_surface.get_height() + i*2), pygame.SRCALPHA)
            glow_text = self.title_font.render(self.title_text, True, (255, 0, 0))
            glow_text.set_alpha(alpha)
            
            x = (glow_surf.get_width() - self.title_surface.get_width()) // 2
            y = (glow_surf.get_height() - self.title_surface.get_height()) // 2
            glow_surf.blit(glow_text, (x, y))
            
            title_x = self.width // 2 - glow_surf.get_width() // 2
            title_y = self.height // 2 - 100 - i
            self.screen.blit(glow_surf, (title_x, title_y))
        
        # Draw main title
        title_x = self.width // 2 - self.title_surface.get_width() // 2
        title_y = self.height // 2 - 100
        self.screen.blit(self.title_surface, (title_x, title_y))
        
        # Draw subtitle
        subtitle_x = self.width // 2 - self.subtitle_surface.get_width() // 2
        subtitle_y = self.height // 2 - 40
        self.screen.blit(self.subtitle_surface, (subtitle_x, subtitle_y))
        
        # Draw restart option with highlighted R
        restart_text = self.main_font.render(self.restart_text, True, (200, 200, 200))
        restart_x = self.width // 2 - restart_text.get_width() // 2
        restart_y = self.height // 2 + 50
        self.screen.blit(restart_text, (restart_x, restart_y))
        
        # Draw pulsing highlight for R key
        r_highlight = self.main_font.render("R", True, (255, 255, 0))
        r_glow = abs(math.sin(self.time * 0.1)) * 0.5 + 0.5
        r_highlight.set_alpha(int(255 * r_glow))
        self.screen.blit(r_highlight, (restart_x, restart_y))
        
        # Draw menu option with highlighted M
        menu_text = self.main_font.render(self.menu_text, True, (200, 200, 200))
        menu_x = self.width // 2 - menu_text.get_width() // 2
        menu_y = self.height // 2 + 100
        self.screen.blit(menu_text, (menu_x, menu_y))
        
        # Draw pulsing highlight for M key
        m_highlight = self.main_font.render("M", True, (255, 255, 0))
        m_glow = abs(math.sin(self.time * 0.1 + math.pi)) * 0.5 + 0.5
        m_highlight.set_alpha(int(255 * m_glow))
        self.screen.blit(m_highlight, (menu_x, menu_y))
