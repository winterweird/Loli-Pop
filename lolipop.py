"""
DESCRIPTION
 ***********************           LOLI POP           ***********************
 *                                                                          *
 *  PROJECT IDEAS:                                                          *
 *                                                                          *
 *    - Speed varies semi-randomly, increasing as the game drags on         *
 *                                                                          *
 *    - GAME MODES:                                                         *
 *        *  Normal mode:                                                   *
 *               Every time a loli hits the upper boundry of the screen,    *
 *               you lose a life. When you run out of lives, you lose the   *
 *               game.                                                      *
 *        *  Sudden Death mode:                                             *
 *               Just like Normal mode except you only have one life.       *
 *        *  Punishment mode:                                               *
 *               The upper boundry draws closer to the ground for each      *
 *               time a loli hits it. When it reaches the bottom, you       *
 *               lose.                                                      *
 *        *  Impossible mode:                                               *
 *               Just like Normal mode except popping is disabled           *
 *                                                                          *
 *    - Hit list:                                                           *
 *          Missing a target means losing something (possibly a life, or    *
 *          parts of a life).                                               *
 *                                                                          *
 *    - Falling objects may                                                 *
 *        *  Replenish life                                                 *
 *        *  Give boosts (x2 points, slow-mo, etc.)                         *
 *        *  Do absolutely nothing (this game will be so confusing!)        *
 *                                                                          *
 *    - Yandere lolis                                                       *
 *          Possibly induced by reaching a certain difficulty, yandere      *
 *          lolis will begin to pop up. DO NOT CLICK THESE LITTLE BASTARDS! *
 *          However tempting, clicking on a yandere loli is serious         *
 *          business, and might get you killed or worse. Clicking a yandere *
 *          loli is grounds for instant loss.                               *
 *                                                                          *
 ****************************************************************************
"""

import pygame, sys, os, webbrowser, math, random
from pygame.locals import *

GAME_NAME = "Loli Pop" # change anytime

# rooms
# I'll keep these for now, might be useful
# only using four of 'em at the time of writing (2015-02-06)

MAINMENU = 0
PLAYGAME = 1
CREDITS = 2
STORY = 3
GAMEOVER = 4
SETTINGS = 5

# colors
# BECAUSE I FUCKING USE THEM ALL THE TIME
# .... at least while testing stuff

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
HORRIBLEMAGENTA = (255, 0, 255)
STATUSBARGRAY = (181, 181, 181)
BGRGRAY = (230, 230, 230) # Wow, this came in handy....
#                         # ... and THAT is why a simple bgr color is perfectly fine!


# this makes code not go boom
try:
    PATH = os.path.join(os.path.dirname(__file__), 'data')
except:
    PATH = os.path.join(os.getcwd(), 'data')

class GameConstants(object):
    def __init__(self):
        # self.regen = 0 # I might make this a special mode later, but as of now.... no. Just... no.
        self.spawnDelay = 150
        self.baseVSpeed = 2
        self.level = 1 # not sure if I need this, but might be...?
        self.randomVSpeedLevel = 1
    
    def adjust(self):
        #self.regen = round(self.regen + 0.1, 1)
        self.baseVSpeed = round(self.baseVSpeed+0.5, 1)
        self.level += 1
        self.spawnDelay -= round(60/self.level)
        if self.spawnDelay < 20: self.spawnDelay = 20



class Graphics(object):
    def __init__(self):
        imgs = [pygame.image.load(os.path.join(PATH, 'images', 'intro', 'brought%s.png' % n)) for n in range(1, 17)]
        self.intro = [image for index, image in enumerate(imgs) for i in range((1 if index not in (3,4) else 60))]
        
        self.mainmenubgr = pygame.image.load(os.path.join(PATH, "images", "bgrs", "sleepy_loli_resized.png"))
        self.mainmenubgr = (self.mainmenubgr, self.mainmenubgr.get_rect(x=10))
        
        self.lelittlestar = pygame.image.load(os.path.join(PATH, "images", "menu", "smallstarthing.png"))
        lolipath = os.path.join(PATH, "images", "lolis", "resized")
        self.lolis = [pygame.image.load(os.path.join(lolipath, x)) for x in os.listdir(lolipath)]
        
        self.statusbar = pygame.image.load(os.path.join(PATH, 'images', 'misc', 'statusbar.png'))
        self.heart = pygame.image.load(os.path.join(PATH, 'images', 'misc', 'heart.png'))
        self.over9000 = Game.text(Game, "IT'S OVER 9000!", 80, pos=(0, -100), font='edo.ttf')
        self.volume = [pygame.image.load(os.path.join(PATH, "images", "misc", "volume_"+x+".png")) for x in ("off", "on")]
        
        self.storyloli = pygame.image.load(os.path.join(PATH, "images", "menu", "story_loli.png"))
        self.credits = pygame.image.load(os.path.join(PATH, "images", "misc", "credits.png"))
    
    def drawLives(self, nOfLives):
        """Draw the lives on the statusbar"""
        initialPos = (100, 10)
        if nOfLives < 0: nOfLives = 0 # can't make surface with negative size
        self.statusbar = pygame.image.load(os.path.join(PATH, 'images', 'misc', 'statusbar.png'))
        if nOfLives > 3:
            if int(nOfLives) == nOfLives: # doesn't truncate => whole number
                self.statusbar.blit(self.heart, initialPos)
            else:
                surf = pygame.Surface((round(31*(nOfLives-int(nOfLives))), 30))
                surf.fill(STATUSBARGRAY)
                surf.blit(self.heart, (0,0))
                self.statusbar.blit(surf, initialPos)
        else:
            x, y = initialPos
            while nOfLives >= 1:
                self.statusbar.blit(self.heart, (x,y))
                nOfLives -= 1
                x += 35
            if nOfLives:
                surf = pygame.Surface((round(31*nOfLives), 30))
                surf.fill((181,181,181))
                surf.blit(self.heart, (0,0))
                self.statusbar.blit(surf, (x,y))



