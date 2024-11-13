# module to control mouse using directions and distances
from typing import Tuple
from talon import Context, Module, canvas, cron, ctrl, cron, screen, ui, actions
import math, time, random
mode_label = {0:'none',1:'tiny',2:'light',3:'medium',4:'heavy'}
compass_display_modes = {'heavy':4,'medium':3,'light':2,'tiny':1,'none':0}
resting_display_mode = 0
update_interval = 30
fade_time = 5000 # ten seconds

def f_distance(from_pos,to_pos):
    return (((to_pos[0]-from_pos[0]) ** 2) + ((to_pos[1] - from_pos[1]) ** 2))**0.5

class compass:
    def __init__(self, width: float, height: float):
        self.enabled = False
        self.canvas = None
        self.job = None
        self.width = width
        self.height = height
        self.bearing = 0
        self.distance = 0
        self.max_dist = (self.width ** 2 + self.height ** 2) ** 0.5
        self.active_display_mode = 3
        self.display_mode = self.active_display_mode
        self.elapsed_ms = 0
        self.target_ms = 1500
        self.max_ms = 1500
        self.min_ms = 100
    def enable(self, bearing = 0):
        self.bearing = bearing
        if self.enabled:
            return
        self.enabled = True
        screen = ui.main_screen()
        self.width, self.height = screen.width, screen.height
        self.canvas = canvas.Canvas.from_screen(screen)#  canvas.Canvas(0, 0, self.width, self.height)
        self.canvas.register('draw', self.draw_canvas) 
        self.canvas.freeze() # uncomment this line for debugging
        self.job = cron.interval('{}ms'.format(update_interval), self.check_for_updates)
    def disable(self):
        if not self.enabled:
            return
        cron.cancel(self.job)
        self.canvas.close()
        self.canvas = None
        actions.user.zoom_close()
        actions.user.grid_close()
        actions.mode.enable("command")
        actions.mode.disable("user.compass")
        self.enabled = False
    def pot_of_gold(self,x,y,distance,bearing):
        # calculate next position
        theta = math.radians(bearing)
        x2,y2 = x + distance * math.sin(theta), y - distance * math.cos(theta)
        # make sure it is not off the screen
        # note that the most important equation is :
        # tan(theta) = -dx/dy
        if x2 < 0:
            x2 = 0
            if bearing == 90 or bearing == 270:
                y2 = y
            else:
                y2 = y - (x2 - x) / math.tan(theta)
        if x2 > compass_object.width - 1:
            x2 = compass_object.width - 1
            if bearing == 90 or bearing == 270:
                y2 = y
            else:
                y2 = y - (x2 - x) / math.tan(theta)
        if y2 < 0:
            y2 = 0
            x2 = x - (y2 - y) * math.tan(theta)
        if y2 > compass_object.height - 1:
            y2 = compass_object.height - 1
            x2 = x - (y2 - y) * math.tan(theta)            
        return x2,y2
    def distance_to_edge(self,x,y,bearing):
        # calculate distance to edge in pixels
        theta = math.radians(bearing)
        cos_theta = math.cos(theta)
        sin_theta = math.sin(theta)
        h = compass_object.height
        w = compass_object.width
        # get distances in vertical and horizontal directions
        vrt_dist = y/cos_theta if cos_theta>0 else (y-h)/cos_theta if cos_theta<0 else 9999999
        hz_dist = -x/sin_theta if sin_theta<0 else (w-x)/sin_theta if sin_theta>0 else 9999999
        # distance is minimum of vertical and horizontal distances
        return min(vrt_dist,hz_dist)
    def draw_canvas(self, canvas):
        paint = canvas.paint
        paint.antialias = True
        paint.color = 'fff'
        paint.font.size = 36
        rect = canvas.rect

        def line_aliased(x,y,distance,bearing, color_main = 'ffffff99', color_alias = '00000099'):
            for off, color in ((1, color_alias),(-1, color_alias),(0.5, color_main),(-0.5, color_main),(0, color_main)):
                paint.color = color
                start_x,start_y = self.pot_of_gold(x,y,off,bearing + 90)
                finish_x,finish_y = self.pot_of_gold(start_x,start_y,distance,bearing)
                canvas.draw_line(start_x, start_y, finish_x, finish_y)

        def line_thick_aliased(x,y,distance,bearing, color_main = 'ffffff99', color_alias = '00000099'):
            offsets = [2,-2,1.5,-1.5,1,-1,0.5,-0.5,0]
            colors = [color_alias] * 4 + [color_main] * 5
            for off, color in zip(offsets,colors):
                paint.color = color
                start_x,start_y = self.pot_of_gold(x,y,off,bearing + 90)
                finish_x,finish_y = self.pot_of_gold(start_x,start_y,distance,bearing)
                canvas.draw_line(start_x, start_y, finish_x, finish_y)

        def text_aliased(label,x,y,font_size):
                paint.font.size = font_size
                limit = 2
                for dx in range(-limit,limit+1):
                    for dy in range(-limit,limit+1):
                        # spine-black and more transparent towards edges
                        dist = ((dx ** 2) + (dy ** 2)) ** 0.5
                        paint.color = f'000000'
                        canvas.draw_text(label,x + dx,y + dy)
                # outline-white and less transparent
                paint.color = 'ffffffee'
                canvas.draw_text(label,x,y)
                canvas.draw_text(label,x+1,y-1)

        def left_cardinal(b):
            b = b % 360
            r = 'W' if b<45 else 'N' if b<135 else 'E' if b<225 else 'S' if b<315 else 'W'
            return r

        def right_cardinal(b):
            b = b % 360
            r = 'E' if b<45 else 'S' if b<135 else 'W' if b<225 else 'N' if b<315 else 'E'
            return r

        # get spoke parameters
        distance = 5000
        crosshair_radius = 30
        
        long_crosshair_length = 12
        short_crosshair_length = 5

        inner_compass_radius = 250
        outer_compass_radius = 200
        short_compass_mark_length = 50
        long_compass_mark_length = 100
        label_offset = 25
        pos = ctrl.mouse_pos()
        cx = pos[0]
        cy = pos[1]
        max_dist = self.distance_to_edge(cx,cy,self.bearing)

        # DRAW GRID
        startBearing = max(0,self.bearing)
        if mode_label[self.display_mode] in ['heavy','medium','light','tiny']:
            # draw circular crosshairs around current mouse position
            for brg_adj in [0,90,180,270]:
                start_x,start_y = self.pot_of_gold(cx,cy,crosshair_radius-long_crosshair_length,startBearing + brg_adj)
                line_aliased(start_x, start_y, long_crosshair_length, startBearing + brg_adj, color_main = 'ff9999ff', color_alias = 'ffffff99')
            for brg_adj in range(0,360,10):
                if not brg_adj % 90 == 0:
                    start_x,start_y = self.pot_of_gold(cx,cy,crosshair_radius - short_crosshair_length,startBearing + brg_adj)
                    line_aliased(start_x, start_y, short_crosshair_length, startBearing + brg_adj, color_main = 'ff9999ff', color_alias = 'ffffff99')

        if mode_label[self.display_mode] in ['heavy','medium','light','tiny']: 
            # draw an extra little arrow for tiny display
            start_x,start_y = self.pot_of_gold(cx,cy,crosshair_radius,startBearing)
            line_aliased(start_x, start_y, crosshair_radius * 0.5, startBearing, color_main = 'ff9999ff', color_alias = 'ffffff99')
            start_x,start_y = self.pot_of_gold(cx,cy,crosshair_radius * 1.5, startBearing)
            line_aliased(start_x, start_y, crosshair_radius * 0.25, startBearing + 135, color_main = 'ff9999ff', color_alias = 'ffffff99')
            line_aliased(start_x, start_y, crosshair_radius * 0.25, startBearing - 135, color_main = 'ff9999ff', color_alias = 'ffffff99')
            
        
        # bearing not selected
        if self.bearing  == -1:
            if mode_label[self.display_mode] in ['heavy','medium','light']:
                # draw cardinal directions and diagonals
                for bearing in range(45,359,90):
                    start_x,start_y = self.pot_of_gold(cx,cy,crosshair_radius,bearing)
                    line_aliased(start_x, start_y, distance, bearing)
                for bearing in range(0,359,45):
                    if bearing % 90 == 0:
                        start_x,start_y = self.pot_of_gold(cx, cy, inner_compass_radius - long_compass_mark_length, bearing)
                        line_aliased(start_x, start_y, long_compass_mark_length, bearing)
            if mode_label[self.display_mode] in ['heavy','medium']:
                # draw minor spokes
                for bearing_x10 in range(0,3590,225):
                    bearing = bearing_x10/10
                    if bearing % 45 != 0:
                        start_x,start_y = self.pot_of_gold(cx, cy, inner_compass_radius - short_compass_mark_length, bearing)
                        line_aliased(start_x, start_y, short_compass_mark_length, bearing)
            if mode_label[self.display_mode] in ['heavy','medium','light']:
                # draw labels for cardinal directions
                paint.color = 'ffffffff'
                for bearing,label in zip([0,90,180,270],['North','East','South','West']):
                    start_x,start_y = self.pot_of_gold(cx,cy,inner_compass_radius + label_offset,bearing)
                    text_aliased(label,start_x,start_y,45)
            if mode_label[self.display_mode] in ['heavy','medium']:
                paint.color = 'DDDDDDDD'
                for bearing,label in zip([45,135,225,315],['NE', 'SE','SW','NW']):
                    start_x,start_y = self.pot_of_gold(cx,cy,inner_compass_radius + label_offset,bearing)
                    text_aliased(label,start_x,start_y,30)
            if mode_label[self.display_mode] in 'heavy':
                paint.color = 'BBBBBB99'
                for bearing,label in zip([22.5,67.5,112.5,157.5,202.5,247.5,292.5,337.5],['NNE', 'ENE','ESE','SSE','SSW','WSW','WNW','NNW']):
                    start_x,start_y = self.pot_of_gold(cx,cy,inner_compass_radius + label_offset,bearing)
                    text_aliased(label,start_x,start_y,18)
                    
        # bearing selected
        if self.bearing  != -1:            
            # draw distance hash lines
            spacings = []
            label_spacings = []
            if mode_label[self.display_mode] in ['heavy','medium','light']:
                spacings += [500,100]
                label_spacings += [500]
                if mode_label[self.display_mode] in ['heavy','medium']:
                    spacings += [50,10]
                    label_spacings += [100]
            
            spacing_sizes = {500:60,100:39,50:21,10:12}
            if mode_label[self.display_mode] == 'medium':
                spacing_sizes = {500:60,100:25,50:11,10:3}    
            if mode_label[self.display_mode] == 'light':
                spacing_sizes = {500:60,100:5,50:3,10:2}    
            for j in range(len(spacings)):
                spacing = spacings[j]
                size = spacing_sizes[spacing]
                for i in range(int(self.max_dist/spacing) + 1):
                    # make sure that we are not hitting a larger spacing
                    if (j == 0) or (((spacing * i) % spacings[j-1]) != 0):
                        for inout in [-1,1]:
                            d = self.distance + spacing * i * inout
                            if d > 0 and d < max_dist:
                                x,y = self.pot_of_gold(cx,cy,d,self.bearing)
                                sx,sy = self.pot_of_gold(x,y,size/2,self.bearing - 90)
                                if spacing == 10:
                                    line_aliased(sx,sy,size,self.bearing + 90)
                                elif spacing == 500:
                                    line_thick_aliased(sx,sy,size,self.bearing + 90,color_main = "ff999999")
                                else:
                                    line_thick_aliased(sx,sy,size,self.bearing + 90)
                                # draw crosshairs for display light mode
                                if mode_label[self.display_mode] == 'light':
                                    sx,sy = self.pot_of_gold(x,y,size/2,self.bearing - 180)
                                    if spacing == 500:
                                        line_aliased(sx,sy,size,self.bearing)
                                # draw labels for big lines
                                if spacing in label_spacings:
                                    s = 5 if 0 < self.bearing < 180 else size + 5
                                    sx,sy = self.pot_of_gold(sx,sy,s,self.bearing - 90)
                                    fs = 27 if spacing == 500 else 18
                                    text_aliased(str(spacing * i),sx,sy,fs)
            if mode_label[self.display_mode] in ['heavy']:
                # draw selected bearing line            
                start_x,start_y = self.pot_of_gold(cx,cy,10,self.bearing)
                line_thick_aliased(start_x, start_y, distance, self.bearing, color_main = 'ff9999ff', color_alias = 'ffffff99')
            
            # draw adjacent bearings thirty degrees on either side
            for left_right in [-1,1]:
                cardinal = left_cardinal(self.bearing) if left_right == -1 else right_cardinal(self.bearing)
                if mode_label[self.display_mode] in ['heavy','medium']:
                    # draw full spoke every ten degrees
                    for brg_adj in [10,20,30]:
                        b = self.bearing + brg_adj * left_right
                        start_distance = min(100,max_dist * 0.5)
                        start_x,start_y = self.pot_of_gold(cx,cy,start_distance,b)
                        if mode_label[self.display_mode] in ['heavy']:
                            line_aliased(start_x,start_y,distance,b)
                    # determine radii
                    hash_len = spacing_sizes[500]
                    radii = []
                    min_int_ratio = 10 # minimum interval ratio
                    if max_dist > min_int_ratio * hash_len:
                        radii = [0.6]
                    if mode_label[self.display_mode] == 'heavy':
                        if max_dist > 3 * min_int_ratio * hash_len:
                            radii = [0.2,0.5,0.8]
                        elif max_dist > 2 * min_int_ratio * hash_len:
                            radii = [0.35,0.75]
                    # draw dial marks at radii
                    for brg_adj in range(31):
                        spacing_size_id = 500 if brg_adj%10==0 else 100 if brg_adj%5==0 else 50
                        hash_len = spacing_sizes[spacing_size_id]/2
                        b = self.bearing + brg_adj * left_right
                        dial_radius = [int(max_dist * x) for x in radii]
                        for out_dist in dial_radius:
                            start_x,start_y = self.pot_of_gold(cx,cy,out_dist - hash_len/2,b)
                            line_aliased(start_x,start_y, hash_len,b)
                            # label spokes every ten degrees
                            if brg_adj % 10 == 0:
                                buffer = 10
                                text_x,text_y = self.pot_of_gold(start_x,start_y,buffer+hash_len,b)
                                label = "{}{}".format(str(abs(brg_adj)), cardinal)
                                text_aliased(label,text_x,text_y,18)
        if compass_object.canvas != None:
            compass_object.canvas.move(0,0) # this forces canvas redraw
    def check_for_updates(self):
        if self.display_mode == resting_display_mode:
            actions.user.compass_disable()
            return 
        do_redraw = True
        # increment time since last action
        self.elapsed_ms += update_interval
        # fade radial grid
        if self.elapsed_ms > fade_time:
            if self.display_mode > resting_display_mode:
                self.display_mode = self.display_mode - 1
                self.elapsed_ms = 0
           

