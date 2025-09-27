# game.py
import random
from math import floor
from pygame import Rect

WIDTH, HEIGHT = 800, 600
TITLE = "Mini Roguelike"
TILE = 32

STATE_MENU, STATE_GAME = "menu", "game"
game_state = STATE_MENU
music_on, sfx_on = True, True

# ---------------- MAP ----------------
RAW_MAP = [
    "############################",
    "#............#............#",
    "#............#............#",
    "#....#####...#...#####....#",
    "#..........................#",
    "############################",
]
ROWS, COLS = len(RAW_MAP), len(RAW_MAP[0])
WIDTH, HEIGHT = COLS*TILE, ROWS*TILE

def is_wall(c):
    x, y = c
    return RAW_MAP[y][x] == "#"

def to_px(cx, cy): return cx*TILE+TILE//2, cy*TILE+TILE//2

# ---------------- ANIMATION ----------------
class AnimatedSprite:
    def __init__(self, name, pos, frames):
        self.name, self.x, self.y = name, *pos
        self.state, self.dir, self.frame = "idle", "right", 0
        self.frames = frames  # dict[(state,dir)] = qtd
        self.t = 0

    def update(self, dt):
        self.t += dt
        f = self.frames[(self.state,self.dir)]
        if f>0 and self.t>=0.1:
            self.t=0; self.frame=(self.frame+1)%f

    def draw(self):
        img=f"{self.name}_{self.state}_{self.dir}_{self.frame}"
        try: screen.blit(img,(self.x-16,self.y-16))
        except: screen.draw.filled_circle((self.x,self.y),14,"blue")

    @property
    def rect(self): return Rect(self.x-16,self.y-16,32,32)

# ---------------- HERO ----------------
class Hero:
    def __init__(self):
        self.cx,self.cy=2,2
        self.x,self.y=to_px(self.cx,self.cy)
        self.sprite=AnimatedSprite("hero",(self.x,self.y),
          {("idle","right"):4,("idle","left"):4,("walk","right"):6,("walk","left"):6})
        self.moving,self.src,self.dst,self.t=False,(0,0),(0,0),0

    def want_move(self,dx,dy):
        if self.moving: return
        nx,ny=self.cx+dx,self.cy+dy
        if is_wall((nx,ny)): return
        self.cx,self.cy=nx,ny
        self.src,self.dst=(self.x,self.y),to_px(nx,ny)
        self.moving,self.t=True,0
        self.sprite.state="walk"
        self.sprite.dir="left" if dx<0 else "right"
        if sfx_on: sounds.step.play()

    def update(self,dt):
        if self.moving:
            self.t+=dt/0.2
            if self.t>=1: self.t,self.moving=1,False; self.sprite.state="idle"
            self.x=self.src[0]*(1-self.t)+self.dst[0]*self.t
            self.y=self.src[1]*(1-self.t)+self.dst[1]*self.t
        self.sprite.x,self.sprite.y=self.x,self.y
        self.sprite.update(dt)

    def draw(self): self.sprite.draw()
    def reset(self): self.__init__()

# ---------------- ENEMY ----------------
class Enemy:
    def __init__(self,cx,cy,rect):
        self.cx,self.cy=cx,cy
        self.x,self.y=to_px(cx,cy)
        self.territory=rect
        self.sprite=AnimatedSprite("slime",(self.x,self.y),
          {("idle","right"):4,("idle","left"):4,("walk","right"):6,("walk","left"):6})
        self.moving,self.src,self.dst,self.t=False,(0,0),(0,0),0
        self.cool=0

    def step(self):
        for _ in range(5):
            dx,dy=random.choice([(1,0),(-1,0),(0,1),(0,-1)])
            nx,ny=self.cx+dx,self.cy+dy
            if is_wall((nx,ny)) or not self.territory.collidepoint(nx,ny): continue
            self.cx,self.cy=nx,ny
            self.src,self.dst=(self.x,self.y),to_px(nx,ny)
            self.moving,self.t=True,0
            self.sprite.state="walk"
            self.sprite.dir="left" if dx<0 else "right"; return
        self.sprite.state="idle"

    def update(self,dt):
        self.cool-=dt
        if self.moving:
            self.t+=dt/0.25
            if self.t>=1: self.t,self.moving=1,False; self.cool=0.5; self.sprite.state="idle"
            self.x=self.src[0]*(1-self.t)+self.dst[0]*self.t
            self.y=self.src[1]*(1-self.t)+self.dst[1]*self.t
        elif self.cool<=0: self.step()
        self.sprite.x,self.sprite.y=self.x,self.y; self.sprite.update(dt)

    def draw(self): self.sprite.draw()

# ---------------- MENU ----------------
class Button:
    def __init__(self,text,y): self.text,self.r=text,Rect(WIDTH//2-100,y,200,50)
    def draw(self): screen.draw.filled_rect(self.r,"white"); screen.draw.text(self.text,center=self.r.center,color="black")
    def hit(self,pos): return self.r.collidepoint(pos)

btns=[Button("Start",200),Button("Music ON",270),Button("Quit",340)]

# ---------------- GLOBALS ----------------
hero=Hero()
enemies=[Enemy(10,2,Rect(8,1,10,4)),Enemy(20,3,Rect(18,1,6,5))]

# ---------------- PZG HOOKS ----------------
def draw():
    screen.clear()
    if game_state==STATE_MENU:
        for b in btns: b.draw()
    else:
        for y,row in enumerate(RAW_MAP):
            for x,c in enumerate(row):
                col=(60,60,80) if c=="#" else (200,200,220)
                screen.draw.filled_rect(Rect(x*TILE,y*TILE,TILE,TILE),col)
        for e in enemies: e.draw()
        hero.draw()

def update(dt):
    if game_state==STATE_GAME:
        hero.update(dt)
        for e in enemies:
            e.update(dt)
            if hero.sprite.rect.colliderect(e.sprite.rect):
                if sfx_on: sounds.hit.play()
                hero.reset()

def on_key_down(k):
    global game_state,music_on
    if game_state==STATE_GAME:
        if k==keys.ESCAPE: set_menu()
        elif k in (keys.M,): toggle_music()
        elif k in (keys.LEFT,keys.A): hero.want_move(-1,0)
        elif k in (keys.RIGHT,keys.D): hero.want_move(1,0)
        elif k in (keys.UP,keys.W): hero.want_move(0,-1)
        elif k in (keys.DOWN,keys.S): hero.want_move(0,1)

def on_mouse_down(pos):
    global game_state,music_on,sfx_on
    if game_state==STATE_MENU:
        if btns[0].hit(pos): set_game()
        elif btns[1].hit(pos): music_on,sfx_on=not music_on,not sfx_on; btns[1].text=f"Music {'ON' if music_on else 'OFF'}"; toggle_music()
        elif btns[2].hit(pos): exit()

def set_game(): 
    global game_state; game_state=STATE_GAME; toggle_music()
def set_menu(): 
    global game_state; game_state=STATE_MENU
def toggle_music():
    if music_on: music.play("bgm"); music.set_volume(0.5)
    else: music.stop()
