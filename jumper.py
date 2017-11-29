#!/usr/bin/env python

import sys, pygame, time, math, glob, random
from itertools import repeat
assert sys.version_info >= (3,4), 'This script requires at least Python 3.4'

screen_size = (500,750)
FPS = 30
gravity = (0.0, 3.0)

#
# Blockhead
#

def add_vectors(vect1, vect2):
        """ Returns the sum of two vectors """
        (angle1, length1) = vect1
        (angle2, length2) = vect2
        x  = math.sin(angle1) * length1 + math.sin(angle2) * length2
        y  = math.cos(angle1) * length1 + math.cos(angle2) * length2    
        angle  = 0.5 * math.pi - math.atan2(y, x)
        length = math.hypot(x, y)
        return (angle, length)


class World(pygame.sprite.Sprite):
        def __init__(self):
                pygame.sprite.Sprite.__init__(self)
                self.background_images = self.running_images = glob.glob("resources/background/bg*.png")
                self.background_images.sort()
                self.background = []
                w,h = screen_size
                for b in self.background_images:
                        img = pygame.image.load(b)
                        r = img.get_rect()
                        temp = [img,(0,0,w,r.height-2*h)]
                        self.background.append(temp)
                self.rect = pygame.Rect((0,0,w,h))
                self.image = pygame.Surface(self.rect.size).convert()


                
                self.image.blit(self.background[0][0], (0,0), self.background[0][1])
                #self.image.blit(self.background[1][0], (0,0), self.background[1][1])
                #self.image.blit(self.background[2][0], (0,0), self.background[2][1])
                #self.image.blit(self.background[3][0], (0,0), self.background[3][1])
                #self.image.blit(self.background[4][0], (0,0), self.background[4][1])

                
class Platform(pygame.sprite.Sprite):
        def __init__(self, x, y):
                pygame.sprite.Sprite.__init__(self)
                self.image = pygame.image.load("resources/Box.png")
                self.rect = self.image.get_rect()

                self.rect.y = y
                self.rect.x = x

                self.resetMargin = 20

        def update(self, speed):
                speedx,speedy = speed
                self.rect.x -= speedx
                self.rect.y -= speedy
                self.reset()

        def reset(self):
                if self.rect.y > screen_size[1] * 10:
                        self.rect.x = random.randrange(self.resetMargin, screen_size[0] - self.resetMargin)
                        self.rect.y = -self.resetMargin

class Player(pygame.sprite.Sprite):        
        def __init__(self, startingPosx = 50, jumpForce = 15):
                pygame.sprite.Sprite.__init__(self)
                self.jumpForce = jumpForce
                self.running_images = glob.glob("resources/character/square_*.png")
                
                self.running_images.sort()
                self.running = []
                for r in self.running_images:
                        temp = pygame.image.load(r)
                        self.running.append(temp)
                self.running_frame = 0
                self.image = self.running[self.running_frame]
                self.rect = self.image.get_rect()
                self.rect.x = startingPosx
                self.rect.y = 600
                self.originalRectY = self.rect.y
                self.speed = (0,0)
                self.normalSpeed = (0, 0)
                self.sprintSpeed = (0, -10)
                self.falling = False
                self.dead = False
                self.sprint = False
                self.jumpDecay = 1
                
                self.grounded = True
                self.groundedHeight = self.originalRectY

                self.timesDodged = 0                

                self.walkSpeed = 10
                self.currentSpeed = 0
                
                self.dy = 0

                self.last_update = pygame.time.get_ticks()
                self.last_update_speed = pygame.time.get_ticks()

        
        def update(self, speed = (0, 0)):
                if not self.dead:
                        now = pygame.time.get_ticks()
                        if now - self.last_update > FPS * 2:
                                self.last_update = now
                                self.running_frame = (self.running_frame + 1) % len(self.running)
                                self.image = self.running[self.running_frame]
                        if now - self.last_update_speed > FPS * (math.fabs(self.normalSpeed[1]) + 1) * 3:
                                self.last_update_speed = now
                                if self.normalSpeed[1] > -10:
                                        self.normalSpeed = (self.normalSpeed[0], self.normalSpeed[1] - 0.1)

                        if self.sprint:
                                self.speed = self.sprintSpeed
                        else:
                                self.speed = self.normalSpeed
                else:
                        self.speed = (0, 0)
                #self.rect.y == self.originalRectY
                        
                self.rect.centery += self.dy
                self.rect.centerx += self.currentSpeed

                if self.rect.right < 0:
                        self.rect.left = screen_size[0]
                if self.rect.left > screen_size[0]:
                        self.rect.right = 0
                
                if not self.grounded and not self.dead:
                        self.dy += self.jumpDecay
                #if self.grounded:
                #        self.rect.centery += self.speed[1]
                #        print(speed[1])
                if self.grounded and self.rect.bottom > self.groundedHeight and not self.falling:
                        self.rect.bottom = self.groundedHeight
                        self.dy = 0

                speedx,speedy = speed
                self.rect.x -= speedx
                self.rect.y -= speedy
                        
                #if self.falling:
                #        self.speed = add_vectors(self.speed,gravity)

        def walk(self, on, directionLeft):
                if on:
                        if directionLeft:
                                self.currentSpeed = -self.walkSpeed
                        else:
                                self.currentSpeed = self.walkSpeed
                else:
                        if (directionLeft and self.currentSpeed == -self.walkSpeed) or (not directionLeft and self.currentSpeed == self.walkSpeed):
                                self.currentSpeed = 0


        def jump(self):
                if not self.dead:
                        if self.grounded:
                                self.dy -= self.jumpForce
                                pygame.mixer.Sound("7967_cfork_boing-raw.ogg").play()

        def reset(self):
                if self.rect.x < -150:
                        self.rect.x = random.randrange(1000, 2000)
                        self.timesDodged += 1
        