compass_object = compass(5000, 5000)
# compass_object.enable()

mod = Module()
mod.list('compass_display_mode', desc = 'amount of information displayed in compass grid')
mod.mode("compass",desc = "Compass commands only")

@mod.capture(rule="((north | east | south | west | northeast | southeast | southwest | northwest | up | down | left | right) [(north | east | south | west | northeast | southeast | southwest | northwest)])")
def bearing(m) -> float:
    """determines bearing from spoken compass direction"""
    def bearing_average(b1,b2):
        difference = ((b2 - b1 + 180) % 360) - 180
        return b1 + difference/2
        
    bearing_lookup = {
        'northeast':45,'southeast':135,'southwest':225,'northwest':315,
        'north':0,'east':90,'south':180,'west':270,
        'up':0,'right':90,'down':180,'left':270
        }
    bearing = None
    for w in range(len(m)-1,-1,-1):
        if bearing == None:
            bearing = bearing_lookup[m[w]]
        else:
            bearing = bearing_average(bearing, bearing_lookup[m[w]])
    return bearing

          
@mod.action_class
class Actions:
    def compass_enable(display_mode: int = -1):
        """Enable relative mouse guide"""
        if display_mode == -1:
            display_mode = compass_object.active_display_mode
        compass_object.enable()
        compass_object.elapsed_ms = 0
        compass_object.display_mode = display_mode

    def compass_set_bearing(bearing: float):
        """enable relative mouse guide and point to given bearing direction"""
        compass_object.enable(bearing)
        compass_object.elapsed_ms = 0
        compass_object.display_mode = compass_object.active_display_mode
        
    def compass_disable():
        """Disable relative mouse guide"""
        compass_object.disable()

    def move_cardinal(move_degrees: float, target: float):
        """move the bearing direction a certain number of degrees towards a cardinal direction"""
        # determine difference between current bearing and target bearing
        delta = (((target - compass_object.bearing) + 180) % 360) - 180       
        # limit movement to ensure we don't go past the target direction
        if move_degrees > abs(delta):
            move_degrees = abs(delta)
        # adjust sign of movement if necessary
        if delta < 0:
            move_degrees = -move_degrees            
        # initialize compass compass
        compass_object.enable((compass_object.bearing + move_degrees) % 360)
        compass_object.elapsed_ms = 0
        compass_object.display_mode = compass_object.active_display_mode

    def fly_out(distance: int, max_ms: int = -1):
        """move out the specified number of pixels"""
        pos = ctrl.mouse_pos()
        cx,cy = pos[0],pos[1]
        trg = compass_object.pot_of_gold(cx, cy, distance, compass_object.bearing)
        print(f'trg: {trg}')
        actions.user.slow_mouse(round(trg[0]),round(trg[1]),max_ms)
        if max_ms > 0:
            compass_object.max_ms = max_ms
        compass_object.elapsed_ms = 0
        compass_object.display_mode = compass_object.active_display_mode

    def reverse():
        """reverse direction"""
        compass_object.bearing = (compass_object.bearing + 180) % 360        
        update_canvas()
        compass_object.elapsed_ms = 0
        compass_object.display_mode = compass_object.active_display_mode

    def fly_back(distance: int):
        """turn around and move back the specified number of pixels"""
        compass_object.bearing = (compass_object.bearing + 180) % 360
        actions.user.fly_out(distance)
        compass_object.bearing = (compass_object.bearing + 180) % 360

    def compass_jiggle(max_dist: int = 10):
        """move the mouse around a little"""
        pos = ctrl.mouse_pos()
        init_x,init_y = pos[0],pos[1]
        for n in range(10):
            d = max_dist*random.random()
            b = 360*random.random()
            trg = compass_object.pot_of_gold(init_x,init_y,d,b)
            actions.user.slow_mouse(round(trg[0]),round(trg[1]),50)
            actions.sleep("50ms")
        actions.user.slow_mouse(round(trg[0]),round(trg[1]),50)
        
    def center_compass():
        """move mouse to center of screen"""
        x,y = int(compass_object.width/2), int(compass_object.height/2)
        ctrl.mouse_move(x,y)
        compass_object.last_pos = x,y
        compass_object.cur_pos = x,y
        compass_object.target_pos = x,y
        compass_object.bearing = -1
        ctx.tags = ["user.compass_showing","user.compass_active"]

    def compass_set_display_mode(mode: str):
        """change how much information is displayed in the compass grid"""
        compass_object.active_display_mode = mode
        compass_object.display_mode = mode
    
    def start_extra_time():
        """Begins extra time where display is tiny, before compass exits 100%"""
        actions.mode.enable("command")
        compass_object.display_mode = 1
        compass_object.elapsed_ms = 0        
ctx = Context()
