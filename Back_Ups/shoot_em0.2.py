import pygame 
import time
import random
import json
import os
import re
import math
import heapq





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
        
    def move_with_collision(self, barriers):
        # Store original position
        original_position = self.rect.topleft


        # Check for collisions with barriers
        for barrier in barriers:
            if self.rect.colliderect(barrier.rect):
                # Collision detected, move back to original position
                self.rect.topleft = original_position
                # Implement logic to navigate around the barrier
                self.navigate_around_barrier(barrier)

    def navigate_around_barrier(self, barrier):
        # This is a simple navigation logic. You can enhance it based on your game's needs.
        if self.rect.centerx < barrier.rect.centerx:
            self.rect.x -= self.vel
        else:
            self.rect.x += self.vel
        if self.rect.centery < barrier.rect.centery:
            self.rect.y -= self.vel
        else:
            self.rect.y += self.vel
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
    def is_close_to_barrier(self, barriers, threshold=80):
        for barrier in barriers:
            # Calculate the distance between the closest edges of the Thingy and the barrier
            distance_x = max(barrier.rect.left - self.rect.right, self.rect.left - barrier.rect.right, 0)
            distance_y = max(barrier.rect.top - self.rect.bottom, self.rect.top - barrier.rect.bottom, 0)

            distance = math.sqrt(distance_x ** 2 + distance_y ** 2)

            if distance <= threshold:
                return True  # Thingy is within threshold distance of a barrier
        return False  # Thingy is not close to any barrier
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
            Barrier(0, 0, WIDTH, 40),  
            Barrier(0, HEIGHT - 40, WIDTH, 40),  
            Barrier(0, 0, 40, HEIGHT),  
            Barrier(WIDTH - 40, 0, 40, HEIGHT),  
            Barrier(200,200, 200, 200)
        ]
        self.score = 0
        self.count = 0
        self.last_shot_time = 0
        self.last_shot_time2 = 0
        self.shot_delay = 1000
        self.spawn_timer = 0
        self.enemy_count = 0
        self.within_dis = False
          

    def run(self):
        clock = pygame.time.Clock()
        current_time = pygame.time.get_ticks()
        grid = self.create_grid(WIDTH, HEIGHT, self.barriers, 40)
        run = True

        while run:
            clock.tick(60)
            keys = pygame.key.get_pressed()
            player_moving = self.check_player_movement(keys)
            
            self.spawn_enemies()
            
            for thing in self.thingy:
                if thing.is_close_to_barrier(self.barriers):
                    thing.avoid_others(self.thingy)
                    self.update(self.player, grid, 40, thing)
                else:
                    thing.avoid_others(self.thingy)
                    if thing.type == 'normal':
                        Thingy.track_player(thing, self.player)
                    else:
                        Thingy.track_player_shooter(thing, self.player)
                        #thing.orbit_player(self.player, orbit_radius=300, orbit_speed=0.005)  # adjust radius and speed as needed

            '''for thing in self.thingy:
                self.update(self.player, grid, 40, thing)
            
            for thing in self.thingy:
                thing.avoid_others(self.thingy)
                if thing.type == 'normal':
                    Thingy.track_player(thing, self.player)
                else:
                    Thingy.track_player_shooter(thing, self.player)
                    #thing.orbit_player(self.player, orbit_radius=300, orbit_speed=0.005)  # adjust radius and speed as needed'''
            
            
                

                
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
    
    def update(self, player, grid, cell_size, thing):
        start = (thing.rect.x // cell_size, thing.rect.y // cell_size)
        goal = (player.rect.x // cell_size, player.rect.y // cell_size)
        path = self.a_star_search(grid, start, goal)
        if path and len(path) > 1:  # Check if a path exists and has more than one point
            # Move towards the next point on the path
            next_cell = path[1]  # path[0] is the current cell, so we look at path[1]
            next_x, next_y = next_cell[0] * cell_size, next_cell[1] * cell_size

            # Adjust thingy's position to move towards next cell
            if thing.rect.x < next_x:
                thing.rect.x += min(thing.vel, next_x - thing.rect.x)
            elif thing.rect.x > next_x:
                thing.rect.x -= min(thing.vel, thing.rect.x - next_x)
            
            if thing.rect.y < next_y:
                thing.rect.y += min(thing.vel, next_y - thing.rect.y)
            elif thing.rect.y > next_y:
                thing.rect.y -= min(thing.vel, thing.rect.y - next_y)
    
    def create_grid(self, width, height, barriers, cell_size):
        grid = [[0 for _ in range(height // cell_size)] for _ in range(width // cell_size)]
        for barrier in barriers:
            x_start = barrier.rect.x // cell_size
            y_start = barrier.rect.y // cell_size
            x_end = (barrier.rect.x + barrier.rect.width) // cell_size
            y_end = (barrier.rect.y + barrier.rect.height) // cell_size
            for x in range(x_start, x_end):
                for y in range(y_start, y_end):
                    grid[x][y] = 1  # Mark barrier cells as blocked
        return grid
    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def a_star_search(self, grid, start, goal):
        # Priority queue
        frontier = []
        heapq.heappush(frontier, (0, start))
        
        came_from = {start: None}
        cost_so_far = {start: 0}

        while frontier:
            current = heapq.heappop(frontier)[1]

            if current == goal:
                break

            for next in self.neighbors(grid, current):
                new_cost = cost_so_far[current] + 1
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristic(goal, next)
                    heapq.heappush(frontier, (priority, next))
                    came_from[next] = current

        return self.reconstruct_path(came_from, start, goal)

    def neighbors(self, grid, node):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Four directions: up, right, down, left
        result = []
        for dir in directions:
            next = (node[0] + dir[0], node[1] + dir[1])
            if 0 <= next[0] < len(grid) and 0 <= next[1] < len(grid[0]) and grid[next[0]][next[1]] == 0:
                result.append(next)
        return result

    def reconstruct_path(self, came_from, start, goal):
        path = []
        current = goal
        while current != start:
            if current not in came_from:
                return []  # Return an empty path if the goal is unreachable
            path.append(current)
            current = came_from[current]
        path.append(start)  # Optional
        path.reverse()  # Optional
        return path
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
            for barrier in self.barriers:
                if projectile_rect.colliderect(barrier.rect):
                    self.projectiles.remove(projectile)
        for projectile in self.projectiles2[:]:
            projectile_rect2 = pygame.Rect(projectile.x - 5, projectile.y - 5, 10, 10)
            if projectile_rect2.colliderect(self.player.rect):
                self.projectiles2.remove(projectile)
                self.count += 1
                break 
            for barrier in self.barriers:
                if projectile_rect2.colliderect(barrier.rect):
                    self.projectiles2.remove(projectile)
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
        self.win.blit(version_text, (1650, 40))
        self.win.blit(score_text, (60, 40))
        self.win.blit(count_text, (60, 70))
        pygame.display.update()

def main():
    game = ShootEmGame()
    game.run()

if __name__ == "__main__":
    main()