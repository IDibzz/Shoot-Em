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
pygame.display.set_caption("Shoot_Em")

BG = pygame.transform.scale(pygame.image.load("grass3.png"), (WIDTH,HEIGHT))

pygame.event.set_grab(True)

PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
PLAYER_VEL = 5

projectiles = []
projectiles2 = []

thingy_projectile = []

projectile_color = (255, 0, 0)
projectile_speed = 5
projectile_speed2 = 10

thingy_vel = 3
thingy_width = 20
thingy_height = 10
FONT = pygame.font.SysFont("comicsans", 30)
#renders everything to screen
def draw(player, Player_moving, thingy, score, orbit_circle_pos, count2, thingy2):
    WIN.blit(BG, (0,0))
    
    
    pygame.draw.circle(WIN, (0, 255, 0), orbit_circle_pos, 10)
    
    pygame.draw.rect(WIN, "red", player)
    version_text = FONT.render("Version 0.1", 1, "white")
    WIN.blit(version_text, (1750, 10))
    collisions = FONT.render(str(count2), 1, "white")
    score_text = FONT.render(str(score), 1, "white")
    WIN.blit(score_text, (10,10))
    WIN.blit(collisions, (10,40))
    for projectile in projectiles2:
        pygame.draw.circle(WIN, projectile_color, (int(projectile[0]), int(projectile[1])), 5)
    for projectile in projectiles:
        pygame.draw.circle(WIN, projectile_color, (int(projectile[0]), int(projectile[1])), 5)
    for projectile in thingy_projectile:
        pygame.draw.circle(WIN, projectile_color, (int(projectile[0]), int(projectile[1])), 5)
    for thing in thingy: 
        pygame.draw.rect(WIN, "blue", thing)
    for thing in thingy2: 
        pygame.draw.rect(WIN, "black", thing)
    pygame.display.update()

#general enemy behavoir: following you trying to touch you to kill you
def thingy_tracking(player, thingy, thingy_vel):
    for thing in thingy:
        dx = player.centerx - thing.centerx
        dy = player.centery - thing.centery
        distance = math.hypot(dx, dy)
        if distance != 0:  
            dx, dy = dx / distance, dy / distance
        thing.x += dx * thingy_vel
        thing.y += dy * thingy_vel
def thingy_tracking2(player, thingy, thingy_vel):
    radius = 300
    
    for thing in thingy:
        dx = player.centerx - thing.centerx
        dy = player.centery - thing.centery
        distance = math.hypot(dx, dy)

        if distance > radius:
            if distance != 0:  
                dx, dy = dx / distance, dy / distance
            thing.x += dx * thingy_vel
            thing.y += dy * thingy_vel
        
            

#enemy behavior to thingys that have guns (need to add "gun", and radius that they can not pass to player)
def thingy_2(thingy, player_pos):
    for thing in thingy:
        thingy_pos = thing.centerx, thing.centery
        thingy_projectile.append(add_projectile(thingy_pos, player_pos))

#postition of gun for player
def gun_position(player, orbit_distance):
    mx, my = pygame.mouse.get_pos()  
    angle_to_mouse = math.atan2(my - player.centery, mx - player.centerx)
    orbit_circle_x = int(player.centerx + orbit_distance * math.cos(angle_to_mouse))
    orbit_circle_y = int(player.centery + orbit_distance * math.sin(angle_to_mouse))
    orbit_circle_pos = (orbit_circle_x, orbit_circle_y)
    return orbit_circle_pos

#fix this once base game is done so it take you to menu or death screen or whatever
def play_thingy_col(player, thingy, count):
    for thing in thingy:
        if player.colliderect(thing):
            count += 1
    return count

#checks collisions fo proejctiles from player to thingys and thingy2
def check_collision(thingies, projectiles, score, thingy_count):
    for thingy in thingies[:]:  
        for projectile in projectiles:
            projectile_rect = pygame.Rect(projectile[0] - 5, projectile[1] - 5, 10, 10)
            if projectile_rect.colliderect(thingy):
                projectiles.remove(projectile)
                thingies.remove(thingy)
                score += 1
                thingy_count -= 1
                break  
    return score, thingies, thingy_count