class Sound(object):
    def __init__(self):
        # Here be sound files
        try:
            self.blop = pygame.mixer.Sound(os.path.join(PATH, 'sound', 'sfx', 'blop.ogg'))
        except:
            print("Couldn't load blop.ogg")
        try:
            self.balloon = pygame.mixer.Sound(os.path.join(PATH, "sound", "sfx", "balloon.ogg"))
        except:
            print("Couldn't load balloon.ogg")
        try:
            self.click = pygame.mixer.Sound(os.path.join(PATH, "sound", "sfx", "click.ogg"))
        except:
            print("Couldn't load click.ogg")



class Loli(object):
    def __init__(self, loli):
        
        self.origimage = loli
        self.image = pygame.Surface(self.origimage.get_size())
        self.image.fill(BGRGRAY)
        self.image.set_colorkey(BGRGRAY)
        self.image.blit(self.origimage, (0,0))
        self.rect = self.image.get_rect()
        # I'll get back to placing the rect
        
        # base horizontal speed
        self.hspeed = 0.2
        self.maxhspeed = random.randint(5, 7)
        self.hvel = self.maxhspeed*random.choice((-1, 1)) # random start direction: left/right
        
        minDistanceFromEdge = 100
        self.rect.center = (random.randint(minDistanceFromEdge, 640-minDistanceFromEdge), 600)
        
        # Any decimal positions will be stored here
        self.xpos, self.ypos = self.rect.x, self.rect.y
        
        self.jamvektslinje = self.rect.centerx # I don't remember English name of this
        
        # when hvel == 0, I need to know whether to proceed left or right.
        # there are probably better ways, I might change this later.
        # unless my code grows to a horrific beast and all hope of revision
        # becomes a faint memory in the face of eternal darkness.......
        self.returningFromRight = True if self.hvel > 0 else False
        
        self.removeCounter = 10
        self.resizer = 1
        self.removeThyself = False
        self.doneRemoving = False
        self.alpha = 250
        bpth = os.path.join(PATH, "images", "misc", "blood_d")
        self.bloodanimation = [pygame.image.load(os.path.join(bpth, x)) for x in os.listdir(bpth)]
        self.bloodindex = 0
    
    def draw(self, surf):
        surf.blit(self.image, self.rect)
    
    def goUp(self, base, randomnessBoundry):
        # set ypos to a random 
        self.ypos -= base+random.random()*randomnessBoundry*0.5 # half random is enough D:
        self.rect.y = round(self.ypos)
    
    def drift(self):
        self.xpos += self.hvel
        self.rect.x = round(self.xpos)
    
    def goLR(self):
        if self.rect.centerx > self.jamvektslinje: self.hvel = round(self.hvel - self.hspeed, 1)
        elif self.rect.centerx < self.jamvektslinje: self.hvel = round(self.hvel + self.hspeed, 1)
        elif self.returningFromRight:
            self.hvel = round(self.hvel - self.hspeed, 1)
            self.returningFromRight = False
        else:
            self.hvel = round(self.hvel + self.hspeed, 1)
            self.returningFromRight = True
        
        # shouldn't go faster than maximum velocity allowed
        if self.hvel > self.maxhspeed: self.hvel = self.maxhspeed
        elif self.hvel < -self.maxhspeed: self.hvel = -self.maxhspeed
    
    def remove(self, surface):
        self.draw(surface)
        if self.removeThyself:
            self.hspeed = 0
            self.hvel = 0
            self.resizer = round(self.resizer+0.05, 2)
            c = self.rect.center
            self.image = pygame.transform.scale(self.origimage, (round(self.origimage.get_width()*self.resizer), round(self.origimage.get_height()*self.resizer)))
            self.rect = self.image.get_rect(center=c)
            self.removeCounter -= 1
            if not self.removeCounter:
                self.doneRemoving = True
    
    def explode(self, surface):
        self.draw(surface)
        if self.removeThyself:
            self.hspeed = 0
            self.hvel = 0
            self.alpha -= 25
            self.image.set_alpha(self.alpha)
            c, b = self.rect.center, self.bloodanimation[self.bloodindex]
            surface.blit(b, b.get_rect(center=c))
            self.removeCounter -= 1
            if self.removeCounter%2: self.bloodindex += 1
            if not self.removeCounter:
                self.doneRemoving = True



