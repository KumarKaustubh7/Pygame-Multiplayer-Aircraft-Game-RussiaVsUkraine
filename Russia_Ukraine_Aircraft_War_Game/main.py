import pygame
import os

pygame.font.init()

#Create Window
WIDTH, HEIGHT = 1150,750
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Multiplayer Air Battle between Russia and Ukraine")  #Setting name of our window

#Loading ukraine ship
UKRAINE_SHIP = pygame.image.load(os.path.join("asset","ukraine_ship.png"))

#Loading russian ship
RUSSIAN_SHIP = pygame.image.load(os.path.join("asset","russian_ship.png"))

#Load Fire
FIRE_UKRAINE = pygame.image.load(os.path.join("asset","fire_ukraine.png"))

FIRE_RUSSIA = pygame.image.load(os.path.join("asset","fire_russia.png"))

#Load Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("asset","background_sky.png")), (WIDTH,HEIGHT))  #scaling so to make background fit the screen size

class Fire:
    def __init__(self, x, y, img):          #To initialize (x,y) coordinate for release of fire.
        self.x = x + 75
        self.y = y + 57
        self.img = img                      #To call its image
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):                 #to show the fire on screen
        window.blit(self.img, (self.x,self.y))

    def moveR(self, vel):                   #movement of russian fire
        self.x += vel
    def moveU(self, vel):                   #movement of ukrainian fire
        self.x -= vel

    def off_screen(self, width):            #check if fire left the screen
        return not(self.x <= width and self.x >=0)   #if not on screen

    def collision(self, obj):               #if the aircraft collided with the enemy fire
        return collide(self, obj)


class Ship:         #abstract class
    COOLDOWN = 30   # half of sec, so I can fire 2 times a sec

    def __init__(self, x, y, health = 100):         #Each ship has x,y cordinate and health
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.fire_img = None
        self.fires = []
        self.cool_down_counter = 0              #To add wait time between two fire

    def draw(self, window):         #window to tell where are we putting it.
        window.blit(self.ship_img, (self.x, self.y))    #putting the aircraft at (x,y)
        for fire in self.fires:     #draw the fire on screen which are in fires list
            fire.draw(window)


    def move_fire(self, vel, obj):
        self.cooldown()
        for fire in self.fires:
            fire.move(vel)          #move fire with velocity
            if fire.off_screen(WIDTH):  #if fire crossed width remove them
                self.fires.remove(fire)
            elif fire.collision(obj):   #if fire collided with our object reduce its health
                obj.health -=10
                self.fires.remove(fire) #and then remove that fire


    def cooldown(self): #handling cool_down_counter
        if self.cool_down_counter>=self.COOLDOWN:       #if cool_down_counter is 0 then nothing
            self.cool_down_counter =0
        elif self.cool_down_counter > 0:                #but if >0 and not passed the time limit of COOLDOWN, increment it by 1
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:     #not in the process of keeping how long till the next shot
            fire = Fire(self.x, self.y, self.fire_img)  #if cool_down_counter is 0 then we can fire or add fire in the list
            self.fires.append(fire)         #adding fire to the fires list
            self.cool_down_counter = 1      #it will now count up, now in next turn cool_down_counter is greater than COOLDOWN
                             #so as per the cooldown function if cond it will decrease to 0 and we can shoot again after half a sec.

    def get_width(self):                #get width of the ship
        return self.ship_img.get_width()

    def get_height(self):               #get height of the ship
        return self.ship_img.get_height()



class PlayerRussia(Ship):
    def __init__(self, x, y, health = 100):
        super().__init__(x, y, health)
        self.ship_img = RUSSIAN_SHIP
        self.fire_img = FIRE_RUSSIA
        self.mask = pygame.mask.from_surface(self.ship_img)   #to ensure bullet is hitting the mask of then ship,mask will cover the image borders
        self.health = health        #the initial health is maximum health i.e. 100

    def move_fire(self, vel, obj):          #method overriding
        self.cooldown()                 #if we can fire or not
        for fire in self.fires:         #if fires have elements then move them as per move function
            fire.moveR(vel)          #move fire with velocity
            if fire.off_screen(WIDTH):  #if fire crossed width remove them
                self.fires.remove(fire)
            if fire.collision(obj):   #if fire collided with our object reduce its health
                obj.health -=10
                self.fires.remove(fire) #and then remove that fire


    def draw(self, window):         #draw function of russian aircraft
        super().draw(window)        #overloading the draw function of Ship class
        self.healthbar(window)

    def healthbar(self, window):        #shows the rectangles as health bar and will decrease if hit.
        pygame.draw.rect(window, (255, 0, 0),(10,70, 100, 10))      #RED
        pygame.draw.rect(window, (0, 255, 0), (10,70, self.health,10))      #Green