#checks if collisions from thingy2 projectile hit player
def check_player_col(player, thingy_projectile, count2):
    for projectile in  thingy_projectile:
        projectile_rect = pygame.Rect(projectile[0] - 5, projectile[1] - 5, 10, 10)
        if projectile_rect.colliderect(player):
                thingy_projectile.remove(projectile)
                #thingies.remove(thingy) eventually change to player
                count2 += 1
                break  
    return count2

#litteraly just add prjectiles to the list to then render on screen
def add_projectile(player_pos, target_pos):
    dx, dy = target_pos[0] - player_pos[0], target_pos[1] - player_pos[1]
    distance = math.hypot(dx, dy)
    if distance == 0:  
        distance = 1
    dx, dy = dx / distance, dy / distance  
    return [player_pos[0], player_pos[1], dx, dy]

def main():
    run = True
    player = pygame.Rect(200,HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
    thingy= []
    thingy2 = []
    clock = pygame.time.Clock()
    Player_moving = False  
    last_shot_time = 0
    last_shot_time2 = 0
    shot_delay = 1000 
    score = 0
    thingy_count = 0
    orbit_distance = 60
    count2 = 0
    

    while run:
        clock.tick(60)
        player_pos = player.centerx, player.centery
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        orbit_circle_pos = gun_position(player, orbit_distance)
        
        thingy_tracking(player, thingy, thingy_vel)
        thingy_tracking2(player, thingy2, thingy_vel)
        
        
        if keys[pygame.K_a] | keys[pygame.K_s] | keys[pygame.K_d] | keys[pygame.K_w]:
            Player_moving = True
        else:
            Player_moving = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
            
                current_time = pygame.time.get_ticks()
                if current_time - last_shot_time >= shot_delay:
                    last_shot_time = current_time
                    if Player_moving:
                        projectiles2.append(add_projectile(orbit_circle_pos, pygame.mouse.get_pos())) 
                    else:
                        projectiles.append(add_projectile(orbit_circle_pos, pygame.mouse.get_pos()))  

        current_time2 = pygame.time.get_ticks()
        if current_time2 - last_shot_time2 >= shot_delay:
            last_shot_time2 = current_time2
            thingy_2(thingy2, player_pos)

        for projectile in thingy_projectile:
            projectile[0] += projectile[2] * projectile_speed
            projectile[1] += projectile[3] * projectile_speed
        for projectile in projectiles2:
            projectile[0] += projectile[2] * projectile_speed2
            projectile[1] += projectile[3] * projectile_speed2
        for projectile in projectiles:
             projectile[0] += projectile[2] * projectile_speed
             projectile[1] += projectile[3] * projectile_speed
        
        score, thingy, thingy_count = check_collision(thingy, projectiles, score, thingy_count)
        score, thingy, thingy_count = check_collision(thingy, projectiles2, score, thingy_count)
        score, thingy2, thingy_count = check_collision(thingy2, projectiles, score, thingy_count)
        score, thingy2, thingy_count = check_collision(thingy2, projectiles2, score, thingy_count)
        count2 = check_player_col(player, thingy_projectile, count2)
        
        if thingy_count < 5:
            
            for _ in range(1):
                int1 = random.randint(0,5)
                thingy_x = random.randint(0, WIDTH - thingy_width)
                thingy_y = random.randint(0, HEIGHT - thingy_height)
                thing = pygame.Rect(thingy_x, thingy_y, thingy_width, thingy_height)
                if int1 == 1:
                    thingy2.append(thing)
                else:
                    thingy.append(thing)
            thingy_count += 1
        
        count2 = play_thingy_col(player, thingy, count2)
    
        if keys[pygame.K_a] and player.x - PLAYER_VEL >= 0:
            player.x -= PLAYER_VEL
        if keys[pygame.K_d] and player.x + PLAYER_VEL + player.width <= WIDTH:
            player.x += PLAYER_VEL
        if keys[pygame.K_w] and player.y - PLAYER_VEL >= 0:
            player.y -= PLAYER_VEL
        if keys[pygame.K_s] and player.y + PLAYER_VEL + player.height <= HEIGHT:
            player.y += PLAYER_VEL
        draw(player, Player_moving, thingy, score, orbit_circle_pos, count2, thingy2)

if __name__ == "__main__":
    main() 