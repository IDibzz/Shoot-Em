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
        self.rect = pygame.Rect(200, HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.velocity = PLAYER_VEL
    def move(self, keys):
        if keys[pygame.K_a] and self.rect.x - self.velocity >= 0:
            self.rect.x -= self.velocity
        if keys[pygame.K_d] and self.rect.x + self.velocity + self.rect.width <= WIDTH:
            self.rect.x += self.velocity
        if keys[pygame.K_w] and self.rect.y - self.velocity >= 0:
            self.rect.y -= self.velocity
        if keys[pygame.K_s] and self.rect.y + self.velocity + self.rect.height <= HEIGHT:
            self.rect.y += self.velocity
    

class Thingy(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, vel, type='normal'):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.type = type
        self.vel = vel

    def track_player(self, player):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)
        if distance != 0:  
            dx, dy = dx / distance, dy / distance
        self.rect.x += dx * self.vel
        self.rect.y += dy * self.vel   

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

class ShootEmGame:
    def __init__(self):
        self.win = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Shoot_Em")
        self.bg = pygame.image.load("grass3.png").convert()
        self.bg = pygame.transform.scale(self.bg, (WIDTH, HEIGHT))
        self.player = Player()
        self.thingy = []
        self.projectiles = []
        self.score = 0
        self.count = 0
        self.last_shot_time = 0
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
                Thingy.track_player(thing, self.player)
            
            Player.move(self.player, keys)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_shooting(player_moving)
                    
            self.update_projectiles()
            self.check_collisions()
            self.play_thingy_col()
            self.draw()

    def play_thingy_col(self):
        for thing in self.thingy:
            if self.player.rect.colliderect(thing):
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
        
    def spawn_enemies(self):
        self.spawn_timer += 1
        if self.spawn_timer >= 1 and self.enemy_count < 5:
            x = random.randint(0, WIDTH - thingy_width)
            y = random.randint(0, HEIGHT - thingy_height)
            type = 'normal' #if random.randint(0, 1) == 0 else 'shooter'
            enemy = Thingy(x, y, thingy_width, thingy_height, thingy_vel, type)
            self.thingy.append(enemy)
            self.enemy_count += 1
            self.spawn_timer = 0 

    def draw(self):
        self.win.blit(self.bg, (0, 0))
        pygame.draw.rect(self.win, "red", self.player.rect)
        pygame.draw.circle(WIN, (0, 255, 0), self.gun_position(), 10)
        for enemy in self.thingy:
            pygame.draw.rect(self.win, "blue" if enemy.type == 'normal' else "black", enemy.rect)
        for projectile in self.projectiles:
            projectile.draw(self.win)
        count_text = FONT.render(str(self.count), 1, "white")
        score_text = FONT.render(str(self.score), 1, "white")
        self.win.blit(score_text, (10, 10))
        self.win.blit(count_text, (10, 40))
        pygame.display.update()

def main():
    game = ShootEmGame()
    game.run()

if __name__ == "__main__":
    main()



