class BloodStain(object):
    def __init__(self, pos):
        self.origimage = pygame.image.load(os.path.join(PATH, "images", "misc", "blood_stain.png")).convert_alpha()
        self.image = pygame.Surface(self.origimage.get_size())
        self.image.fill(BGRGRAY)
        self.image.set_colorkey(BGRGRAY)
        self.image.blit(self.origimage, (0,0))
        self.image.convert()
        self.rect = self.image.get_rect(center = pos)
        self.alpha = 500
    
    def update(self, surface):
        self.alpha -= 1
        self.image.set_alpha(self.alpha)
        surface.blit(self.image, self.rect)



class FallingBGR(object):
    def __init__(self):
        self.image = pygame.Surface((640,480))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.topleft = (0, -480)
        self.acc = 0
        self.gravity = 0.01
        self.velocity = 0
        self.actualY = self.rect.y
    
    def fall(self):
        if self.rect.y == 0:
            self.acc = 0
            self.velocity = 0
        else:
            self.acc += self.gravity
            self.velocity += self.acc
            self.actualY += self.velocity
            self.rect.y = round(self.actualY)
            if self.rect.y > 0:
                self.rect.y = 0
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)
    
    def reset(self):
        self.rect.topleft = (0, -480)
        self.acc = 0
        self.velocity = 0
        self.actualY = self.rect.y



