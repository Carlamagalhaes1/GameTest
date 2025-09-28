# type: ignore
# -*- coding: utf-8 -*-

import random
from pygame import Rect

WIDTH, HEIGHT, TILE = 900, 600, 32
TITLE = "Mini Roguelike"

STATE_MENU, STATE_GAME, STATE_WIN = "menu", "game", "win"
game_state = STATE_MENU
music_on, sfx_on = True, True

RAW_MAP = [
    "############################",
    "#....#.......#......##.....#",
    "#............#.............#",
    "#....#####...#...#####.....#",
    "#..........................#",
    "############################",
]
ROWS, COLS = len(RAW_MAP), len(RAW_MAP[0])
MAP_WIDTH, MAP_HEIGHT = COLS*TILE, ROWS*TILE
OFFSET_X, OFFSET_Y = (WIDTH-MAP_WIDTH)//2, (HEIGHT-MAP_HEIGHT)//2
DOOR_CX, DOOR_CY = COLS-2, 4

def is_wall(c): x,y=c; return RAW_MAP[y][x] == "#"
def to_px(cx,cy): return OFFSET_X+cx*TILE+TILE//2, OFFSET_Y+cy*TILE+TILE//2
def play_sound(name):
    if not sfx_on: return
    try: getattr(sounds, name).play()
    except: pass

class AnimatedSprite:
    def __init__(self, name, pos, frames):
        self.name,self.x,self.y=name,*pos
        self.state,self.dir,self.frame,self.t="idle","right",0,0
        self.frames=frames
    def update(self, dt):
        self.t+=dt; f=self.frames[(self.state,self.dir)]
        if f>0 and self.t>=0.1: self.t=0; self.frame=(self.frame+1)%f
    def draw(self):
        img=f"{self.name}_{self.state}_{self.dir}_{self.frame}"
        try: screen.blit(img,(self.x-16,self.y-16))
        except: screen.draw.filled_circle((self.x,self.y),14,"blue")
    @property
    def rect(self): return Rect(self.x-16,self.y-16,32,32)

class Hero:
    def __init__(self):
        self.cx,self.cy=2,2
        self.x,self.y=to_px(self.cx,self.cy)
        self.sprite=AnimatedSprite("hero",(self.x,self.y),{
            ("idle","right"):2,("idle","left"):2,("walk","right"):2,("walk","left"):2,
            ("hurt","left"):2,("hurt","right"):2})
        self.moving,self.src,self.dst,self.t=False,(0,0),(0,0),0
    def want_move(self,dx,dy):
        if self.moving: return
        nx,ny=self.cx+dx,self.cy+dy
        if is_wall((nx,ny)): return
        self.cx,self.cy=nx,ny
        self.src,self.dst=(self.x,self.y),to_px(nx,ny)
        self.moving,self.t=True,0
        self.sprite.state="walk"; self.sprite.dir="left" if dx<0 else "right"; play_sound("step")
    def update(self,dt):
        if self.moving:
            self.t+=dt/0.2
            if self.t>=1: self.t,self.moving=1,False; self.sprite.state="idle"
            self.x=self.src[0]*(1-self.t)+self.dst[0]*self.t
            self.y=self.src[1]*(1-self.t)+self.dst[1]*self.t
        self.sprite.x,self.sprite.y=self.x,self.y; self.sprite.update(dt)
    def draw(self): self.sprite.draw()
    def reset(self): self.__init__()

class Enemy:
    def __init__(self,cx,cy,rect):
        self.cx,self.cy=cx,cy; self.x,self.y=to_px(cx,cy); self.territory=rect
        self.sprite=AnimatedSprite("slime",(self.x,self.y),{
            ("idle","right"):2,("idle","left"):2,("walk","right"):2,("walk","left"):2})
        self.moving,self.src,self.dst,self.t,self.cool=False,(0,0),(0,0),0,0
    def step(self):
        for _ in range(5):
            dx,dy=random.choice([(1,0),(-1,0),(0,1),(0,-1)])
            nx,ny=self.cx+dx,self.cy+dy
            if is_wall((nx,ny)) or not self.territory.collidepoint(nx,ny): continue
            self.cx,self.cy=nx,ny
            self.src,self.dst=(self.x,self.y),to_px(nx,ny)
            self.moving,self.t=True,0
            self.sprite.state="walk"; self.sprite.dir="left" if dx<0 else "right"; return
        self.sprite.state="idle"
    def update(self,dt):
        self.cool-=dt
        if self.moving:
            self.t+=dt/0.25
            if self.t>=1: self.t,self.moving=1,False; self.cool,self.sprite.state=0.5,"idle"
            self.x=self.src[0]*(1-self.t)+self.dst[0]*self.t
            self.y=self.src[1]*(1-self.t)+self.dst[1]*self.t
        elif self.cool<=0: self.step()
        self.sprite.x,self.sprite.y=self.x,self.y; self.sprite.update(dt)
    def draw(self): self.sprite.draw()

