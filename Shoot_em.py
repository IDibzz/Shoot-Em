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
    
    
    
    
    pygame.draw.rect(WIN, "red", player)
    
    score_text = FONT.render(str(score), 1, "white")
    WIN.blit(score_text, (10,10))

    for projectile in projectiles2:
        pygame.draw.circle(WIN, projectile_color, (int(projectile[0]), int(projectile[1])), 5)
    
    for projectile in projectiles:
            pygame.draw.circle(WIN, projectile_color, (int(projectile[0]), int(projectile[1])), 5)
    for thing in thingy: 
        pygame.draw.rect(WIN, "blue", thing)
    pygame.display.update()
    
def check_collision(thingies, projectiles, score, thingy_count):
    for thingy in thingies[:]:  # Iterate over a copy of the list to avoid modification issues
        for projectile in projectiles:
            projectile_rect = pygame.Rect(projectile[0] - 5, projectile[1] - 5, 10, 10)
            if projectile_rect.colliderect(thingy):
                projectiles.remove(projectile)
                thingies.remove(thingy)
                score += 1
                thingy_count -= 1
                break  # Break the inner loop to avoid errors due to removing the projectile
    return score, thingies, thingy_count

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
    thingy= []
    clock = pygame.time.Clock()
    Player_moving = False  
    last_shot_time = 0
    shot_delay = 1000 
    score = 0
    thingy_count = 0

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
        
        
        score, thingy, thingy_count = check_collision(thingy, projectiles, score, thingy_count)
        score, thingy, thingy_count = check_collision(thingy, projectiles2, score, thingy_count)

        
        if thingy_count < 5:
            for _ in range(1):
                thingy_x = random.randint(0, WIDTH - thingy_width)
                thingy_y = random.randint(0, HEIGHT - thingy_height)
                thing = pygame.Rect(thingy_x, thingy_y, thingy_width, thingy_height)
                thingy.append(thing)
            thingy_count += 1
          
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