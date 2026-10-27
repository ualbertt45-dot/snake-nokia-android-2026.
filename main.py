import random
from pathlib import Path
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line, RoundedRectangle
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp

COLS, ROWS = 22, 26
BG = (0.67, 0.75, 0.48, 1)
DARK = (0.14, 0.24, 0.14, 1)
MID = (0.30, 0.42, 0.23, 1)

class SnakeGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.score_label = Label(text='', bold=True, color=DARK, font_size='20sp', size_hint=(None,None))
        self.hint = Label(text='TOQUE EM INICIAR', color=DARK, font_size='14sp', size_hint=(None,None))
        self.add_widget(self.score_label)
        self.add_widget(self.hint)
        self.buttons = {}
        for label, direction in [('▲',(0,1)), ('▼',(0,-1)), ('◀',(-1,0)), ('▶',(1,0))]:
            b = Button(text=label, font_size='26sp', bold=True, background_normal='', background_color=MID, color=(1,1,1,1))
            b.bind(on_press=lambda instance, d=direction: self.turn(d))
            self.add_widget(b)
            self.buttons[label] = b
        self.start_button = Button(text='INICIAR', bold=True, background_normal='', background_color=DARK)
        self.start_button.bind(on_press=self.start)
        self.add_widget(self.start_button)
        self.pause_button = Button(text='PAUSAR', bold=True, background_normal='', background_color=MID)
        self.pause_button.bind(on_press=self.pause)
        self.add_widget(self.pause_button)
        self.bind(size=self.layout_ui, pos=self.layout_ui)
        self.reset()
        Clock.schedule_interval(self.tick, 1 / 25)
        Window.bind(on_key_down=self.key_down)

    def reset(self):
        self.snake = [(COLS//2, ROWS//2), (COLS//2-1, ROWS//2)]
        self.direction = (1,0)
        self.next_direction = self.direction
        self.food = self.new_food()
        self.score = 0
        self.elapsed = 0
        self.state = 'ready'
        self.update_ui()
        self.draw()

    def new_food(self):
        free = [(x,y) for x in range(COLS) for y in range(ROWS) if (x,y) not in self.snake]
        return random.choice(free) if free else None

    def start(self, *_):
        self.reset()
        self.state = 'playing'
        self.update_ui()

    def pause(self, *_):
        if self.state == 'playing':
            self.state = 'paused'
        elif self.state == 'paused':
            self.state = 'playing'
        self.update_ui()

    def turn(self, direction):
        if self.state != 'playing':
            return
        if direction != (-self.direction[0], -self.direction[1]):
            self.next_direction = direction

    def key_down(self, window, key, scancode, codepoint, modifiers):
        mapping = {273:(0,1),274:(0,-1),276:(-1,0),275:(1,0),119:(0,1),115:(0,-1),97:(-1,0),100:(1,0)}
        if key in mapping:
            self.turn(mapping[key])
        elif key == 32:
            self.pause()
        elif key == 13:
            self.start()
        return True

    def tick(self, dt):
        if self.state != 'playing':
            return
        self.elapsed += dt
        speed = min(16, 7 + self.score // 40)
        if self.elapsed < 1 / speed:
            return
        self.elapsed = 0
        self.direction = self.next_direction
        x, y = self.snake[0]
        dx, dy = self.direction
        head = (x+dx,y+dy)
        eating = head == self.food
        body = self.snake if eating else self.snake[:-1]
        if not (0 <= head[0] < COLS and 0 <= head[1] < ROWS) or head in body:
            self.state = 'over'
            self.update_ui()
            return
        self.snake.insert(0, head)
        if eating:
            self.score += 10
            self.food = self.new_food()
            if self.food is None:
                self.state = 'won'
        else:
            self.snake.pop()
        self.update_ui()
        self.draw()

    def update_ui(self):
        self.score_label.text = f'PONTOS: {self.score}'
        self.hint.text = {'ready':'TOQUE EM INICIAR', 'playing':'', 'paused':'PAUSADO', 'over':'FIM DE JOGO! TOQUE EM REINICIAR', 'won':'VOCE VENCEU!'}.get(self.state,'')
        self.start_button.text = 'REINICIAR' if self.state in ('over','won','paused','playing') else 'INICIAR'
        self.pause_button.text = 'CONTINUAR' if self.state == 'paused' else 'PAUSAR'

    def layout_ui(self, *_):
        w,h = self.size
        pad = dp(12)
        controls_height = min(dp(205), h * .29)
        header_height = dp(68)
        avail_h = max(dp(120), h - controls_height - header_height - 3*pad)
        cell = min((w-2*pad)/COLS, avail_h/ROWS)
        self.cell = cell
        self.board_w, self.board_h = cell*COLS, cell*ROWS
        self.board_x = self.x + (w-self.board_w)/2
        self.board_y = self.y + controls_height + pad
        self.score_label.size = (w-2*pad,dp(32))
        self.score_label.pos = (self.x+pad, self.board_y+self.board_h+dp(25))
        self.hint.size = (w-2*pad,dp(26))
        self.hint.pos = (self.x+pad, self.board_y+self.board_h)
        bsize = min(dp(57), controls_height*.30)
        cx = self.center_x
        cy = self.y + controls_height*.52
        positions = {'▲':(cx-bsize/2,cy+bsize*.72), '▼':(cx-bsize/2,cy-bsize*.72), '◀':(cx-bsize*1.65,cy), '▶':(cx+bsize*.65,cy)}
        for label, button in self.buttons.items():
            button.size = (bsize,bsize)
            button.pos = positions[label]
        bw = min(dp(112), w*.28)
        self.start_button.size = (bw,dp(43))
        self.start_button.pos = (self.x+pad,self.y+dp(9))
        self.pause_button.size = (bw,dp(43))
        self.pause_button.pos = (self.right-pad-bw,self.y+dp(9))
        self.draw()

    def draw(self):
        self.canvas.before.clear()
        if not hasattr(self,'cell'):
            return
        with self.canvas.before:
            Color(*BG)
            Rectangle(pos=self.pos,size=self.size)
            Color(0.58,0.68,0.40,1)
            Rectangle(pos=(self.board_x,self.board_y),size=(self.board_w,self.board_h))
            Color(*DARK)
            Line(rectangle=(self.board_x,self.board_y,self.board_w,self.board_h),width=dp(2))
            c=self.cell
            for x,y in self.snake:
                Color(*DARK if (x,y)==self.snake[0] else MID)
                RoundedRectangle(pos=(self.board_x+x*c+c*.08,self.board_y+y*c+c*.08),size=(c*.84,c*.84),radius=[c*.16])
            if self.food is not None:
                x,y=self.food
                Color(*DARK)
                RoundedRectangle(pos=(self.board_x+x*c+c*.20,self.board_y+y*c+c*.20),size=(c*.60,c*.60),radius=[c*.30])

class SnakeApp(App):
    def build(self):
        self.title='Snake Nokia Mobile'
        return SnakeGame()

if __name__ == '__main__':
    SnakeApp().run()