class Button:
    def __init__(self,text,y): self.text,self.r=text,Rect(WIDTH//2-120,y,240,60)
    def draw(self): screen.draw.filled_rect(self.r,(200,200,255)); screen.draw.rect(self.r,(0,0,100)); screen.draw.text(self.text,center=self.r.center,fontsize=36,color="black")
    def hit(self,pos): return self.r.collidepoint(pos)

class SmallButton:
    def __init__(self,text,x,y,w=120,h=36): self.text=text; self.r=Rect(x,y,w,h)
    def draw(self): screen.draw.filled_rect(self.r,(210,210,230)); screen.draw.rect(self.r,(30,30,60)); screen.draw.text(self.text,center=self.r.center,fontsize=22,color="black")
    def hit(self,pos): return self.r.collidepoint(pos)

btns=[Button("Iniciar",250),Button("Musica ON/OFF",350),Button("Sair do jogo",450)]

def make_game_buttons():
    x=12; return [SmallButton(f"Musica {'ON' if music_on else 'OFF'}",x,12),
                  SmallButton(f"Sons {'ON' if sfx_on else 'OFF'}",x,56),
                  SmallButton("Voltar ao inicio",x,100)]
game_btns=make_game_buttons()

hero=None; enemies=[]

def draw():
    screen.clear()
    if game_state==STATE_MENU:
        screen.fill((30,30,80)); screen.draw.text("Mini Roguelike",center=(WIDTH//2,120),fontsize=48,color="white")
        for b in btns: b.draw()
    elif game_state==STATE_GAME:
        for y,row in enumerate(RAW_MAP):
            for x,c in enumerate(row):
                col=(60,60,80) if c=="#" else (200,200,220)
                r=Rect(OFFSET_X+x*TILE,OFFSET_Y+y*TILE,TILE,TILE)
                screen.draw.filled_rect(r,col)
                if (x,y)==(DOOR_CX,DOOR_CY):
                    screen.draw.filled_rect(r.inflate(-8,-4),(40,160,40))
                    screen.draw.filled_circle((r.right-12,r.centery),3,(230,230,120))
        for e in enemies: e.draw()
        hero.draw()
        for b in game_btns: b.draw()
    else:
        screen.fill((20,30,20))
        screen.draw.text("Issooo!",center=(WIDTH//2,180),fontsize=72,color="white")
        screen.draw.text("Venceu!",center=(WIDTH//2,260),fontsize=48,color="white")
        screen.draw.text("ENTER ou clique para voltar ao menu",center=(WIDTH//2,360),fontsize=28,color="white")

def update(dt):
    if game_state!=STATE_GAME: return
    hero.update(dt)
    for e in enemies:
        e.update(dt)
        if hero.sprite.rect.colliderect(e.sprite.rect):
            play_sound("hit"); hero.sprite.state="hurt"; hero.sprite.dir="left"; clock.schedule(hero.reset,0.5)
    if (hero.cx,hero.cy)==(DOOR_CX,DOOR_CY):
        try: sounds.win.play()
        except: pass
        set_win()

def on_key_down(key):
    global game_state,music_on,sfx_on,game_btns
    if game_state==STATE_GAME:
        if   key==keys.ESCAPE: set_menu()
        elif key==keys.M: music_on=not music_on; toggle_music(); game_btns[0].text=f"Musica {'ON' if music_on else 'OFF'}"
        elif key==keys.N: sfx_on=not sfx_on; game_btns[1].text=f"Sons {'ON' if sfx_on else 'OFF'}"
        elif key in (keys.LEFT,keys.A):  hero.want_move(-1,0)
        elif key in (keys.RIGHT,keys.D): hero.want_move(1,0)
        elif key in (keys.UP,keys.W):    hero.want_move(0,-1)
        elif key in (keys.DOWN,keys.S):  hero.want_move(0,1)
    elif game_state==STATE_WIN and key in (keys.RETURN,keys.SPACE): set_menu()

def on_mouse_down(pos):
    global game_state,music_on,sfx_on,game_btns
    if game_state==STATE_MENU:
        if   btns[0].hit(pos): set_game()
        elif btns[1].hit(pos): music_on=not music_on; toggle_music(); btns[1].text=f"Musica {'ON' if music_on else 'OFF'}"
        elif btns[2].hit(pos): exit()
    elif game_state==STATE_GAME:
        if   game_btns[0].hit(pos): music_on=not music_on; toggle_music(); game_btns[0].text=f"Musica {'ON' if music_on else 'OFF'}"
        elif game_btns[1].hit(pos): sfx_on=not sfx_on; game_btns[1].text=f"Sons {'ON' if sfx_on else 'OFF'}"
        elif game_btns[2].hit(pos): set_menu()
    elif game_state==STATE_WIN: set_menu()

def set_game():
    global game_state,hero,enemies,game_btns
    hero=Hero(); enemies=[Enemy(10,2,Rect(8,1,10,4)),Enemy(20,3,Rect(18,1,6,5))]
    game_btns=make_game_buttons(); game_state=STATE_GAME; toggle_music()

def set_menu(): 
    global game_state; game_state=STATE_MENU

def set_win():
    global game_state; game_state=STATE_WIN

def toggle_music():
    if music_on: music.play("bgm"); music.set_volume(0.6)
    else: music.stop()