class ConfirmDialog(object):
    def __init__(self):
        self.image = pygame.Surface((200, 100))
        self.image.fill(WHITE)
        pygame.draw.rect(self.image, BLACK, (0, 0, 200, 100), 5)
        self.areusure = Game.text(Game, "Are you sure?", 20, pos=(self.image.get_width()//2,30), font="DejaVuSans-Bold.ttf")
        
        self.yes = Game.text(Game, "YES", 15, pos=(50, 80), font="DejaVuSans-Bold.ttf")
        self.no = Game.text(Game, "NO", 15, pos=(150, 80), font="DejaVuSans-Bold.ttf")
        self.yesCenterRelative = (-50, 30)
        self.noCenterRelative = (50, 30)
        for item in [self.areusure, self.yes, self.no]:
            self.image.blit(item[0], item[1])
    
    def confirm(self, screen):
        while True:
            screen.blit(self.image, self.image.get_rect(center=(screen.get_width()//2, screen.get_height()//2)))
            yesRect = self.yes[0].get_rect(center=(screen.get_width()//2+self.yesCenterRelative[0], screen.get_height()//2+self.yesCenterRelative[1]))
            noRect = self.no[0].get_rect(center=(screen.get_width()//2+self.noCenterRelative[0], screen.get_height()//2+self.noCenterRelative[1]))
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if yesRect.collidepoint(event.pos):
                            return True
                        if noRect.collidepoint(event.pos):
                            return False
                elif event.type == KEYDOWN:
                    if event.key == K_RETURN:
                        return True
                    if event.key == K_ESCAPE:
                        return False
                    if event.key == K_BACKSPACE:
                        return False
            pygame.display.update()



class Game(object):
    center = (320, 240)
    def __init__(self):
        pygame.mixer.pre_init(48000)
        pygame.init()
        
        self.width = 640
        self.height = 480
        self.center = (self.width//2, self.height//2)
        self.windowsize = (self.width, self.height)
        self.screen = pygame.display.set_mode(self.windowsize)
        self.windowrect = self.screen.get_rect()
        self.windowrect.topleft = (0, 0)
        
        pygame.display.set_caption(GAME_NAME)
        pygame.display.set_icon(pygame.image.load(os.path.join(PATH, "images", "misc", "icon.png")))
        
        self.graphics = Graphics()
        self.sound = Sound()
        self.constants = GameConstants()
        self.gameOverBGR = FallingBGR()
        self.confirmDialog = ConfirmDialog()
        
        self.clock = pygame.time.Clock()
        
        self.storyUnlocked = False
        self.storyRead = False
        self.scaryMode = False
        self.gameSetuped = False
        
        with open(os.path.join(PATH, "game_data", "confirm_quit.set"), 'r') as cq:
            try: self.confirmQuit = int(cq.readline())
            except: self.confirmQuit = 1
        
        self.first = True
        self.volume = 1
        self.storyNarrativeCounter = 0
        
        self.alpha = 255 # use in story but maybe also other places
        
        pygame.mixer.music.load(os.path.join(PATH, "sound", "music", "silent.ogg"))
        
        self.room = MAINMENU
    
    def getEvents(self):
        self.events = pygame.event.get()
    
    def checkQuit(self):
        "This will happen alot, so I'll make it a method"
        for event in self.events:
            if event.type == QUIT:
                if not self.confirmQuit or self.confirmDialog.confirm(self.screen):
                    pygame.quit()
                    sys.exit()
    
    def update(self, fps=60, rects=None):
        if rects == None: pygame.display.update()
        else: pygame.display.update(rects)
        self.clock.tick(fps)
    
    def setupGame(self):
        self.loliList = []
        self.loliSpawned = 10
        self.score = 0
        self.lives = 3
        self.gameOverBGR.reset()
        self.gameoverAlpha = 400
        self.returnCountdown = 100
        self.newHigh = False
        self.constants.__init__()
        self.bloodstains = [] # contains BloodStain() instances
        self.gameSetuped = True
    
    def text(self, msg, size, **kwargs):
        """msg: content of text
        size: size of text
        pos: where text should be located (x,y)
        anchor: which part pos will apply to
        font: which font used
        color: which color of text"""
        
        try: pos = kwargs["pos"]
        except: pos = self.center
        try: anchor = kwargs["anchor"]
        except: anchor = "C"
        try: color = kwargs["color"]
        except: color = BLACK
        try: font = os.path.join(PATH, "fonts", kwargs["font"])
        except: font = os.path.join(PATH, "fonts", "ouat.ttf")
        
        surface = pygame.font.Font(font, size).render(msg, True, color)
        rect = surface.get_rect(center = pos)
        
        # I was like, half a step away from spelling NSFW!
        if "N" in anchor: rect.top = pos[1]
        if "S" in anchor: rect.bottom = pos[1]
        if "E" in anchor: rect.right = pos[0]
        if "W" in anchor: rect.left = pos[0]
        return surface, rect
    
    def flash(self, text, size, **kwargs):
        # I gave up on fade out, it's not worth it
        
        # set up variables
        pos = kwargs["pos"] if "pos" in kwargs else self.center
        anchor = kwargs["anchor"] if "anchor" in kwargs else "C"
        color = kwargs["color"] if "color" in kwargs else BLACK
        font = kwargs["font"] if "font" in kwargs else os.path.join(PATH, 'fonts', 'ouat.ttf')
        bgrColor = kwargs["bgrColor"] if "bgrColor" in kwargs else WHITE
        cim = kwargs["cim"] if "cim" in kwargs else False
        
        
        alpha = 0
        x = 0
        
        msg = self.text(text, size, pos=pos, anchor=anchor, color=color, font=font)
        
        bgr = pygame.Surface(msg[0].get_size())
        bgr.fill(bgrColor)
        bgr.set_colorkey(bgrColor)
        bgr.blit(msg[0], (0,0))
        bgr.convert()
        
        # OBSERVE MY SHITTY FLASHING OF TEXT
        while True:
            self.getEvents()
            self.checkQuit()
            
            alpha += 1
            
            bgr.set_alpha(alpha)
            self.screen.blit(bgr, msg[1])            
            
            self.update()
            
            while alpha == 30: # since layers pile up, it's opaque now
                self.getEvents()
                self.checkQuit()
                
                x += 1
                
                self.update()
                
                while x == 110:
                    if cim: return
                    self.getEvents()
                    self.checkQuit()
                    
                    alpha -= 5
                    
                    bgr.set_alpha(alpha)
                    self.screen.blit(bgr, msg[1])
                    
                    self.update()
                    
                    if alpha == 0:
                        return
    
    def flashSeries(self, size, *lines, **kwargs):
        pos = kwargs["pos"] if "pos" in kwargs else self.center
        anchor = kwargs["anchor"] if "anchor" in kwargs else "C"
        color = kwargs["color"] if "color" in kwargs else BLACK
        font = kwargs["font"] if "font" in kwargs else os.path.join(PATH, 'fonts', 'ouat.ttf')
        bgrColor = kwargs["bgrColor"] if "bgrColor" in kwargs else WHITE
        
        cx, cy = pos
        for l in lines:
            self.flash(l, size, pos=(cx, cy), anchor=anchor, color=color, font=font, bgrColor=bgrColor, cim=True)
            if l: cy += size
        self.update(1)
    
    def playIntro(self):
        "The intro will go here and should be self-sufficient."
        
        # FOLDER STRUCTURE IMPORTANT
        try:
            appear = pygame.mixer.Sound(os.path.join(PATH, 'sound', 'sfx', 'intro_appear.wav'))
        except:
            appear = None
            print("Couldn't load appear")
        
        try:
            iblast = pygame.mixer.Sound(os.path.join(PATH, 'sound', 'sfx', 'intro_shatter.wav'))
        except:
            iblast = None
            print("Couldn't load iblast")
        
        for index, i in enumerate([pygame.Surface((1, 1)) for i in range(10)] + self.graphics.intro + [pygame.Surface((1,1)) for i in range(100)]):
            self.getEvents()
            self.checkQuit()
            
            for event in self.events:
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    # stop playing sounds and exit function
                    appear.stop()
                    iblast.stop()
                    return
            
            #image scaled down 3 times
            i = pygame.transform.scale(i, (i.get_width()//3, i.get_height()//3))
            
            # center
            c = (self.width//2, self.height//2)
            r = i.get_rect(center=c)
            
            if index == 0 and appear:      # start playing appear at start
                appear.play()
            elif index == 130 and iblast:  # start playing iblast at 130th frame
                iblast.play()
            
            # clear, blit and update
            self.screen.fill(0)
            self.screen.blit(i, r)
            self.update(30)
    
    def mainMenu(self):
        if not pygame.mixer.music.get_busy():
            if self.first:
                self.first = False
                pygame.mixer.music.load(os.path.join(PATH, "sound", "music", "silent.ogg"))
                pygame.mixer.music.play(0, 1.5)
            else:
                pygame.mixer.music.load(os.path.join(PATH, "sound", "music", "lolita.ogg"))
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)
        
        if self.volume:
            pygame.mixer.music.set_volume(0.5)
        else:
            pygame.mixer.music.set_volume(0)
        
        # LOLI POP title
        lolipop = self.text("LOLI   POP", 50, pos=(480, 80))
        
        # PLAY GAME button
        playgame = self.text("PLAY", 25, pos=(430, 200), anchor="W")
        
        # SETTINGS button
        settings = self.text("SETTINGS", 25, pos=(430, 235), anchor="W")
        
        # STORY button
        story = self.text("STORY", 25, pos=(430, 270), anchor="W", color=(STATUSBARGRAY if not self.storyUnlocked else BLACK))
        
        # CREDITS button
        cred = self.text("CREDITS", 25, pos=(430, 305), anchor="W")
        
        # QUIT button
        stop = self.text("QUIT", 25, pos=(430, 340), anchor="W")
        
        # HIGH SCORE note
        with open(os.path.join(PATH, "game_data", "high.score"), "r") as hsfile:
            highscore = hsfile.readline()
            if int(highscore) >= 1000:
                self.storyUnlocked = True
            highscore = self.text("High Score:  %s" %(highscore), 20, pos=(480, 130))
        
        # CREATED BY mini small text at the edge of the screen.
        createdby = self.text("Created by Vegard Itland Enterprise", 10, pos=(self.width-5, self.height-5), anchor="SE")
        
        menuButtons = [playgame, settings, story, cred, stop]
        otherBlitItems = [lolipop, highscore, createdby, self.graphics.mainmenubgr]
        
        for event in self.events:
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if playgame[1].collidepoint(event.pos): # player clicked the play game button
                        self.room = PLAYGAME
                    elif settings[1].collidepoint(event.pos): # player clicked the settings button
                        self.room = SETTINGS
                    elif story[1].collidepoint(event.pos):
                        if self.storyUnlocked:
                            self.room = STORY
                        else:
                            s = pygame.Surface((story[0].get_width()+70, story[0].get_height()))
                            s.fill(WHITE)
                            self.screen.blit(s, s.get_rect(center=story[1].center))
                            self.flash("Score 1000 points in Loli Pop to unlock Story", 12, pos=(480, 270), font="DejaVuSans-Bold.ttf")
                    elif cred[1].collidepoint(event.pos):
                        self.room = CREDITS
                    elif stop[1].collidepoint(event.pos):
                        pygame.event.post(pygame.event.Event(QUIT))
            elif event.type == KEYDOWN:
                if event.key == ord("p"):
                    self.room = PLAYGAME
        
        self.screen.fill((255, 255, 255))
        for item in menuButtons:
            self.screen.blit(item[0], item[1])
            self.screen.blit(self.graphics.lelittlestar, self.graphics.lelittlestar.get_rect(center = (item[1].left-20, item[1].centery)))
        for item in otherBlitItems:
            self.screen.blit(item[0], item[1])
        self.update()
        if self.room == PLAYGAME: self.transitionscreen()
        elif self.room == STORY: self.transitionscreen()
    
    def playGame(self):
        
        if not self.gameSetuped: self.setupGame()
        if not pygame.mixer.music.get_busy():
            if self.first:
                self.first = False
                pygame.mixer.music.load(os.path.join(PATH, "sound", "music", "silent.ogg"))
                pygame.mixer.music.play(0, 1.5)
            else:
                pygame.mixer.music.load(os.path.join(PATH, "sound", "music", ("creepy_music" if self.scaryMode else "thai_music")+".ogg"))
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)
        
        if self.volume:
            pygame.mixer.music.set_volume(0.5)
        else:
            pygame.mixer.music.set_volume(0)
        
        for event in self.events:
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE: # return to main with ESC
                    self.gameSetuped = False
                    self.room = MAINMENU
                    self.transitionscreen()
                    return
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    for l in self.loliList:
                        if l.rect.collidepoint(event.pos):
                            if not self.scaryMode:
                                self.sound.blop.play()
                            else:
                                self.sound.balloon.play()
                                self.bloodstains.append(BloodStain(l.rect.center))
                            l.removeThyself = True
                            self.score += 5*self.constants.level
                            if not self.score % 100: self.constants.adjust()
                            if self.score > 9000:
                                self.graphics.over9000 = self.graphics.over9000[0], self.graphics.over9000[0].get_rect(center=self.center)
                            break
                    else:
                        if not self.graphics.statusbar.get_rect().collidepoint(event.pos):
                            self.sound.click.play()
                            self.lives = round(self.lives - 0.1, 1)
                        else:
                            if pygame.Rect(576, 1, 48, 48).collidepoint(event.pos):
                                self.volume = 0 if self.volume else 1
        
        if self.lives <= 0:
            with open(os.path.join(PATH, "game_data", "high.score"), "r") as hsfile:
                if self.score > int(hsfile.readline()):
                    self.newHigh = True
            if self.newHigh:
                with open(os.path.join(PATH, "game_data", "high.score"), "w") as hsfile:
                    hsfile.write(str(self.score))
            self.room = GAMEOVER
            pygame.mixer.music.fadeout(1000)
            self.first = True
        
        score = self.text(str(self.score), 22, pos=(340, 25), anchor='W', font="DejaVuSans-Bold.ttf")
        lifecount = self.text('x'+str(math.ceil(self.lives)) if self.lives>3 else '', 22, pos=(140, 25), anchor="W", font='DejaVuSans-Bold.ttf')
        level = self.text(str(self.constants.level), 22, pos=(500,25), anchor="W", font="DejaVuSans-Bold.ttf")
        
        self.graphics.drawLives(self.lives)
        
        self.screen.fill(BGRGRAY)
        
        # HANDLE BLOODSTAIN BLITTING
        toremove = []
        for i, s in enumerate(self.bloodstains):
            s.update(self.screen)
            if s.alpha == 0:
                toremove.append(i)
        for i, x in enumerate(toremove):
            self.bloodstains.pop(x-i) # i = popped elements - since list gets shorter
        # END OF HANDLE BLOODSTAIN BLITTING
        
        if not self.loliSpawned:
            self.loliList.append(Loli(self.graphics.lolis[random.randint(0,len(self.graphics.lolis)-1)]))
            self.loliSpawned = self.constants.spawnDelay
        else:
            self.loliSpawned -= 1
        for l in self.loliList:
            if l.rect.bottom < 50:
                self.loliList.remove(l)
                self.lives = round(self.lives - 0.5, 1)
            elif l.doneRemoving:
                self.loliList.remove(l)
            else:
                l.goUp(self.constants.baseVSpeed, self.constants.randomVSpeedLevel)
                l.drift() # the initial speed must first be applied, or else weird stuff happens
                l.goLR()
                if not self.scaryMode: l.remove(self.screen) # remove and explode incorporate draw
                else: l.explode(self.screen)                 # see line above
        
        self.screen.blit(self.graphics.statusbar, (0,0))
        self.screen.blit(score[0], score[1])
        self.screen.blit(level[0], level[1])
        self.screen.blit(self.graphics.volume[self.volume], self.graphics.volume[0].get_rect(center=(600, 25)))
        self.screen.blit(self.graphics.over9000[0], self.graphics.over9000[1])
        self.screen.blit(lifecount[0], lifecount[1])
        
        self.update(self.room==GAMEOVER and 1 or 60)
    
    def gameOver(self):
        if not pygame.mixer.music.get_busy():
            if self.first:
                self.first = False
                pygame.mixer.music.load(os.path.join(PATH, "sound", "music", "silent.ogg"))
                pygame.mixer.music.play()
            else:
                pygame.mixer.music.load(os.path.join(PATH, "sound", "music", "game_over.ogg"))
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)
        
        if self.volume:
            pygame.mixer.music.set_volume(0.5)
        else:
            pygame.mixer.music.set_volume(0)
        
        self.gameOverBGR.fall()
        self.gameOverBGR.draw(self.screen)
        
        if self.gameoverAlpha > 0: self.gameoverAlpha -= 1
        
        gameovermsg = self.text("GAME OVER", 50, color=RED, font="edo.ttf")
        mask = pygame.Surface(gameovermsg[0].get_size())
        mask.fill(BLACK)
        mask.set_alpha(self.gameoverAlpha)
        maskrect = mask.get_rect(center=self.center)
        
        score = self.text("SCORE:  %s" %(self.score), 22, pos=(self.width//2, 300), anchor='N', color=WHITE, font='DejaVuSans-Bold.ttf')
        newhigh = self.text("(New high!)", 15, pos=(self.width//2, 326), anchor="N", color=WHITE, font="DejaVuSans-Bold.ttf")
        
        returnToMain = self.text("Click here (or press Escape) to return to the main menu", 15, pos=(self.width//2, 400), anchor="N", color=WHITE, font='DejaVuSans-Bold.ttf')
        
        if self.gameOverBGR.rect.y == 0:
            self.screen.blit(gameovermsg[0], gameovermsg[1])
            self.screen.blit(mask, maskrect)
        
        if self.gameoverAlpha == 0:
            self.screen.blit(score[0], score[1])
            if self.newHigh: self.screen.blit(newhigh[0], newhigh[1])
            self.returnCountdown -= 1
            if self.returnCountdown < 0:
                self.screen.blit(returnToMain[0], returnToMain[1])
                for event in self.events:
                    if event.type == KEYDOWN:
                        if event.key == K_ESCAPE: # return to main with ESC
                            self.gameSetuped = False
                            self.room = MAINMENU
                    elif event.type == MOUSEBUTTONDOWN:
                        if event.button == 1:
                            if returnToMain[1].collidepoint(event.pos):
                                self.gameSetuped = False
                                self.room = MAINMENU
        
        self.update()
        if self.room == MAINMENU:
            self.first = True
            self.transitionscreen()
    
    def settings(self):
        
        # SETTINGS title
        title = self.text("SETTINGS", 50, pos=(self.width//2, 100))
        
        # BUTTONS GO HERE
        # ||
        # \/ (improvised down arrow)
        
        # return to main button
        returnToMain = self.text("Return to main", 20, pos=(self.width//2, 400), anchor="N")
        
        # reset high score button
        resetHigh = self.text("Reset High Score", 25, pos=(100, 200), anchor="W")
        
        # toggle volume
        volume = self.text("Toggle music on/off", 25, pos=(100, 230), anchor="W")
        
        # the game turned scary ;-;
        scary = self.text("Toggle Scary Mode off/on", 25, pos=(100, 260), anchor="W")
        
        
        
        buttons = [resetHigh, volume]
        if self.storyRead:
            buttons.append(scary)
        otherthings = [title, returnToMain, (self.graphics.volume[self.volume], self.graphics.volume[0].get_rect(center=(400, 230)))]
        
        resetted = False
        scaremoved = False
        voltog = False
        for event in self.events:
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE: # return to main with ESC
                    self.room = MAINMENU
                    return
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if returnToMain[1].collidepoint(event.pos):
                        self.room = MAINMENU
                        return
                    elif resetHigh[1].collidepoint(event.pos):
                        if self.confirmDialog.confirm(self.screen):
                            with open(os.path.join(PATH, "game_data", "high.score"), "w") as hsfile:
                                hsfile.write("0")
                            resetted = True
                    elif self.storyRead and scary[1].collidepoint(event.pos):
                        self.scaryMode = not self.scaryMode
                        scaremoved = True
                    elif volume[1].collidepoint(event.pos) or otherthings[2][1].collidepoint(event.pos):
                        self.volume = 0 if self.volume else 1
                        voltog = True
        
        self.screen.fill(WHITE)
        bgrimage = pygame.image.load(os.path.join(PATH, "images", "bgrs", "settings_bgr.png"))
        self.screen.blit(bgrimage, bgrimage.get_rect(center=self.center))
        mask = pygame.Surface(bgrimage.get_size())
        mask.fill(WHITE)
        mask.set_alpha(180)
        self.screen.blit(mask, mask.get_rect(center=self.center))
        
        
        for item in buttons:
            self.screen.blit(item[0], item[1])
            c = item[1].x-20, item[1].centery
            self.screen.blit(self.graphics.lelittlestar, self.graphics.lelittlestar.get_rect(center=c))
        for item in otherthings:
            self.screen.blit(item[0], item[1])
        
        if resetted:
            self.flash("High Score was reset", 30, pos=(self.width//2, 150), font="DejaVuSans-Bold.ttf", bgrImg = os.path.join(PATH, "images", "bgrs", "settings_bgr.png"))
        if scaremoved:
            self.flash("Scary Mode toggled " +("off" if not self.scaryMode else "on"), 30, pos=(self.width//2, 150), font="DejaVuSans-Bold.ttf", bgrImg = os.path.join(PATH, "images", "bgrs", "settings_bgr.png"))
        if voltog:
            pygame.mixer.music.set_volume(0.5 if self.volume else 0)
            self.flash("Volume turned " + ("on" if self.volume else "off"), 30, pos=(self.width//2, 150), font="DejaVuSans-Bold.ttf")
        
        self.update()
    
    def story(self):
        self.storyNarrativeCounter += 1
        if not pygame.mixer.music.get_busy():
            if self.first:
                self.first = False
                pygame.mixer.music.load(os.path.join(PATH, "sound", "music", "silent.ogg"))
                pygame.mixer.music.play(0, 1.5)
            else:
                pygame.mixer.music.load(os.path.join(PATH, "sound", "music", "story_music.ogg"))
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)
        
        if self.volume:
            pygame.mixer.music.set_volume(0.5)
        else:
            pygame.mixer.music.set_volume(0)
        
        if self.storyNarrativeCounter <101:
            frame = pygame.image.load(os.path.join(PATH, "images", "menu", "frame1.png")).convert()
        elif self.storyNarrativeCounter < 801:
            frame = pygame.image.load(os.path.join(PATH, "images", "menu", "frame2.png")).convert()
            if self.storyNarrativeCounter == 101:
                self.alpha = 0
        else:
            frame = pygame.image.load(os.path.join(PATH, "images", "menu", "frame3.png")).convert()
            if self.storyNarrativeCounter == 801:
                self.alpha = 0
            if self.storyNarrativeCounter == 1001:
                self.alpha = 255
        
        frect = frame.get_rect(center = self.center)
        
        frame.set_alpha(self.alpha)
        if self.storyNarrativeCounter < 1001:
            self.alpha += 1
        else:
            self.alpha -= 1
        
        lolheight = self.graphics.storyloli.get_height()
        hght = lolheight + (256-self.storyNarrativeCounter)
        
        if hght < 0: hght = 0
        
        sl = pygame.Surface((self.graphics.storyloli.get_width(),hght))
        sl.fill(STATUSBARGRAY)
        sl.set_colorkey(STATUSBARGRAY)
        sl.blit(self.graphics.storyloli, (0,0))
        
        if self.storyNarrativeCounter == 100:
            self.flashSeries(15, "You, like many others, started", "watching anime \"for the plot\".", " ", "However, this soon began to",
                             "change as your heart was", "captured by the cute and", "charming ways of the lolitas.", " ",
                             "After watching countless", "episodes of anime, and", "being teased by their",
                             "adorableness, you'd", "had enough. You", "had to have them.", "",
                             pos=(self.width//2, 120), font="DejaVuSans-Bold.ttf")
        
        if self.storyNarrativeCounter == 255:
            self.flashSeries(15, "So, putting an evil plan in", "motion, you set out to", "capture the innocent children", "to satisfy your own perverted", "desires.", "",
                             color=WHITE, bgrColor=BLACK, pos=(self.width//2, 170), font="DejaVuSans-Bold.ttf")
        
        if self.storyNarrativeCounter == 257+lolheight:
            self.flashSeries(15, "You confined them in a dark", "dungeon, the depths of which", "assured you that they would", "never be able to escape...", '', "Alive.",
                             " ", "You presumed it to be secret.", "To be safe.", '',
                             color=WHITE, bgrColor=BLACK, pos=(self.width//2, 170), font="DejaVuSans-Bold.ttf")
        
        if self.storyNarrativeCounter == 300+lolheight:
            self.flashSeries(29, "You were wrong.", "", color=WHITE, bgrColor=BLACK, pos=self.center, font="DejaVuSans-Bold.ttf")
        
        if self.storyNarrativeCounter == 350+lolheight:
            self.flashSeries(15, "In your haste, you had","forgotten that a few Mahou","Shoujos resided among the","lolis you had captured. With","their powers, they put a",
                             "magic spell on their fellow","prisoners."," ","And soon, all the lolis began","to rise towards the exit...","",
                             color=WHITE, bgrColor=BLACK, pos=(self.width//2, 170), font="DejaVuSans-Bold.ttf")
        
        if self.storyNarrativeCounter == 400+lolheight:
            self.flashSeries(15, "As soon as you realized this,", "panic struck you. But just as", "swiftly as it had come, it", "suddenly vanished, as you",
                             "understood what you would", "have to do.", " ", "After all, you cannot allow", "your secret to be exposed to", "the outer world. The", "authorities will not take", "kindly to this.", " ",
                             "Surely they will understand.", "",
                             color=WHITE, bgrColor=BLACK, pos=(self.width//2, 135), font="DejaVuSans-Bold.ttf")
        
        if self.storyNarrativeCounter == 450+lolheight:
            self.flashSeries(30, "THIS IS", "FOR THE BEST", color=WHITE, bgrColor=BLACK, pos=(self.width//2, self.height//2-15), font="edo.ttf")
        
        if self.storyNarrativeCounter == 1000:
            self.flashSeries(100, "HURRY", "", "", color=WHITE, bgrColor=BLACK, pos=self.center, font="edo.ttf")
        if not self.storyRead:
            self.scaryMode = True # only turn on scary mode first time entering the room
        self.storyRead = True
        fuckthiscrap = self.text("Fuck this crap!", 20, pos=(self.center[0],430))
        
        for event in self.events:
            if event.type == MOUSEBUTTONDOWN:
                if fuckthiscrap[1].collidepoint(event.pos):
                    self.room = MAINMENU
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.room = MAINMENU
        
        if self.storyNarrativeCounter == 1: self.screen.fill(WHITE)
        elif self.storyNarrativeCounter>1000: self.screen.fill(BLACK)
        
        reblit = pygame.Surface((640, 480))
        reblit.fill(WHITE)
        self.screen.blit(reblit, (0, frect.bottom))
        self.screen.blit(reblit, (frect.right, 0))
        
        self.screen.blit(frame, frect)
        self.screen.blit(sl, sl.get_rect(x=400, y=250))
        
        self.screen.blit(fuckthiscrap[0], fuckthiscrap[1])
        
        
        if self.storyNarrativeCounter == 1255:
            self.room = MAINMENU
        if self.room == MAINMENU:
            self.storyNarrativeCounter = 0
            self.transitionscreen()
        
        self.update()
    
    def credits(self):
        rect = self.graphics.credits.get_rect()
        self.screen.fill(BLACK)
        self.screen.blit(self.graphics.credits, rect)
        self.update(1)
        while rect.bottom > self.height:
            self.getEvents()
            self.checkQuit()
            rect.y -= 1
            self.screen.fill(BLACK)
            self.screen.blit(self.graphics.credits, rect)
            self.update()
        self.update(1)
        self.room = MAINMENU
        self.transitionscreen()
    
    def transitionscreen(self):
        pygame.mixer.music.fadeout(1000)
        self.screen.fill(BLACK)
        self.update(1)
        self.first = True
    
    def main(self):
        """This is the main method of this game and incorporates
        methods such as mainMenu(), gameplay() (<-- will change),
        etc., which will again incorporate methods such as update()"""
        
        self.playIntro()
        
        while True:
            self.getEvents()
            self.checkQuit()
            if self.room == MAINMENU:
                self.mainMenu()
            elif self.room == PLAYGAME:
                self.playGame()
            elif self.room == GAMEOVER:
                self.gameOver()
            elif self.room == SETTINGS:
                self.settings()
            elif self.room == STORY:
                self.story()
            elif self.room == CREDITS:
                self.credits()
            else:
                print("Idefkwyda, but this shit is not a room.")
                self.room = MAINMENU


if __name__ == '__main__':
    game = Game()
    game.main()