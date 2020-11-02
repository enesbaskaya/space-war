import pygame
import os
import random

pygame.font.init()

# pencere boyutları ve başlığı
width = 750
height = 750
gameWindow = pygame.display.set_mode((width, height))
pygame.display.set_caption("Space Shooter Tutorial")

# warships load images
redSpaceShip = pygame.image.load(os.path.join("assets", "shipRed.png"))
greenSpaceShip = pygame.image.load(os.path.join("assets", "shipGreen.png"))
blueSpaceShip = pygame.image.load(os.path.join("assets", "shipBlue.png"))

# player ship image
yellowSpaceShip = pygame.image.load(os.path.join("assets", "shipYellow.png"))

# laser
redLaser = pygame.image.load(os.path.join("assets", "laserRed.png"))
yellowLaser = pygame.image.load(os.path.join("assets", "laserYellow.png"))
greenLaser = pygame.image.load(os.path.join("assets", "laserGreen.png"))
blueLaser = pygame.image.load(os.path.join("assets", "laserBlue.png"))

# backgroun image
bg = pygame.transform.scale(pygame.image.load(os.path.join("assets", "bgImage.png")), (width, height))


# lazer özellikleri
class Laser:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, window):
        window.blit(self.image, (self.x, self.y))

    def move(self, movement):
        self.y += movement

    def offScreen(self, height):
        return not (self.y <= height and self.y >= 0)

    def shipCollision(self, obj):
        return shipCollide(self, obj)


# gemi özellikleri
class Ship:
    coolDownL = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.shipImg = None
        self.laserImg = None
        self.lasers = []
        self.coolDownCounter = 0

    def draw(self, window):
        window.blit(self.shipImg, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def moveLasers(self, movement, obj):
        self.coolDown()
        for laser in self.lasers:
            laser.move(movement)
            if laser.offScreen(height):
                self.lasers.remove(laser)
            elif laser.shipCollision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def coolDown(self):
        if self.coolDownCounter <= self.coolDownL:
            self.coolDownCounter = 0
        elif self.coolDownCounter > 0:
            self.coolDownCounter += 1

    def shoot(self):
        if self.coolDownCounter == 0:
            laser = Laser(self.x, self.y, self.laserImg)
            self.lasers.append(laser)
            self.coolDownCounter = 1

    def getWidth(self):
        return self.shipImg.get_width()

    def getHeight(self):
        return self.shipImg.get_height()


# oyuncu özellikleri
class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.shipImg = yellowSpaceShip
        self.laserImg = yellowLaser
        self.mask = pygame.mask.from_surface(self.shipImg)
        self.maxHealth = health

    def moveLasers(self, movement, objs):
        self.coolDown()
        for laser in self.lasers:
            laser.move(movement)
            if laser.offScreen(height):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.shipCollision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthBar(window)

    def healthBar(self, window):
        pygame.draw.rect(window, (255, 0, 0),
                         (self.x, self.y + self.shipImg.get_height() + 10, self.shipImg.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0),
                         (self.x, self.y + self.shipImg.get_height() + 10,
                          self.shipImg.get_width() * (1 - ((self.maxHealth - self.health) / self.maxHealth)), 10))


# düşman gemilerinin özellikleri
class EnemyShip(Ship):
    enemyColorMap = {
        "redEnemy": (redSpaceShip, redLaser),
        "greenEnemy": (greenSpaceShip, greenLaser),
        "blueEnemy": (blueSpaceShip, blueLaser)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.shipImg, self.laserImg = self.enemyColorMap[color]
        self.mask = pygame.mask.from_surface(self.shipImg)

    def move(self, movement):
        self.y += movement

    def shoot(self):
        if self.coolDownCounter == 0:
            laser = Laser(self.x - 15, self.y, self.laserImg)
            self.lasers.append(laser)
            self.coolDownCounter = 1


def shipCollide(obj1, obj2):
    offsetX = obj2.x - obj1.x
    offsetY = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offsetX, offsetY)) != None


def main():
    run = True
    fps = 60

    # oyuncunun seviyesi ve kalan can bilgisi değişkenleri
    level = 0
    lives = 3

    # kayıp sayacı ve bilgisi
    lost = False
    lostCount = 0

    # hareket değişkenleri
    waveLength = 5
    enemyMovement = 1
    playerMovement = 5
    laserMovement = 5

    # label için font tanımla
    lblFont = pygame.font.SysFont("comicsans", 40)
    lostFont = pygame.font.SysFont("comicsans", 55)

    # düşmanların tanımlanması
    enemies = []

    # oyuncunun pencerede yerleşmesi
    player = Player(300, 640)

    clock = pygame.time.Clock()

    # arkaplanın renklendirilmesi ve label, oyuncu ve düşmanların pencerede yerleşmesi
    def bgPoints():
        gameWindow.blit(bg, (0, 0))
        lblLives = lblFont.render(f"Lives: {lives}", 1, (255, 255, 255))
        gameWindow.blit(lblLives, (10, 10))
        lblLevel = lblFont.render(f"Level: {level}", 1, (255, 255, 255))
        gameWindow.blit(lblLevel, (width - lblLevel.get_width() - 10, 10))
        for enemy in enemies:
            enemy.draw(gameWindow)

        player.draw(gameWindow)
        if lost:
            lblLost = lostFont.render("Game Over!", 1, (255, 255, 255))
            gameWindow.blit(lblLost, (width / 2 - lblLost.get_width() / 2, 350))

        pygame.display.update()

    while run:
        clock.tick(fps)

        bgPoints()

        if lives <= 0 or player.health <= 0:
            lost = True
            lostCount += 1

        if lost:
            if lostCount > fps * 3:
                run = False
            else:
                continue

        #düşman gemileri
        if len(enemies) == 0:
            level += 1
            waveLength += 5
            for i in range(waveLength):
                enemy = EnemyShip(random.randrange(50, width - 100), random.randrange(-1500, -100),
                                  random.choice(["redEnemy", "greenEnemy", "blueEnemy"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        # klavye ve mouse atamaları
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - playerMovement > 0:
            player.x -= playerMovement
        if keys[pygame.K_RIGHT] and player.x + playerMovement + player.getWidth() < width:
            player.x += playerMovement
        if keys[pygame.K_UP] and player.y - playerMovement > 0:
            player.y -= playerMovement
        if keys[pygame.K_DOWN] and player.y + playerMovement + player.getHeight() + 15 < height:
            player.y += playerMovement
        if keys[pygame.K_SPACE]:
            player.shoot()

        # lazer atışları sonrası canların azalması ve düşman gemilerinin yok edilmesi
        for enemy in enemies:
            enemy.move(enemyMovement)
            enemy.moveLasers(laserMovement, player)

            if random.randrange(0, 2 * 60) == 1:
                enemy.shoot()

            if shipCollide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)

            elif enemy.y + enemy.getHeight() > height:
                lives -= 1
                enemies.remove(enemy)

        player.moveLasers(-laserMovement, enemies)

# oyunun açılışı
def mainMenu():
    titleFont = pygame.font.SysFont("comicsans", 55)
    run = True
    while run:
        gameWindow.blit(bg, (0, 0))
        lblTitle = titleFont.render("Press the mouse to begin...", 1, (255, 255, 255))
        gameWindow.blit(lblTitle, (width / 2 - lblTitle.get_width() / 2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            main()
    pygame.quit()


mainMenu()
