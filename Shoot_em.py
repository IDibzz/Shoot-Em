import pygame 
import time
import random
import json
import os
import re
import math
pygame.font.init()
pygame.init()

WIDTH, HEIGHT = 1920, 1080
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shoot Em")

BG = pygame.transform.scale(pygame.image.load("grass3.png"), (WIDTH,HEIGHT))

PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
PLAYER_VEL = 5

projectiles = []
projectile_color = (255, 0, 0)
projectile_speed = 5

def draw(player):
    WIN.blit(BG, (0,0))
   
    pygame.draw.rect(WIN, "red", player)
    for projectile in projectiles:
            pygame.draw.circle(WIN, projectile_color, (int(projectile[0]), int(projectile[1])), 5)
    pygame.display.update()

def add_projectile(player_pos, target_pos):
    dx, dy = target_pos[0] - player_pos[0], target_pos[1] - player_pos[1]
    distance = math.hypot(dx, dy)
    if distance == 0:  # Prevent division by zero
        distance = 1
    dx, dy = dx / distance, dy / distance  # Normalize
    return [player_pos[0], player_pos[1], dx, dy]

def main():
    run = True
    player = pygame.Rect(200,HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
    clock = pygame.time.Clock()





    while run:
        clock.tick(60)
        
        player_pos = []
        player_pos = player.x + 20, player.y
       

        
        
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
            # Add a new projectile on mouse click
                projectiles.append(add_projectile(player_pos, pygame.mouse.get_pos()))  

        
        for projectile in projectiles:
            projectile[0] += projectile[2] * projectile_speed
            projectile[1] += projectile[3] * projectile_speed

        
        

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - PLAYER_VEL >= 0:
            player.x -= PLAYER_VEL
        if keys[pygame.K_RIGHT] and player.x + PLAYER_VEL + player.width <= WIDTH:
            player.x += PLAYER_VEL
        if keys[pygame.K_UP] and player.y - PLAYER_VEL >= 0:
            player.y -= PLAYER_VEL
        if keys[pygame.K_DOWN] and player.y + PLAYER_VEL + player.height <= HEIGHT:
            player.y += PLAYER_VEL
        draw(player)




if __name__ == "__main__":
    main() 