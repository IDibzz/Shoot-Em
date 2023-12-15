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
projectiles2 = []
projectile_color = (255, 0, 0)
projectile_speed = 5
projectile_speed2 = 10

thingy_width = 20
thingy_height = 10
FONT = pygame.font.SysFont("comicsans", 30)

def draw(player, Player_moving, thingy, score):
    WIN.blit(BG, (0,0))
    pygame.draw.rect(WIN, "blue", thingy)
    pygame.draw.rect(WIN, "red", player)
    
    score_text = FONT.render(str(score), 1, "white")
    WIN.blit(score_text, (10,10))

    for projectile in projectiles2:
        pygame.draw.circle(WIN, projectile_color, (int(projectile[0]), int(projectile[1])), 5)
    
    for projectile in projectiles:
            pygame.draw.circle(WIN, projectile_color, (int(projectile[0]), int(projectile[1])), 5)
    pygame.display.update()
    
def check_collision(thingy, projectiles, score): 
    thingy_hit = False
    for projectile in projectiles:
        # Create a rect for the projectile
        projectile_rect = pygame.Rect(projectile[0] - 5, projectile[1] - 5, 10, 10)
        if projectile_rect.colliderect(thingy):
            projectiles.remove(projectile)
            score += 1
            thingy_hit = True
    return score, thingy_hit

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
    thingy = pygame.Rect(400,400,thingy_width,thingy_height)
    clock = pygame.time.Clock()
    Player_moving = False  
    last_shot_time = 0
    shot_delay = 1000 
    score = 0


    while run:
        clock.tick(60)
        
        player_pos = []
        player_pos = player.x + 20, player.y
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        
        
        if keys[pygame.K_a] | keys[pygame.K_s] | keys[pygame.K_d] | keys[pygame.K_w]:
            Player_moving = True
        else:
            Player_moving = False
        
       
                


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
            # Add a new projectile on mouse click
                current_time = pygame.time.get_ticks()
                if current_time - last_shot_time >= shot_delay:
                    last_shot_time = current_time
                    if Player_moving:
                        projectiles2.append(add_projectile(player_pos, pygame.mouse.get_pos())) 
                    else:
                        projectiles.append(add_projectile(player_pos, pygame.mouse.get_pos()))  
                    
                    
        
        
        
        
        for projectile in projectiles2:
                projectile[0] += projectile[2] * projectile_speed2
                projectile[1] += projectile[3] * projectile_speed2
                
        
        for projectile in projectiles:
                projectile[0] += projectile[2] * projectile_speed
                projectile[1] += projectile[3] * projectile_speed
        
        
        score, thingy_hit = check_collision(thingy, projectiles, score)
        if not thingy_hit:  
            score, thingy_hit = check_collision(thingy, projectiles2, score)

        
        

        if keys[pygame.K_a] and player.x - PLAYER_VEL >= 0:
            player.x -= PLAYER_VEL
        if keys[pygame.K_d] and player.x + PLAYER_VEL + player.width <= WIDTH:
            player.x += PLAYER_VEL
        if keys[pygame.K_w] and player.y - PLAYER_VEL >= 0:
            player.y -= PLAYER_VEL
        if keys[pygame.K_s] and player.y + PLAYER_VEL + player.height <= HEIGHT:
            player.y += PLAYER_VEL
        draw(player, Player_moving, thingy, score)




if __name__ == "__main__":
    main() 