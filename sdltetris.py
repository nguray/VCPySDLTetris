"""     Simple Tetris using sdl2.   """
"""             2022                """
"""      Raymond NGUYEN THANH       """
import os
from os import path
from random import randint
import sys
import ctypes
import sdl2
import sdl2.ext
from sdl2 import (pixels, render, events as sdlevents, surface, error,timer)
from sdl2.sdlttf import *
from sdl2.sdlmixer import *
from enum import Enum, unique

WIN_WIDTH   = 480
WIN_HEIGHT  = 560
NB_ROWS     = 20
NB_COLUMNS  = 12
LEFT        = 10
TOP         = 10
CELL_SIZE  = int(WIN_WIDTH / (NB_COLUMNS + 7))

@unique
class GameMode(Enum):
    StandBy = 1
    Play = 2
    GameOver = 3
    HightScore = 4

TETRIS_COLORS = [
    sdl2.SDL_Color(0x0,0x0,0x0,0x0),
    sdl2.SDL_Color(0xFF,0x60,0x60,0xFF),
    sdl2.SDL_Color(0x60,0xFF,0x60,0xFF),
    sdl2.SDL_Color(0x60,0x60,0xFF,0xFF),
    sdl2.SDL_Color(0xCC,0xCC,0x60,0xFF),
    sdl2.SDL_Color(0xCC,0x60,0xCC,0xFF),
    sdl2.SDL_Color(0x60,0xCC,0xCC,0xFF),
    sdl2.SDL_Color(0xDA,0xAA,0x00,0xFF)
]

class Vectoi2i:
    def __init__(self, x:int, y:int):
        self.x = int(x)
        self.y = int(y)

class TetrisShape :
    def __init__(self, x:int =0, y:int =0, itype:int =0):
        self.x = x
        self.y = y 
        self.type = itype
        self.shapes = {
            1:[Vectoi2i(0,-1),Vectoi2i(0,0),Vectoi2i(-1,0),Vectoi2i(-1,1)],
            2:[Vectoi2i(0,-1),Vectoi2i(0,0),Vectoi2i(1,0),Vectoi2i(1,1)],
            3:[Vectoi2i(0,-1),Vectoi2i(0,0),Vectoi2i(0,1),Vectoi2i(0,2)],
            4:[Vectoi2i(-1,0),Vectoi2i(0,0),Vectoi2i(1,0),Vectoi2i(0,1)],
            5:[Vectoi2i(0,0),Vectoi2i(1,0),Vectoi2i(0,1),Vectoi2i(1,1)],
            6:[Vectoi2i(-1,-1),Vectoi2i(0,-1),Vectoi2i(0,0),Vectoi2i(0,1)],
            7:[Vectoi2i(1,-1),Vectoi2i(0,-1),Vectoi2i(0,0),Vectoi2i(0,1)]
        }
        self.init_shape(itype)

    def init_shape(self,ityp:int):
        v = self.shapes.get(ityp)
        if v!=None:
            self.v = v
        else:
            self.v = [Vectoi2i(0,0),Vectoi2i(0,0),Vectoi2i(0,0),Vectoi2i(0,0)]
        # match ityp:
        #     case 1:
        #         self.v = [Vectoi2i(0,-1),Vectoi2i(0,0),Vectoi2i(-1,0),Vectoi2i(-1,1)]
        #     case 2:
        #         self.v = [Vectoi2i(0,-1),Vectoi2i(0,0),Vectoi2i(1,0),Vectoi2i(1,1)]
        #     case 3:
        #         self.v = [Vectoi2i(0,-1),Vectoi2i(0,0),Vectoi2i(0,1),Vectoi2i(0,2)]
        #     case 4:
        #         self.v = [Vectoi2i(-1,0),Vectoi2i(0,0),Vectoi2i(1,0),Vectoi2i(0,1)]
        #     case 5:
        #         self.v = [Vectoi2i(0,0),Vectoi2i(1,0),Vectoi2i(0,1),Vectoi2i(1,1)]
        #     case 6:
        #         self.v = [Vectoi2i(-1,-1),Vectoi2i(0,-1),Vectoi2i(0,0),Vectoi2i(0,1)]
        #     case 7:
        #         self.v = [Vectoi2i(1,-1),Vectoi2i(0,-1),Vectoi2i(0,0),Vectoi2i(0,1)]
        #     case _:
        #         self.v = [Vectoi2i(0,0),Vectoi2i(0,0),Vectoi2i(0,0),Vectoi2i(0,0)]

    def rotate_left(self):
        if self.type != 5:
            for i in range(0,4):
                x = self.v[i].y
                y = -self.v[i].x
                self.v[i].x = x
                self.v[i].y = y

    def rotate_right(self):
        if self.type != 5:
            for i in range(0,4):
                x = -self.v[i].y
                y = self.v[i].x
                self.v[i].x = x
                self.v[i].y = y

    def is_in_board(self)->bool:
        for i in range(0,4):
            x = self.v[i].x + self.x
            y = self.v[i].y + self.y
            if (x < 0) or (x >= NB_COLUMNS) or (y >= NB_ROWS):
                return False
        return True

    def hit_ground(self, board)->bool:
        for i in range(0,4):
            y = self.v[i].y + self.y
            if y>=0:
                x = self.v[i].x + self.x
                if board[x+y*NB_COLUMNS]!=0:
                    return True

        return False

    def max_x(self)->int:
        maxi = self.v[0].x + self.x
        for i in range(1,4):
            x = self.v[i].x + self.x
            if x>maxi:
                maxi = x
        return maxi

    def min_x(self)->int:
        min = self.v[0].x + self.x
        for i in range(1,4):
            x = self.v[i].x + self.x
            if x<min:
                min = x
        return min

    def max_y(self)->int:
        max = self.v[0].y + self.y
        for i in range(1,4):
            y = self.v[i].y + self.y
            if y<max:
                max = y
        return max

    def draw(self,renderer):
        # 
        col = TETRIS_COLORS[self.type]
        sdl2.SDL_SetRenderDrawColor(renderer, col.r, col.g, col.b, sdl2.SDL_ALPHA_OPAQUE)
        rects = []
        a = CELL_SIZE-2
        for v in self.v:
            x = self.x + v.x
            y = self.y + v.y
            if y>=0:
                rects.append(sdl2.SDL_Rect(LEFT+x*CELL_SIZE+1,TOP+y*CELL_SIZE+1,a,a))
        cnt = len(rects)
        if cnt>0:
            rectsArray = ctypes.pointer((sdl2.SDL_Rect * cnt)())
            for i in range(cnt):
                rectsArray.contents[i] = rects[i]
            sdl2.SDL_RenderFillRects(renderer,rectsArray.contents[0],cnt)

