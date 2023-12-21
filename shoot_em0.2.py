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
thingy_count = 0
FONT = pygame.font.SysFont("comicsans", 30)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.rect = pygame.Rect(200, HEIGHT - 500, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.velocity = PLAYER_VEL
        self.player_pos = self.rect.centerx, self.rect.centery
        self.is_paused = False
    def move(self, keys, barriers):
        if keys[pygame.K_a]:  # Move left
            self.rect.x -= self.velocity
            if any(self.rect.colliderect(barrier.rect) for barrier in barriers):
                self.rect.x += self.velocity  # Undo movement if collision

        if keys[pygame.K_d]:  # Move right
            self.rect.x += self.velocity
            if any(self.rect.colliderect(barrier.rect) for barrier in barriers):
                self.rect.x -= self.velocity  # Undo movement if collision

        if keys[pygame.K_w]:  # Move up
            self.rect.y -= self.velocity
            if any(self.rect.colliderect(barrier.rect) for barrier in barriers):
                self.rect.y += self.velocity  # Undo movement if collision

        if keys[pygame.K_s]:  # Move down
            self.rect.y += self.velocity
            if any(self.rect.colliderect(barrier.rect) for barrier in barriers):
                self.rect.y -= self.velocity  # Undo movement if collision
            
        
    def get_pos(self):
        return self.player_pos
    def barrier_collision(self, barriers):
        for barrier in barriers:
            temp = self.rect.topleft
            if self.rect.colliderect(barrier.rect):
                self.player_collison_bar = True
                self.rect = pygame.Rect(temp, PLAYER_WIDTH, PLAYER_HEIGHT)
            
        
     

    

class Thingy(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, vel, type='normal'):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.type = type
        self.vel = vel
        self.thingy_pos = self.rect.centerx, self.rect.centery
        self.orbit_angle = 0
        

    def track_player(self, player):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)
        if distance != 0:  
            dx, dy = dx / distance, dy / distance
        self.rect.x += dx * self.vel
        self.rect.y += dy * self.vel   
    
    def track_player_shooter(self, player):
        if self.type == 'shooter':
            inreach = False
            radius = 300
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            distance = math.hypot(dx, dy)

            if distance > radius:
                if distance != 0:  
                    dx, dy = dx / distance, dy / distance
                
                self.rect.x += dx * self.vel
                self.rect.y += dy * self.vel
    
    def avoid_others(self, all_thingies):
        for other in all_thingies:
            if other != self and self.rect.colliderect(other.rect):
                dx = self.rect.centerx - other.rect.centerx
                dy = self.rect.centery - other.rect.centery
                distance = math.hypot(dx, dy)
                if distance == 0:
                    continue  # Avoid division by zero
                dx, dy = dx / distance, dy / distance
                self.rect.x += dx * self.vel
                self.rect.y += dy * self.vel
    
    def orbit_player(self, player, orbit_radius, orbit_speed):
        if self.type == 'shooter':
            # Increment the angle to move along the orbit
            self.orbit_angle += orbit_speed
            # Calculate new position
            self.rect.x = player.rect.centerx + math.cos(self.orbit_angle) * orbit_radius - self.rect.width / 2
            self.rect.y = player.rect.centery + math.sin(self.orbit_angle) * orbit_radius - self.rect.height / 2

    def get_pos(self):
        return self.thingy_pos
    

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy, speed):
        super().__init__()
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.speed = speed

    def move(self):
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

    def draw(self, surface):
        pygame.draw.circle(surface, "red", (int(self.x), int(self.y)), 5)