class PlayerUkraine(Ship):
    def __init__(self, x, y, health = 100):
        super().__init__(x, y, health)
        self.ship_img = UKRAINE_SHIP
        self.fire_img = FIRE_UKRAINE
        self.mask = pygame.mask.from_surface(self.ship_img)   #to ensure bullet is hitting the mask of then ship,mask will cover the image borders
        self.health = health        #the initial health is maximum health

    def draw(self, window):     #will draw the healthbar on the screen
        super().draw(window)        #will draw the fire on the screen
        self.healthbar(window)

    def healthbar(self, window):        #show the healthbar
        pygame.draw.rect(window, (255, 0, 0),(1040, 70, 100, 10))       #Red rectangle
        pygame.draw.rect(window, (0, 255, 0), (1040,70, self.health,10))        #Green rectangle

    def move_fire(self, vel, obj):
        self.cooldown()
        for fire in self.fires:
            fire.moveU(vel)  # move fire with velocity
            if fire.off_screen(WIDTH):  # if fire crossed width remove them
                self.fires.remove(fire)
            if fire.collision(obj):   #if fire collided with our object reduce its health
                obj.health -=10
                self.fires.remove(fire) #and then remove that fire



def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None   #if pixels of object 2 is overlapping wth mask of aircraft


def main():         #main loop of the game
    run = True          #game will wun
    FPS = 60        #Frames per second
    russianP = 'Sukhoi Su-24'
    ukraineP = 'F-35 Lightning II'
    lifeR = 1       #Both the aircrafts have single life
    lifeU = 1

    main_font = pygame.font.SysFont("comicsans", 30)    #setting font for labels above
    lost_font = pygame.font.SysFont("comicsans", 30)    #setting font for lost message

    playerR_vel = 5    #velocity of Russian plane
    playerU_vel = 5    #velocity of ukrainian plane

    fire_vel = 6        #velocity of fire

    playerR = PlayerRussia(50,250)      #initialize the russian ship coordinates
    playerU = PlayerUkraine(950,350)    #initialize the ukrainian ship coordinates

    clock = pygame.time.Clock()     #for checking the collisions/movement once in FPS

    lostR = False          #Russian loss
    lostR_count = 0         #for showing lost message for certain time

    lostU = False          #Ukrainian loss
    lostU_count = 0  # for showing lost message for certain time

    def redraw_window():
        WIN.blit(BG,(0,0))          #bring the backgroung image to the location (0,0) top left to fill the screen
        #draw text
        russianP_label = main_font.render(f"Russian aircraft: {russianP}", 1, (255,255,255))
        ukraineP_label = main_font.render(f"Ukrainian aircraft: {ukraineP}", 1, (255,255,255))

        WIN.blit(russianP_label,(10,10))            #showing russian and ukrainian labels
        WIN.blit(ukraineP_label,(WIDTH - ukraineP_label.get_width()-10,10))

        playerR.draw(WIN)       #drawing the russian plane
        playerU.draw(WIN)       #drawing the ukrainian plane

        if lostR:       #To show lost message
            lost_label = lost_font.render("Russia lost!!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        if lostU:       #To show lost message
            lost_label = lost_font.render("Ukraine lost!!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 350))

        pygame.display.update()     #Refresh the display


    while run:          #while the game loop is running
        clock.tick(FPS)     #run the clock on FPS so that game is consistent(60sec) on the device
        redraw_window()

        if lifeR == 0 or playerR.health <= 0:
            lostR = True
            lostR_count += 1
        if lostR:                              #showing the lost message
            if lostR_count > FPS * 6 :      #frames per sec x 6 for showing 10 sec
                run = False
            else:
                continue

        if lifeU == 0 or playerU.health <= 0:
            lostU = True
            lostU_count += 1
        if lostU:                              #showing the lost message
            if lostU_count > FPS * 6 :      #frames per sec x 10 for showing 10 sec
                run = False
            else:
                continue



        for event in pygame.event.get():        #check if event occured
             if event.type == pygame.QUIT:      #If Quit selected
                quit()                     #No more looping through


        #to move russian player ship
        keys = pygame.key.get_pressed()      #dict of all keys present or not which we will check if key is pressed or not to move.
        if keys[pygame.K_a] and playerR.x - playerR_vel>0:              #left move
            playerR.x -= playerR_vel
        if keys[pygame.K_d] and playerR.x + playerR_vel + playerR.get_width() <WIDTH:          #move right
            playerR.x += playerR_vel
        if keys[pygame.K_w] and playerR.y - playerR_vel>0:              #move up
            playerR.y -= playerR_vel
        if keys[pygame.K_s] and playerR.y + playerR_vel + playerR.get_height() < HEIGHT:       #move down
            playerR.y += playerR_vel
        if keys[pygame.K_SPACE]:
            playerR.shoot()


        #to move ukrainian player ship
        keys1 = pygame.key.get_pressed()     ##dict of all keys present or not which we will check if key is pressed or not to move.
        if keys1[pygame.K_j] and playerU.x - playerU_vel > 0:          #move bottom
            playerU.x -= playerU_vel
        if keys1[pygame.K_l] and playerU.x + playerU_vel + playerU.get_width() <WIDTH:          #move right
            playerU.x += playerU_vel
        if keys1[pygame.K_i] and playerU.y - playerU_vel>0:              #move up
            playerU.y -= playerU_vel
        if keys1[pygame.K_k] and playerU.y + playerU_vel + playerU.get_height() < HEIGHT:       #move down
            playerU.y += playerU_vel
        if keys[pygame.K_BACKSPACE]:
            playerU.shoot()


        playerR.move_fire(fire_vel, playerU)
        playerU.move_fire(fire_vel, playerR)

main()