class HighScore:
    def __init__(self, name:str, score:int):
        self.name = name
        self.score = score

class Game:
    def __init__(self):
        self.hightScores = [HighScore("--------",0) for i in range(10)]
        self.board = [0 for i in range(0,NB_COLUMNS*NB_ROWS)]
        self.score = 0
        self.curTetromino = TetrisShape(5,4,0)
        self.nextTetromino = TetrisShape(NB_COLUMNS + 3, int(NB_ROWS / 2),randint(1, 7))
        self.mode = GameMode.StandBy
        self.processEvent = self.processEventStandby
        self.fPlaySuccessSound = False
        self.fDropTetromino = False
        self.fFastDown = False
        self.fPause = False
        self.velocityH = 0
        self.idHightScore = -1
        self.player_name = ""
        self.fQuit = False
        self.tblChars = {
            sdl2.SDLK_a:'A',
            sdl2.SDLK_b:'B',
            sdl2.SDLK_c:'C',
            sdl2.SDLK_d:'D',
            sdl2.SDLK_e:'E',
            sdl2.SDLK_f:'F',
            sdl2.SDLK_g:'G',
            sdl2.SDLK_h:'H',
            sdl2.SDLK_i:'I',
            sdl2.SDLK_j:'J',
            sdl2.SDLK_k:'K',
            sdl2.SDLK_l:'L',
            sdl2.SDLK_m:'M',
            sdl2.SDLK_n:'N',
            sdl2.SDLK_o:'O',
            sdl2.SDLK_p:'P',
            sdl2.SDLK_q:'Q',
            sdl2.SDLK_r:'R',
            sdl2.SDLK_s:'S',
            sdl2.SDLK_t:'T',
            sdl2.SDLK_u:'U',
            sdl2.SDLK_v:'V',
            sdl2.SDLK_w:'W',
            sdl2.SDLK_x:'X',
            sdl2.SDLK_y:'Y',
            sdl2.SDLK_z:'Z',
            sdl2.SDLK_0:'0',
            sdl2.SDLK_1:'1',
            sdl2.SDLK_2:'2',
            sdl2.SDLK_3:'3',
            sdl2.SDLK_4:'4',
            sdl2.SDLK_5:'5',
            sdl2.SDLK_6:'6',
            sdl2.SDLK_7:'7',
            sdl2.SDLK_8:'8',
            sdl2.SDLK_9:'9',
            sdl2.SDLK_KP_1:'1',
            sdl2.SDLK_KP_2:'2',
            sdl2.SDLK_KP_3:'3',
            sdl2.SDLK_KP_4:'4',
            sdl2.SDLK_KP_5:'5',
            sdl2.SDLK_KP_6:'6',
            sdl2.SDLK_KP_7:'7',
            sdl2.SDLK_KP_8:'8',
            sdl2.SDLK_KP_9:'9'
        }

    def init_board(self):
        self.board = [0 for i in range(0,NB_COLUMNS*NB_ROWS)]

    def saveHightScore(self):
        with open("highscores.txt",'w') as f:
            for hs in self.hightScores:
                strLi = "{};{}\n".format(hs.name,hs.score)
                f.write(strLi)

    def loadHightScore(self):
        if path.exists("highscores.txt"):
            with open("highscores.txt",'r') as f:
                strLines = f.readlines()
                i = 0
                for strL in strLines:
                    if len(strL)>1:
                        name,score = strL.split(';')
                        self.hightScores[i].name = name
                        self.hightScores[i].score = int(score)
                        i += 1
  

    def is_over(self)->bool:
        for x in range(0,NB_COLUMNS):
            if self.board[x] != 0:
                return True
        return False

    def erase_completed_lines(self)->int:
        nbL = 0
        for y in range(0,NB_ROWS):
            #-- Check completed line
            f_complete = True
            for x in range(0,NB_COLUMNS):
                if self.board[x + y * NB_COLUMNS] == 0 :
                    f_complete = False
                    break
            
            if f_complete :
                nbL += 1
                #-- Shift down the game board
                y1 = y
                while y1 > 0 :
                    ySrcOffset = (y1 - 1) * NB_COLUMNS
                    yDesOffset = y1 * NB_COLUMNS
                    for x in range(0,NB_COLUMNS) :
                        self.board[x + yDesOffset] = self.board[x + ySrcOffset]
                    y1 -= 1
            
        return nbL

    def freeze_tetromino(self)->bool:
        for i in range(0,4):
            y = self.curTetromino.v[i].y + self.curTetromino.y
            if y>=0:
                x = self.curTetromino.v[i].x+self.curTetromino.x
                self.board[x+y*NB_COLUMNS] = self.curTetromino.type

        self.curTetromino = TetrisShape(5,0,self.nextTetromino.type)
        self.curTetromino.y = -self.curTetromino.max_y()-1
        self.nextTetromino = TetrisShape(NB_COLUMNS+3,int(NB_ROWS/2),randint(1, 7))

        nb_lines = self.erase_completed_lines()
        if nb_lines>0:
            self.score += self.compute_score(nb_lines)
            self.fPlaySuccessSound = True
            return True

        return False

    def compute_score(self, nb_lines: int) -> int:
        if nb_lines==1:
            return 40
        elif nb_lines==2:
            return 100
        elif nb_lines==3:
            return 300
        elif nb_lines==4:
            return 1200
        elif nb_lines>4:
            return 2000
        return 0

    
    def draw(self,renderer:sdl2.SDL_Renderer):
        #
        sdl2.SDL_SetRenderDrawColor(renderer, 20, 20, 100, sdl2.SDL_ALPHA_OPAQUE)
        sdl2.SDL_RenderFillRect(renderer,sdl2.SDL_Rect(LEFT,TOP,NB_COLUMNS*CELL_SIZE,NB_ROWS*CELL_SIZE))

        a = CELL_SIZE - 2
        for y in range(0,NB_ROWS):
            for x in range(0,NB_COLUMNS):
                typ = self.board[x + y * NB_COLUMNS]
                if typ != 0 :
                    c = TETRIS_COLORS[typ]
                    l = (x * (CELL_SIZE) + LEFT + 1)
                    t = (y * (CELL_SIZE) + TOP + 1)
                    sdl2.SDL_SetRenderDrawColor(renderer, c.r, c.g, c.b, sdl2.SDL_ALPHA_OPAQUE)
                    sdl2.SDL_RenderFillRect(renderer,sdl2.SDL_Rect(l,t,a,a))

    def processEventStandby(self,event:sdl2.SDL_Event)->bool:
        running = True
        if event.type == sdl2.SDL_QUIT:
            self.fQuit = True
            running = False
        elif event.type == sdl2.SDL_KEYDOWN:
            if event.key.keysym.sym == sdl2.SDLK_SPACE:
                if self.mode is GameMode.StandBy :
                    self.fPause = False
                    self.mode = GameMode.Play
                    self.processEvent = self.processEventPlay
                    self.curTetromino = TetrisShape(5,0,self.nextTetromino.type)
                    self.curTetromino.y = -2
                    self.nextTetromino = TetrisShape(NB_COLUMNS+3,int(NB_ROWS/2),randint(1, 7))
            elif event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                running = False
        return running

    def processEventGameOver(self,event:sdl2.SDL_Event)->bool:
        running = True
        if event.type == sdl2.SDL_QUIT:
            self.fQuit = True
            running = False
        elif event.type == sdl2.SDL_KEYDOWN:
            if event.key.keysym.sym == sdl2.SDLK_SPACE:
                self.mode = GameMode.StandBy
                self.processEvent = self.processEventStandby
            elif event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                running = False
        return running

    def setHightScoreName(self,name:str):
        if self.idHightScore>=0:
            self.hightScores[self.idHightScore].name = name

    def processEventHightScores(self,event:sdl2.SDL_Event)->bool:
        running = True
        if event.type == sdl2.SDL_QUIT:
            self.fQuit = True
            running = False
        elif event.type == sdl2.SDL_KEYDOWN:
            if event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                running = False
            elif event.key.keysym.sym == sdl2.SDLK_BACKSPACE:
                if len(self.player_name)>0:
                    self.player_name = self.player_name[:-1]
                    self.setHightScoreName(self.player_name)                
            elif event.key.keysym.sym == sdl2.SDLK_RETURN:
                if self.idHightScore>=-1:
                    if len(self.player_name)==0:
                        self.player_name = "XXXXXXXX"
                    self.setHightScoreName(self.player_name)
                    self.saveHightScore()
                self.mode = GameMode.StandBy
                self.processEvent = self.processEventStandby
            else:
                c = self.tblChars.get(event.key.keysym.sym)
                if c!=None:
                    self.player_name = self.player_name + c
                    self.setHightScoreName(self.player_name)

        return running

    def processEventPlay(self,event:sdl2.SDL_Event)->bool:
        running = True
        if event.type == sdl2.SDL_QUIT:
            self.fQuit = True
            running = False
        elif event.type == sdl2.SDL_KEYDOWN:
            if event.key.keysym.sym == sdl2.SDLK_LEFT:
                self.velocityH = -1
            elif event.key.keysym.sym == sdl2.SDLK_RIGHT:
                self.velocityH = 1
            elif event.key.keysym.sym == sdl2.SDLK_UP:
                self.curTetromino.rotate_left()
            elif event.key.keysym.sym == sdl2.SDLK_DOWN:
                self.fFastDown = True
            elif event.key.keysym.sym == sdl2.SDLK_SPACE:
                self.fDropTetromino = True
            elif event.key.keysym.sym == sdl2.SDLK_PAUSE:
                self.fPause ^= True
            elif event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                running = False
        elif event.type == sdl2.SDL_KEYUP:
            if event.key.keysym.sym == sdl2.SDLK_LEFT or event.key.keysym.sym == sdl2.SDLK_RIGHT:
                self.velocityH = 0
            elif event.key.keysym.sym == sdl2.SDLK_DOWN:
                self.fFastDown = False
        return running

    def isHightScore(self)->int:
        for i, hs in enumerate(self.hightScores):
            if self.score>hs.score:
                self.idHightScore = i
                return i
        return -1

    def insertHightScore(self, id:int, name:str, score:int):
        if id>=0:
            self.hightScores.insert(id,HighScore(name,score))
            self.hightScores.pop()
            # for i in range(9,id,-1):
            #     iPrev = i - 1
            #     self.hightScores[i].name = self.hightScores[iPrev].name
            #     self.hightScores[i].score = self.hightScores[iPrev].score
            # self.hightScores[id].name = name
            # self.hightScores[id].score = score 

    def drawScore(self,renderer:sdl2.SDL_Renderer,tt_font:sdl2.sdlttf.TTF_Font):
        #---------------------
        x = LEFT
        y = (NB_ROWS+1)*CELL_SIZE
        textScore = 'SCORE : {:06d}'.format(self.score)
        surf = TTF_RenderText_Blended(tt_font, str.encode(textScore), sdl2.SDL_Color(255, 255, 0,255))
        texture = sdl2.SDL_CreateTextureFromSurface(renderer, surf)        
        iW = ctypes.pointer(ctypes.c_int(0))
        iH = ctypes.pointer(ctypes.c_int(0))
        sdl2.SDL_QueryTexture(texture, None, None, iW, iH)
        dst = sdl2.SDL_Rect(int(x), int(y),iW.contents.value,iH.contents.value)
        sdl2.SDL_RenderCopy(renderer, texture, None, dst)
        sdl2.SDL_FreeSurface(surf)
        sdl2.SDL_DestroyTexture(texture)


    def drawHighScores(self,renderer:sdl2.SDL_Renderer,tt_font:sdl2.sdlttf.TTF_Font):
        #---------------------
        xCol0 = LEFT + CELL_SIZE
        xCol1 = LEFT + 7*CELL_SIZE
        title = "HIGHT SCORES"
        surf = TTF_RenderText_Blended(tt_font, str.encode(title), sdl2.SDL_Color(255, 0, 0,255))
        texture = sdl2.SDL_CreateTextureFromSurface(renderer, surf)        
        iW = ctypes.pointer(ctypes.c_long(0))
        iH = ctypes.pointer(ctypes.c_long(0))
        sdl2.SDL_QueryTexture(texture, None, None, iW, iH)
        y = TOP + CELL_SIZE
        dst = sdl2.SDL_Rect(int((LEFT+(NB_COLUMNS*CELL_SIZE-(iW.contents.value)))/2), int(y),iW.contents.value,iH.contents.value)
        sdl2.SDL_RenderCopy(renderer, texture, None, dst)
        sdl2.SDL_FreeSurface(surf)
        sdl2.SDL_DestroyTexture(texture)

        y += 3 * iH.contents.value
        for i in range(0,10):
            hs = self.hightScores[i]
            # Name
            surf = TTF_RenderText_Blended(tt_font, str.encode(hs.name), sdl2.SDL_Color(255, 0, 0,255))
            texture = sdl2.SDL_CreateTextureFromSurface(renderer, surf)        
            iW = ctypes.pointer(ctypes.c_long(0))
            iH = ctypes.pointer(ctypes.c_long(0))
            sdl2.SDL_QueryTexture(texture, None, None, iW, iH)
            dst = sdl2.SDL_Rect(int(xCol0), int(y),iW.contents.value,iH.contents.value)
            sdl2.SDL_RenderCopy(renderer, texture, None, dst)
            sdl2.SDL_FreeSurface(surf)
            sdl2.SDL_DestroyTexture(texture)
            # Score
            scoreTxt = "{:06d}".format(hs.score)
            surf = TTF_RenderText_Blended(tt_font, str.encode(scoreTxt), sdl2.SDL_Color(255, 255, 0,255))
            texture = sdl2.SDL_CreateTextureFromSurface(renderer, surf)        
            iW = ctypes.pointer(ctypes.c_long(0))
            iH = ctypes.pointer(ctypes.c_long(0))
            sdl2.SDL_QueryTexture(texture, None, None, iW, iH)
            dst = sdl2.SDL_Rect(int(xCol1), int(y),iW.contents.value,iH.contents.value)
            sdl2.SDL_RenderCopy(renderer, texture, None, dst)
            sdl2.SDL_FreeSurface(surf)
            sdl2.SDL_DestroyTexture(texture)
            #--
            y += iH.contents.value + 2

    def drawStanBy(self,renderer:sdl2.SDL_Renderer,tt_font:sdl2.sdlttf.TTF_Font):
        #---------------------
        title = "TETRIS in SDL2"
        surf = TTF_RenderText_Blended(tt_font, str.encode(title), sdl2.SDL_Color(255, 255, 0,255))
        texture = sdl2.SDL_CreateTextureFromSurface(renderer, surf)        
        iW = ctypes.pointer(ctypes.c_int(0))
        iH = ctypes.pointer(ctypes.c_int(0))
        sdl2.SDL_QueryTexture(texture, None, None, iW, iH)
        y = TOP + 6*CELL_SIZE
        dst = sdl2.SDL_Rect(int((LEFT+(NB_COLUMNS*CELL_SIZE-(iW.contents.value)))/2), int(y),iW.contents.value,iH.contents.value)
        sdl2.SDL_RenderCopy(renderer, texture, None, dst)
        sdl2.SDL_FreeSurface(surf)
        sdl2.SDL_DestroyTexture(texture)

        y += 2*iH.contents.value
        title = "Press SPACE to Play"
        surf = TTF_RenderText_Blended(tt_font, str.encode(title), sdl2.SDL_Color(255, 255, 0,255))
        texture = sdl2.SDL_CreateTextureFromSurface(renderer, surf)        
        iW = ctypes.pointer(ctypes.c_int(0))
        iH = ctypes.pointer(ctypes.c_int(0))
        sdl2.SDL_QueryTexture(texture, None, None, iW, iH)
        dst = sdl2.SDL_Rect(int((LEFT+(NB_COLUMNS*CELL_SIZE-(iW.contents.value)))/2), int(y),iW.contents.value,iH.contents.value)
        sdl2.SDL_RenderCopy(renderer, texture, None, dst)
        sdl2.SDL_FreeSurface(surf)
        sdl2.SDL_DestroyTexture(texture)

    def drawGameOver(self,renderer:sdl2.SDL_Renderer,tt_font:sdl2.sdlttf.TTF_Font):
        #---------------------
        title = "Game Over"
        surf = TTF_RenderText_Blended(tt_font, str.encode(title), sdl2.SDL_Color(255, 255, 0,255))
        texture = sdl2.SDL_CreateTextureFromSurface(renderer, surf)        
        iW = ctypes.pointer(ctypes.c_int(0))
        iH = ctypes.pointer(ctypes.c_int(0))
        sdl2.SDL_QueryTexture(texture, None, None, iW, iH)
        y = TOP + 6*CELL_SIZE
        dst = sdl2.SDL_Rect(int((LEFT+(NB_COLUMNS*CELL_SIZE-(iW.contents.value)))/2), int(y),iW.contents.value,iH.contents.value)
        sdl2.SDL_RenderCopy(renderer, texture, None, dst)
        sdl2.SDL_FreeSurface(surf)
        sdl2.SDL_DestroyTexture(texture)

        y += 2*iH.contents.value
        title = "Press SPACE to Continue"
        surf = TTF_RenderText_Blended(tt_font, str.encode(title), sdl2.SDL_Color(255, 255, 0,255))
        texture = sdl2.SDL_CreateTextureFromSurface(renderer, surf)        
        iW = ctypes.pointer(ctypes.c_int(0))
        iH = ctypes.pointer(ctypes.c_int(0))
        sdl2.SDL_QueryTexture(texture, None, None, iW, iH)
        dst = sdl2.SDL_Rect(int((LEFT+(NB_COLUMNS*CELL_SIZE-(iW.contents.value)))/2), int(y),iW.contents.value,iH.contents.value)
        sdl2.SDL_RenderCopy(renderer, texture, None, dst)
        sdl2.SDL_FreeSurface(surf)
        sdl2.SDL_DestroyTexture(texture)