# this function creates our shake-generator
# it "moves" the screen to the left and right
# three times by yielding (-5, 0), (-10, 0),
# ... (-20, 0), (-15, 0) ... (20, 0) three times,
# then keeps yieling (0, 0)
def shake():
	s = -1
	for _ in range(0, 3):
		for x in range(0, 20, 5):
			yield (x*s, 0)
		for x in range(20, 0, 5):
			yield (x*s, 0)
		s *= -1
	while True:
		yield (0, 0)

def main():
        pygame.init()
        screen = pygame.display.set_mode(screen_size)
        clock = pygame.time.Clock()

        org_screen = pygame.display.set_mode(screen_size)
        screen = org_screen.copy()
        # 'offset' will be our generator that produces the offset
        # in the beginning of screen shake, we start with a generator that 
        # yields (0, 0) forever
        offset = repeat((0, 0))

        if not pygame.mixer:
                pygame.mixer.init(frequency=ogg.info.sample_rate)
        pygame.mixer.stop()
        pygame.mixer.Sound("Bama_Country.ogg").play(-1)

        world = pygame.sprite.Group()
        world.add(World())
        
        player = Player()
        players = pygame.sprite.Group()
        players.add(player)
        
        platforms = pygame.sprite.Group()
        platforms.add(Platform(50, 730))
        platformHeight = 0
        while platformHeight <= screen_size[1] * 10:
                p = Platform(random.randrange(25, screen_size[0] - 25), platformHeight)
                platforms.add(p)
                platformHeight += random.randrange(50, 150)

        keepPlaying = True

        while keepPlaying:
                clock.tick(FPS)
                screen.fill((0,0,0))
                for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit(0)
                        if event.type == pygame.MOUSEMOTION:
                                pos = pygame.mouse.get_pos()
                        if event.type == pygame.MOUSEBUTTONUP:
                                pos = pygame.mouse.get_pos()
                                #player.sprint = False
                        if event.type == pygame.MOUSEBUTTONDOWN:
                                pos = pygame.mouse.get_pos()
                                #player.sprint = True
                                if player.dead:
                                        keepPlaying = False
                        if event.type == pygame.KEYDOWN:
                                keys = pygame.key.get_pressed()
                                if event.key == pygame.K_a:
                                        player.walk(True, True)
                                if event.key == pygame.K_d:
                                        player.walk(True, False)
                                if event.key != pygame.K_a and event.key != pygame.K_d:
                                        #print("jump...")
                                        player.jump()
                                if player.dead:
                                        keepPlaying = False
                        if event.type == pygame.KEYUP:
                                if event.key == pygame.K_a:
                                        player.walk(False, True)
                                if event.key == pygame.K_d:
                                        player.walk(False, False)

                pGroundedThisUpdate = False
                for p in platforms:
                        if (player.rect.bottom >= p.rect.top and player.rect.bottom <= p.rect.bottom) and (player.rect.right > p.rect.x and player.rect.left < (p.rect.x + p.rect.width)):
                                pGroundedThisUpdate = True
                                player.grounded = True
                                player.groundedHeight = p.rect.top
                                #print("GROUND!")
                if not pGroundedThisUpdate:
                        player.grounded = False
                        player.groundedHeight = 0

                if player.rect.top > screen_size[1] and not player.dead:
                        player.falling = True
                        player.dead = True
                        player.dy = 15
                        pygame.mixer.Sound("goofy-yell.ogg").play()
                        offset = shake() #create a new shake-generator
                        org_screen.blit(screen, next(offset))

                world.update(player.speed)
                world.draw(screen)

                platforms.update(player.speed)
                platforms.draw(screen)

                players.update(player.speed)
                players.draw(screen)

                org_screen.blit(screen, next(offset))

                pygame.display.flip()

if __name__ == '__main__':
        while True:
                main()