class Barrier(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.color = 'white'
    def draw(self, window):
        pygame.draw.rect(window, self.color, self.rect)


class ShootEmGame:
    def __init__(self):
        self.win = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Shoot_Em")
        self.bg = pygame.image.load("grass3.png").convert()
        self.bg = pygame.transform.scale(self.bg, (WIDTH, HEIGHT))
        self.player = Player()
        self.thingy = []
        self.projectiles = []
        self.projectiles2 = []
        self.barriers = [
            Barrier(0, 0, WIDTH, 10),  
            Barrier(0, HEIGHT - 10, WIDTH, 10),  
            Barrier(0, 0, 10, HEIGHT),  
            Barrier(WIDTH - 10, 0, 10, HEIGHT),  
            Barrier(200, 200, 30, 80)
        ]
        self.score = 0
        self.count = 0
        self.last_shot_time = 0
        self.last_shot_time2 = 0
        self.shot_delay = 1000
        self.spawn_timer = 0
        self.enemy_count = 0
          

    def run(self):
        clock = pygame.time.Clock()
        current_time = pygame.time.get_ticks()
        
        run = True

        while run:
            clock.tick(60)
            keys = pygame.key.get_pressed()
            player_moving = self.check_player_movement(keys)
            
            self.spawn_enemies()

            for thing in self.thingy:
                thing.avoid_others(self.thingy)
                if thing.type == 'normal':
                    Thingy.track_player(thing, self.player)
                else:
                    Thingy.track_player_shooter(thing, self.player)
                    #thing.orbit_player(self.player, orbit_radius=300, orbit_speed=0.005)  # adjust radius and speed as needed

                
            self.player.move(keys, self.barriers)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_shooting(player_moving)
                    
            
            current_time2 = pygame.time.get_ticks()
            if current_time2 - self.last_shot_time2 >= 1000:
                self.last_shot_time2 = current_time2
                self.thingy_shooting()
                
            
            
            self.update_projectiles()
            self.check_collisions()
            self.play_thingy_col()
            self.draw()

    def play_thingy_col(self):
        for thing in self.thingy:
            if self.player.rect.colliderect(thing):
                self.thingy.remove(thing)
                self.enemy_count -= 1
                self.count += 1

        

    def check_player_movement(self, keys):
        if keys[pygame.K_a] | keys[pygame.K_s] | keys[pygame.K_d] | keys[pygame.K_w]:
            Player_moving = True
        else:
            Player_moving = False
        return Player_moving
        
    def update_projectiles(self):
        for projectile in self.projectiles:
            projectile.move()
            if projectile.x < 0 or projectile.x > WIDTH or projectile.y < 0 or projectile.y > HEIGHT:
                self.projectiles.remove(projectile)
        for projectile in self.projectiles2:
            projectile.move()
            if projectile.x < 0 or projectile.x > WIDTH or projectile.y < 0 or projectile.y > HEIGHT:
                self.projectiles2.remove(projectile)
    
    def thingy_shooting(self):
        for thing in self.thingy:
            if thing.type == 'shooter':
                target_pos = self.player.rect.centerx, self.player.rect.centery
                starting_pos = thing.rect.centerx, thing.rect.centery
                self.projectiles2.append(self.create_projectile(starting_pos, target_pos, 5))
        


    def handle_shooting(self, player_moving):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= self.shot_delay:
            self.last_shot_time = current_time
            orbit_circle_pos = self.gun_position()
            target_pos = pygame.mouse.get_pos()
            if player_moving:
                projectile = self.create_projectile(orbit_circle_pos, target_pos, 10)
            else:
                projectile = self.create_projectile(orbit_circle_pos, target_pos, 5)
            self.projectiles.append(projectile)

    def gun_position(self):
        mx, my = pygame.mouse.get_pos()
        angle_to_mouse = math.atan2(my - self.player.rect.centery, mx - self.player.rect.centerx)
        orbit_distance = 60
        orbit_circle_x = int(self.player.rect.centerx + orbit_distance * math.cos(angle_to_mouse))
        orbit_circle_y = int(self.player.rect.centery + orbit_distance * math.sin(angle_to_mouse))
        return (orbit_circle_x, orbit_circle_y)

    def create_projectile(self, start_pos, target_pos, speed):
        dx, dy = target_pos[0] - start_pos[0], target_pos[1] - start_pos[1]
        distance = math.hypot(dx, dy)
        if distance == 0:
            distance = 1
        dx, dy = dx / distance, dy / distance
        return Projectile(start_pos[0], start_pos[1], dx, dy, speed)

    def check_collisions(self):
        # Check for projectile collisions with enemies
        for projectile in self.projectiles[:]:
            projectile_rect = pygame.Rect(projectile.x - 5, projectile.y - 5, 10, 10)
            for enemy in self.thingy[:]:
                if projectile_rect.colliderect(enemy.rect):
                    self.projectiles.remove(projectile)
                    self.thingy.remove(enemy)
                    self.score += 1
                    self.enemy_count -= 1
                    break 
        for projectile in self.projectiles2[:]:
            projectile_rect2 = pygame.Rect(projectile.x - 5, projectile.y - 5, 10, 10)
            if projectile_rect2.colliderect(self.player.rect):
                self.projectiles2.remove(projectile)
                self.count += 1
                break 

    def spawn_enemies(self):
        self.spawn_timer += 1
        if self.spawn_timer >= 1 and self.enemy_count < 5:
            x = random.randint(0, WIDTH - thingy_width)
            y = random.randint(0, HEIGHT - thingy_height)
            type = 'normal' if random.randint(0, 1) == 0 else 'shooter'
            enemy = Thingy(x, y, thingy_width, thingy_height, thingy_vel, type)
            self.thingy.append(enemy)
            self.enemy_count += 1
            self.spawn_timer = 0 

    def draw(self):
        self.win.blit(self.bg, (0, 0))
        pygame.draw.rect(self.win, "red", self.player.rect)
        pygame.draw.circle(WIN, (0, 255, 0), self.gun_position(), 10)
        for barrier in self.barriers:
            barrier.draw(self.win)
        for enemy in self.thingy:
            pygame.draw.rect(self.win, "blue" if enemy.type == 'normal' else "black", enemy.rect)
        for projectile in self.projectiles:
            projectile.draw(self.win)
        for projectile in self.projectiles2:
            projectile.draw(self.win)
        version_text = FONT.render("Version 0.2", 1, "white")
        count_text = FONT.render(str(self.count), 1, "white")
        score_text = FONT.render(str(self.score), 1, "white")
        self.win.blit(version_text, (1700, 10))
        self.win.blit(score_text, (20, 10))
        self.win.blit(count_text, (20, 40))
        pygame.display.update()

def main():
    game = ShootEmGame()
    game.run()

if __name__ == "__main__":
    main()