def run1():

    # initialize
    sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO|sdl2.SDL_INIT_TIMER|sdl2.SDL_INIT_AUDIO)

    sdl2.sdlttf.TTF_Init()

    # create window
    win = sdl2.SDL_CreateWindow(b"Tetris SDL",
            sdl2.SDL_WINDOWPOS_CENTERED,
            sdl2.SDL_WINDOWPOS_CENTERED,
            WIN_WIDTH, WIN_HEIGHT, sdl2.SDL_WINDOW_SHOWN)
    
    fname = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "resources", "sansation.ttf")
    tt_font = sdl2.sdlttf.TTF_OpenFont(str.encode(fname), 18)
    sdl2.sdlttf.TTF_SetFontStyle(tt_font, TTF_STYLE_BOLD|TTF_STYLE_ITALIC)

    mname = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "resources", "Tetris.ogg")
    Mix_OpenAudio(44100, MIX_DEFAULT_FORMAT, MIX_DEFAULT_CHANNELS, 1024)
    tetris_music=Mix_LoadMUS(str.encode(mname))
    Mix_VolumeMusic(0)
    Mix_PlayMusic(tetris_music,-1)

    cname = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "resources", "109662__grunz__success.wav")
    succes_sound = Mix_LoadWAV(str.encode(cname))
    Mix_Volume(-1, 15)

    # create renderer
    renderer = sdl2.SDL_CreateRenderer(win, -1, sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_PRESENTVSYNC)
    
    # fill background with white
    #sdl2.SDL_SetRenderDrawColor(renderer, 255, 255, 255, sdl2.SDL_ALPHA_OPAQUE)
    #sdl2.SDL_RenderClear(renderer)
    
    # draw a black line
    #sdl2.SDL_SetRenderDrawColor(renderer, 255, 0, 0, sdl2.SDL_ALPHA_OPAQUE)
    
    # create python list of SDL_Points
    #points = [sdl2.SDL_Point(0,0), sdl2.SDL_Point(640,480),sdl2.SDL_Point(640,0), sdl2.SDL_Point(0,480)] 
    # convert SDL_Point list to SDL_Point C array
    #cnt = len(points)
    #pointsArray = ctypes.pointer((sdl2.SDL_Point * cnt)())
    #for i in range(cnt):
    #    pointsArray.contents[i] = points[i]
    #sdl2.SDL_RenderDrawLines(renderer, pointsArray.contents[0], cnt)

    # 
    # col = TETRIS_COLORS[3]
    # sdl2.SDL_SetRenderDrawColor(renderer, col.r, col.g, col.b, sdl2.SDL_ALPHA_OPAQUE)
    # a = CELL_SIZE-2
    # rects = [sdl2.SDL_Rect(5,5,a,a),sdl2.SDL_Rect(5,5+CELL_SIZE,a,a),sdl2.SDL_Rect(5,5+2*CELL_SIZE,a,a)]
    # cnt = len(rects)
    # rectsArray = ctypes.pointer((sdl2.SDL_Rect * cnt)())
    # for i in range(cnt):
    #     rectsArray.contents[i] = rects[i]
    # sdl2.SDL_RenderFillRects(renderer,rectsArray.contents[0],cnt)

    # --
    game = Game()

    game.loadHightScore()

    curTime = sdl2.timer.SDL_GetTicks()
    curTime1 = curTime
    

    #game.score = 500

    # run event loop
    running = True

    while running:

        events = sdl2.ext.get_events()
        for event in events:
            running = game.processEvent(event)
            if game.fQuit:
                break
            if not running:
                game.curTetromino.type = 0
                id = game.isHightScore()
                if id>=0:
                    game.insertHightScore(id,game.player_name,game.score)
                    game.init_board()
                    game.score = 0
                    game.mode = GameMode.HightScore
                    game.processEvent = game.processEventHightScores
                    running = True

        #
        if game.mode is GameMode.Play:
            fAlreadyMoveH = False
            nbTicks = sdl2.timer.SDL_GetTicks()
            elapsed = nbTicks - curTime
            if elapsed>100:
                curTime = nbTicks
                game.curTetromino.x += game.velocityH
                if not game.curTetromino.is_in_board():
                    game.curTetromino.x -= game.velocityH
                else:
                    if game.curTetromino.hit_ground(game.board):
                        game.curTetromino.x -= game.velocityH
                fAlreadyMoveH = True

            if game.fDropTetromino:
                curTime1 = nbTicks
                game.curTetromino.y += 1
                if not game.curTetromino.is_in_board():
                    game.curTetromino.y -= 1
                    game.freeze_tetromino()
                    game.fDropTetromino = False
                else:
                    if game.curTetromino.hit_ground(game.board):
                        game.curTetromino.y -= 1
                        game.freeze_tetromino()
                        game.fDropTetromino = False
            else:
                if game.fFastDown:
                    limit = 100
                else:
                    limit = 600
                elapsed = nbTicks - curTime1
                if elapsed>limit and game.fPause==False:
                    curTime1 = nbTicks
                    if not fAlreadyMoveH:
                        if not game.curTetromino.is_in_board():
                            game.curTetromino.x -= game.velocityH
                        else:
                            if game.curTetromino.hit_ground(game.board):
                                game.curTetromino.x -= game.velocityH
                    game.curTetromino.y += 1
                    game.nextTetromino.rotate_right()
                    if not game.curTetromino.is_in_board():
                        game.curTetromino.y -= 1
                        game.freeze_tetromino()
                    else:
                        if game.curTetromino.hit_ground(game.board):
                            game.curTetromino.y -= 1
                            game.freeze_tetromino()

            if game.is_over():
                game.curTetromino.type = 0
                game.init_board()
                id = game.isHightScore()
                if id>=0:
                    game.insertHightScore(id,game.player_name,game.score)
                    game.score = 0
                    game.mode = GameMode.HightScore
                    game.processEvent = game.processEventHightScores
                else:
                    game.mode = GameMode.GameOver
                    game.processEvent = game.processEventGameOver


        #
        sdl2.SDL_SetRenderDrawColor(renderer, 30, 30, 80, sdl2.SDL_ALPHA_OPAQUE)
        sdl2.SDL_RenderClear(renderer)

        game.draw(renderer)

        if game.mode is GameMode.HightScore:
            game.drawHighScores(renderer, tt_font)
        elif game.mode is GameMode.GameOver:
            game.drawGameOver(renderer, tt_font)
        elif game.mode is GameMode.StandBy:
            game.drawStanBy(renderer, tt_font)

        if game.curTetromino.type!=0:
            game.curTetromino.draw(renderer)

        game.nextTetromino.draw(renderer)

        if game.fPlaySuccessSound:
            Mix_PlayChannel(-1, succes_sound, 0)
            game.fPlaySuccessSound = False

        # Draw Score Text
        game.drawScore(renderer,tt_font)

        sdl2.SDL_RenderPresent(renderer)

        sdl2.SDL_Delay(20)
    
    #
    game.saveHightScore()

    # clean up
    sdl2.SDL_DestroyRenderer(renderer)
    sdl2.SDL_DestroyWindow(win)
    TTF_CloseFont(tt_font)
    sdl2.sdlttf.TTF_Quit()
    Mix_CloseAudio()
    sdl2.SDL_Quit()

    
