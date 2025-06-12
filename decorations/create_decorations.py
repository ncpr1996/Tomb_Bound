import pygame
import os

# Initialize pygame
pygame.init()

# Create decorative elements
def create_skull():
    size = 60
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Draw skull shape
    skull_color = (220, 220, 200)  # Off-white
    
    # Main skull
    pygame.draw.ellipse(surface, skull_color, (10, 5, 40, 35))
    
    # Jaw
    pygame.draw.rect(surface, skull_color, (15, 35, 30, 15), border_radius=5)
    
    # Eyes
    eye_color = (0, 0, 0)
    pygame.draw.ellipse(surface, eye_color, (18, 20, 10, 12))
    pygame.draw.ellipse(surface, eye_color, (32, 20, 10, 12))
    
    # Nose
    pygame.draw.polygon(surface, eye_color, [(30, 25), (25, 35), (35, 35)])
    
    # Teeth
    teeth_color = (250, 250, 250)
    for i in range(5):
        pygame.draw.rect(surface, teeth_color, (17 + i*6, 40, 4, 5))
    
    return surface

def create_torch():
    size = 60
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Draw torch handle
    handle_color = (101, 67, 33)  # Brown
    pygame.draw.rect(surface, handle_color, (25, 20, 10, 35))
    
    # Draw torch head
    head_color = (150, 75, 0)  # Darker brown
    pygame.draw.ellipse(surface, head_color, (20, 10, 20, 15))
    
    # Draw flame
    flame_colors = [
        (255, 0, 0),      # Red
        (255, 120, 0),    # Orange
        (255, 215, 0)     # Yellow
    ]
    
    # Draw flame layers
    pygame.draw.ellipse(surface, flame_colors[0], (15, 0, 30, 20))
    pygame.draw.ellipse(surface, flame_colors[1], (20, 3, 20, 15))
    pygame.draw.ellipse(surface, flame_colors[2], (23, 5, 14, 10))
    
    return surface

def create_scarab():
    size = 60
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Draw scarab body
    body_color = (0, 0, 120)  # Dark blue
    highlight_color = (0, 200, 200)  # Turquoise
    
    # Main body
    pygame.draw.ellipse(surface, body_color, (10, 15, 40, 30))
    
    # Head
    pygame.draw.circle(surface, body_color, (20, 15), 10)
    
    # Decorative patterns
    pygame.draw.line(surface, highlight_color, (30, 15), (30, 45), 2)
    pygame.draw.arc(surface, highlight_color, (15, 20, 30, 20), 0, 3.14, 2)
    
    # Legs (3 on each side)
    for i in range(3):
        # Left legs
        pygame.draw.line(surface, body_color, (15 + i*10, 25), (5 + i*5, 35 + i*5), 2)
        # Right legs
        pygame.draw.line(surface, body_color, (45 - i*10, 25), (55 - i*5, 35 + i*5), 2)
    
    return surface

# Create and save the decorations
if __name__ == "__main__":
    # Create decorations directory if it doesn't exist
    if not os.path.exists("decorations"):
        os.makedirs("decorations")
    
    # Create and save skull
    skull = create_skull()
    pygame.image.save(skull, os.path.join("decorations", "skull.png"))
    
    # Create and save torch
    torch = create_torch()
    pygame.image.save(torch, os.path.join("decorations", "torch.png"))
    
    # Create and save scarab
    scarab = create_scarab()
    pygame.image.save(scarab, os.path.join("decorations", "scarab.png"))
    
    print("Decorations created successfully!")