def run():

    #sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)

    sdl2.ext.init()

    # window = sdl2.SDL_CreateWindow(b"SDL Tetris",
    #                                 sdl2.SDL_WINDOWPOS_CENTERED,
    #                                 sdl2.SDL_WINDOWPOS_CENTERED,
    #                                 WIN_WIDTH, WIN_HEIGHT, sdl2.SDL_WINDOW_SHOWN)

    window = sdl2.ext.Window("SDL Tetris", size=(WIN_WIDTH, WIN_HEIGHT))
    window.show()

    fname = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "resources", "hello.bmp")

    #image = sdl2.SDL_LoadBMP(fname.encode("utf-8"))
    #windowsurface = sdl2.SDL_GetWindowSurface(window)
    #sdl2.SDL_BlitSurface(image, None, windowsurface, None)
    #sdl2.SDL_UpdateWindowSurface(window)
    #sdl2.SDL_FreeSurface(image)
    #renderer = sdl2.SDL_CreateRenderer(window,-1,sdl2.SDL_RENDERER_ACCELERATED)

    renderer = sdl2.ext.Renderer(window)
    renderer.color = sdl2.SDL_Color(0,0,0,255)
    renderer.clear()

    rects = []
    rects.append((5,5,CELL_SIZE,CELL_SIZE))
    rects.append((5,35,CELL_SIZE,CELL_SIZE))
    renderer.fill(rects,color=(0,255,0,255))
    renderer.present()

    # sdl2.SDL_RenderClear(renderer);

    # sdl2.SDL_SetRenderDrawColor(renderer,255, 0, 0, 255)
    # sdl2.SDL_RenderDrawLine(renderer,10,10,200,200)

    #rect = sdl2.SDL_Rect(5,5,25,25)
    #sdl2.SDL_RenderFillRect(renderer,rect)

    #sdl2.SDL_RenderPresent(renderer);

    running = True
    event = sdl2.SDL_Event()
    while running:
        for event in sdl2.ext.get_events():
            if event.type == sdl2.SDL_QUIT:
                running = False
                break
        sdl2.SDL_Delay(10)

    sdl2.ext.quit()

    #sdl2.SDL_DestroyWindow(window)
    #sdl2.SDL_Quit()

    return 0


if __name__ == "__main__":
    sys.exit(run1())