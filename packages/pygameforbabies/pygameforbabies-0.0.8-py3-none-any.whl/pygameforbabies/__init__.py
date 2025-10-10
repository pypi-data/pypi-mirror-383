import pygame,pymunk,pymunk.pygame_util
import pygame.camera
import math
try: # stiching
    from . import window,connect,keys,log,mouses,clipboard,d3
except:
    import window,connect,keys,log,mouses,clipboard,d3
def _rotate(image, topleft, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)
    return (rotated_image, new_rect)
log.info(f"Backends: {pygame.camera.get_backends()}")
pygame.init()
pygame.camera.init()
print("PYGAME_INIT")
physics_size = [1000,1000]
space = pymunk.space.Space()
gravity = (0,900)
space.gravity = gravity
_quit = True
drawqueue = []
updatequeue = []
running = True
scene = "init"
camerapos = [0,0]
camerazoom = 1.0
screen = None
camallowed = True
cams = pygame.camera.list_cameras()
physics = True
drawphysics = True
log.info(f"Cameras: {cams}")
def additer(iter1, iter2):
    return [iter1[0] + iter2[0], iter1[1] + iter2[1]]
def subiter(iter1, iter2):
    return [iter1[0] - iter2[0], iter1[1] - iter2[1]]
def multiter(iter1, iter2):
    return [iter1[0] * iter2[0], iter1[1] * iter2[1]]
def diviter(iter1, iter2):
    return [iter1[0] / iter2[0], iter1[1] / iter2[1]]
def hidemouse():
    pygame.mouse.set_visible(False)
def showmouse():
    pygame.mouse.set_visible(True)
def setmouse(mouse, system = False):
    if not system:
        pygame.mouse.set_cursor(mouse)
    else:
        pygame.mouse.set_system_cursor(mouse)
mouselocked = False
if not cams:
    log.error("Attach a camera to your device")
    camallowed = False
webcamsize = (640,480)
webcam = pygame.camera.Camera(cams[0])
def takepicturetofile(path="photo.jpg"):
    if camallowed:
        webcam.start()
        pygame.time.wait(1000)  # 1 second delay
        pygame.image.save(webcam.get_image(), path)
        webcam.stop()
def getmousepos():
    return (pygame.mouse.get_pos()[0] + camerapos[0], pygame.mouse.get_pos()[1] + camerapos[1])
def changemusic(path):
    pygame.mixer.music.load(path)
    pygame.mixer.music.play(-1)
def stopmusic():
    pygame.mixer.music.stop()
def screenshot(path="screenshot.png"):
    pygame.image.save(screen,path) # type: ignore
def quit_app():
    exit(0)
def _loadimage(path):
    try:
        return pygame.image.load(path)
    except Exception as e:
        log.error(f"Could not load {path}: {e}")
        return None

# im lazy
class Sound(pygame.mixer.Sound):
    pass

# sprite
class Sprite:
    def __init__(self,imgpath,pos=[0,0],scale = [64,64], camaffect=True, rotation = 0,removecolor=None, scene="init"):
        self.image = _loadimage(imgpath)
        self.children = []
        self.pos = pos
        self.scale = scale
        self.rotation = rotation
        self.camaffect = camaffect
        self.update = connect._defaultfunc
        self.visible = True if self.image else False
        self.removecolor = removecolor
        self.scene = scene
    def add(self):
        drawqueue.append(self)
    def changeimg(self,path):
        self.image = _loadimage(path)
        self.visible = True if self.image else False
    def move(self,dx,dy):
        self.pos[0] += dx
        self.pos[1] += dy
    def iscolliding(self,other):
        if self.visible:
            meow1 = pygame.transform.scale(self.image, self.scale).get_rect() # type: ignore
            meow1.topleft = self.pos
            meow2 = pygame.transform.scale(other.image, other.scale).get_rect()
            meow2.topleft = other.pos
            return meow1.colliderect(meow2)
    def rotate(self, angle):
        self.rotation += angle
    def _draw(self, screen:pygame.Surface):
        if scene == self.scene:
            self.visible = True
        else:
            self.visible = False
        
        if self.visible:
            ss = _rotate(
                    pygame.transform.scale(
                        self.image,  # type: ignore
                        (abs(self.scale[0] * camerazoom), abs(self.scale[1] * camerazoom))
                    ),
                    self.pos,
                    self.rotation
                )
            s = ss[0]
            r = ss[1]
            if self.removecolor:
                s.set_colorkey(self.removecolor)
            screen.blit(
                s,
                (
                    (r.topleft[0] - camerapos[0]) * camerazoom,
                    (r.topleft[1] - camerapos[1]) * camerazoom
                )
            )
    def _drawab(self, screen:pygame.Surface):
        if scene == self.scene:
            self.visible = True
        else:
            self.visible = False
        if self.visible:
            ss = _rotate(
                    pygame.transform.scale(
                        self.image,  # type: ignore
                        (abs(self.scale[0] * camerazoom), abs(self.scale[1] * camerazoom))
                    ),
                    self.pos,
                    self.rotation
                )
            s = ss[0]
            r = ss[1]
            if self.removecolor:
                s.set_colorkey(self.removecolor)
            screen.blit(
                s,
                #(
                #    (self.pos[0] - camerapos[0]) * camerazoom,
                #    (self.pos[1] - camerapos[1]) * camerazoom
                #)
                r
            )
class Line:
    def __init__(self, p1=(0,0), p2=(0,20), color="red", camaffect=True, width=4,visible=True, scene="init"):
        self.p1 = p1
        self.p2 = p2
        self.color = color
        self.camaffect = camaffect
        self.width = width
        self.visible = visible
        self.scene = scene
    def add(self):
        drawqueue.append(self)
    def _draw(self,screen):
        if scene == self.scene:
            self.visible = True
        else:
            self.visible = False
        if self.visible:
            pygame.draw.line(
                screen, 
                self.color, 
                (
                    (self.p1[0] - camerapos[0]) * camerazoom, 
                    (self.p1[1] - camerapos[1]) * camerazoom
                ), 
                (
                    (self.p2[0] - camerapos[0]) * camerazoom, 
                    (self.p2[1] - camerapos[1]) * camerazoom
                ), 
                self.width
            )
    def _drawab(self,screen):
        if scene == self.scene:
            self.visible = True
        else:
            self.visible = False
        if self.visible:
            pygame.draw.line(
                screen, 
                self.color, 
                self.p1, 
                self.p2, 
                self.width
            )
class Rectangle:
    def __init__(self, pos=[0,0],size=[20,20],color='red',camaffect=True, visible=True, scene="init"):
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        self.color = color
        self.camaffect=camaffect
        self.visible = visible
        self.scene = scene
        self.modrect = self.rect
    def add(self):
        drawqueue.append(self)
    def _draw(self, screen):
        if scene == self.scene:
            self.visible = True
        else:
            self.visible = False
        # Create a new pygame.Rect object with the adjusted position
        if self.visible:
            self.modrect = pygame.Rect(
                (self.rect.x - camerapos[0]) * camerazoom,
                (self.rect.y - camerapos[1]) * camerazoom,
                abs(self.rect.width * camerazoom),
                abs(self.rect.height * camerazoom)
            )
            pygame.draw.rect(
                screen, 
                self.color, 
                self.modrect
            )
    def _drawab(self,screen):
        if scene == self.scene:
            self.visible = True
        else:
            self.visible = False
        if self.visible:
            self.modrect = self.rect
            pygame.draw.rect(screen, self.color, self.modrect)

# text
class Text:
    def __init__(self, text="MEoooow",pos=[0,0], size=20, color="red",camaffect=True,visible=True, scene="init"):
        self.pos = pos
        self.size = size
        self.color = color
        self.font = pygame.font.Font(None, self.size)
        self.text = text
        self.camaffect = camaffect
        self.visible = visible
        self.scene = scene
    def add(self):
        drawqueue.append(self)
    def _draw(self,screen):
        if scene == self.scene:
            self.visible = True
        else:
            self.visible = False
        if self.visible:
            meow = self.font.render(self.text,False,self.color)
            screen.blit(
                pygame.transform.scale(
                    meow,  # type: ignore
                    (abs(meow.get_width() * camerazoom), abs(meow.get_height() * camerazoom))
                ), 
                (
                    self.pos[0] - camerapos[0], 
                    self.pos[1] - camerapos[1]
                )
            )
    def _drawab(self,screen):
        if scene == self.scene:
            self.visible = True
        else:
            self.visible = False
        if self.visible:
            meow = self.font.render(self.text,False,self.color)
            screen.blit(meow, self.pos)

# circle
class Circle:
    def __init__(self,pos=[0,0], color="red", radius=10, camaffect=True,visible=True, scene="init") -> None:
        #pygame.draw.circle(screen,"blue",(0,0),10)
        self.pos = pos
        self.color = color
        self.radius = radius
        self.camaffect = camaffect
        self.visible = visible
        self.scene = scene
    def add(self):
        drawqueue.append(self)
    def _draw(self,screen):
        if scene == self.scene:
            self.visible = True
        else:
            self.visible = False
        if self.visible:
            pygame.draw.circle(
                screen, 
                self.color, 
                (
                    (self.pos[0] - camerapos[0]) * camerazoom, 
                    (self.pos[1] - camerapos[1]) * camerazoom
                ), 
                abs(self.radius * camerazoom)
            )
    def _drawab(self,screen):
        if scene == self.scene:
            self.visible = True
        else:
            self.visible = False
        if self.visible:
            pygame.draw.circle(screen,self.color,self.pos,self.radius)
class Button:
    def __init__(self, size=50, text="Mrow?", color="blue", hovercolor="red", pos=[0,0], textcolor="white", camaffect=False, onclick=lambda: print("clicked"), scene="init") -> None:
        self.text = Text(text,pos,size,textcolor,camaffect,True)
        m = self.text.font.render(text,True, "white")
        self.hovercolor = hovercolor
        self.color = color
        self.rect = Rectangle([pos[0] - 10, pos[1] - 10], [m.get_width() + 10, m.get_height() + 10], color, camaffect, True)
        self.onclick = onclick
        self.scene = scene
    def show(self):
        self.rect.visible = True
        self.text.visible = True
    def hide(self):
        self.rect.visible = False
        self.text.visible = False
    def add(self):
        self.rect.add()
        self.text.add()
        updatequeue.append(self)
    def _update(self,event):
        if scene == self.scene:
            self.show()
        else:
            self.hide()
        if self.rect.visible:
            if self.rect.modrect.collidepoint(pygame.mouse.get_pos()):
                self.rect.color = self.hovercolor
                setmouse(mouses.HANDPOINT)
            else:
                self.rect.color = self.color
                setmouse(mouses.NORMAL)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.modrect.collidepoint(event.pos):
                setmouse(mouses.NORMAL)
                self.onclick()
    def changetext(self,text):
        self.text.text = text
        m = self.text.font.render(text,True, "white")
        self.rect.rect.size = (m.get_width() + 10, m.get_height() + 10)
class Slider:
    def __init__(self, pos=[0,0], size=[200,20], color="blue", handlecolor="red", minvalue=0, maxvalue=100, startvalue=50, camaffect=False, onchange=lambda val: print(val)) -> None:
        self.rect = Rectangle(pos,size,color,camaffect,True)
        self.handlepos = [pos[0] + (startvalue - minvalue) / (maxvalue - minvalue) * size[0] - 10, pos[1] - 5]
        self.handle = Rectangle(self.handlepos,[20,size[1]+10],handlecolor,camaffect,True)
        self.minvalue = minvalue
        self.maxvalue = maxvalue
        self.value = startvalue
        self.dragging = False
        self.onchange = onchange
    def add(self):
        self.rect.add()
        self.handle.add()
        updatequeue.append(self)
    def _update(self,event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle.rect.collidepoint(event.pos):
                self.dragging = True
        if event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        if event.type == pygame.MOUSEMOTION:
            if self.dragging:
                new_x = event.pos[0]
                new_x = max(self.rect.rect.x, min(new_x, self.rect.rect.x + self.rect.rect.width))
                self.handle.rect.x = new_x - 10
                relative_x = self.handle.rect.x + 10 - self.rect.rect.x
                self.value = self.minvalue + (relative_x / self.rect.rect.width) * (self.maxvalue - self.minvalue)
                self.onchange(self.value)
class TextInput:
    def __init__(self, pos=[0,0], size=20, color="black", bgcolor="white", camaffect=False, scene="init") -> None:
        self.text = ""
        self.pos = pos
        self.size = size
        self.color = color
        self.bgcolor = bgcolor
        self.font = pygame.font.Font(None, self.size)
        self.camaffect = camaffect
        self.scene = scene
        self.active = False
    def add(self):
        drawqueue.append(self)
        updatequeue.append(self)
    def _draw(self,screen):
        if scene == self.scene:
            self.visible = True
        else:
            self.visible = False
        if self.visible:
            meow = self.font.render(self.text,False,self.color)
            bgrect = meow.get_rect(topleft=(self.pos[0] - camerapos[0], self.pos[1] - camerapos[1]))
            bgrect.inflate_ip(10, 10)  # Add some padding
            pygame.draw.rect(screen, self.bgcolor, bgrect)
            screen.blit(
                pygame.transform.scale(
                    meow,  # type: ignore
                    (abs(meow.get_width() * camerazoom), abs(meow.get_height() * camerazoom))
                ), 
                (
                    (self.pos[0] - camerapos[0]) * camerazoom,
                    (self.pos[1] - camerapos[1]) * camerazoom
                )
            )
    def _drawab(self,screen):
        if scene == self.scene:
            self.visible = True
        else:
            self.visible = False
        if self.visible:
            meow = self.font.render(self.text,False,self.color)
            bgrect = meow.get_rect(topleft=self.pos)
            bgrect.inflate_ip(10, 10)  # Add some padding
            pygame.draw.rect(screen, self.bgcolor, bgrect)
            screen.blit(meow, self.pos)
    def _update(self,event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if pygame.Rect(self.pos[0], self.pos[1], 200, self.size + 10).collidepoint(event.pos):
                    self.active = True
                else:
                    self.active = False
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
class StaticBody:
    def __init__(self, pos=[0,0], size=[50,50], angle=0, bodytype=pymunk.Body.STATIC, color="red", scene="init",mass=1) -> None:
        self.body = pymunk.Body(body_type=bodytype, mass=mass, moment=pymunk.moment_for_box(mass, size))
        self.body.position = pos
        self.body.angle = math.radians(angle)
        self.shape = pymunk.Poly.create_box(self.body, size)
        self.shape.color = pygame.Color(color)
        self.shape.elasticity = 0.5
        self.shape.friction = 0.5
        self.scene = scene
    def add(self):
        space.add(self.body, self.shape)
    def remove(self):
        space.remove(self.body, self.shape)
    def set_position(self, pos):
        self.body.position = pos
    def set_angle(self, angle):
        self.body.angle = math.radians(angle)
    def get_position(self):
        return pymunk.pygame_util.to_pygame(self.body.position, screen) # type: ignore
    def get_angle(self):
        return math.degrees(self.body.angle)
    def apply_force(self, force, point=(0,0)):
        self.body.apply_force_at_local_point(force, point)
    def add_joint(self, other, joint_type="pivot", anchor_a=(0,0), anchor_b=(0,0)):
        "add a joint between this and the other body, the joint types are: pivot, pin, slide, groove"
        if joint_type == "pivot":
            joint = pymunk.PivotJoint(self.body, other.body, anchor_a, anchor_b)
        elif joint_type == "pin":
            joint = pymunk.PinJoint(self.body, other.body, anchor_a, anchor_b)
        elif joint_type == "slide":
            joint = pymunk.SlideJoint(self.body, other.body, anchor_a, anchor_b, 0, 100)
        elif joint_type == "groove":
            joint = pymunk.GrooveJoint(self.body, other.body, anchor_a, anchor_b, (0,0))
        else:
            raise ValueError("Invalid joint type")
        space.add(joint)
        return joint
class StaticCircle(StaticBody):
    def __init__(self, pos=[0,0], radius=50, angle=0, bodytype=pymunk.Body.STATIC, color="red", scene="init",mass=1) -> None:
        self.body = pymunk.Body(body_type=bodytype, mass=mass, moment=pymunk.moment_for_circle(mass, 0, radius))
        self.body.position = pos
        self.body.angle = math.radians(angle)
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.color = pygame.Color(color)
        self.shape.elasticity = 0.5
        self.shape.friction = 0.5
        self.scene = scene
class RigidBody(StaticBody):
    def __init__(self, pos=[0,0], size=[50,50], angle=0, bodytype=pymunk.Body.DYNAMIC, color="blue", scene="init", mass=1) -> None:
        super().__init__(pos, size, angle, bodytype, color, scene, mass)
class RigidCircle(StaticCircle):
    def __init__(self, pos=[0, 0], radius=50, angle=0, bodytype=pymunk.Body.DYNAMIC, color="blue", scene="init", mass=1) -> None:
        super().__init__(pos, radius, angle, bodytype, color, scene, mass)
class Character(RigidBody):
    def __init__(self, pos=[0, 0], size=[50, 80], angle=0, bodytype=pymunk.Body.DYNAMIC, color="blue", scene="init", mass=1) -> None:
        super().__init__(pos, size, angle, bodytype, color, scene, mass)
    
    def move_left(self, impulse=50):
        self.body.angle = 0
        self.body.apply_impulse_at_local_point((-impulse, 0))

    def move_right(self, impulse=50):
        self.body.angle = 0
        self.body.apply_impulse_at_local_point((impulse, 0))

    def jump(self, force=400):
        self.body.angle = 0
        self.body.apply_impulse_at_local_point((0, -force), (0, 0))




#   IMPORTANT
def mainloop():
    global running,screen
    flags = 0
    if window.resizeable:
        flags |= pygame.RESIZABLE
    if window.fullscreen:
        flags |= pygame.FULLSCREEN
    if window.gl:
        flags |= pygame.OPENGL

    screen = pygame.display.set_mode(window.size, flags)
    if window.gl:
        d3._init()
    clipboard._init()
    pygame.display.set_caption(window.title)
    pygame.display.set_icon(window.icon)
    mousedown = False
    clock = pygame.time.Clock()
    _pymunklayer = pygame.Surface(physics_size)
    drawoptions = pymunk.pygame_util.DrawOptions(_pymunklayer)
    while running:
        if mouselocked:
            pygame.mouse.set_pos((window.size[0] / 2, window.size[1] / 2))
        connect.onupdate()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                connect.onkeypress(event.key)
            if event.type == pygame.KEYUP:
                connect.onkeyup(event.key)
            if event.type == pygame.MOUSEBUTTONDOWN:
                connect.onmouseclicked((pygame.mouse.get_pos()[0] + camerapos[0], pygame.mouse.get_pos()[1] + camerapos[1]))
                mousedown = True
            if event.type == pygame.MOUSEBUTTONUP:
                mousedown = False
            if event.type == pygame.MOUSEMOTION:
                connect.onmousemove((pygame.mouse.get_pos()[0] + camerapos[0], pygame.mouse.get_pos()[1] + camerapos[1]))
            if event.type == pygame.MOUSEWHEEL:
                connect.onmousescroll((event.x,event.y))
            if event.type == pygame.QUIT:
                if _quit:
                    running = False
                    connect.onquit()
            for item in updatequeue:
                item._update(event)
            connect.oneventupdate(event)
        if mousedown:
            connect.onmousedown((pygame.mouse.get_pos()[0] + camerapos[0], pygame.mouse.get_pos()[1] + camerapos[1]))
        kes = pygame.key.get_pressed()
        connect.onkeydown(kes)
        screen.fill(window.screencolor)
        if window.gl:
            d3._clear()
        else:
            screen.fill(window.screencolor)
        _pymunklayer.fill(window.screencolor)
        if physics:
            space.step(1/window.fps)
        if drawphysics:
            space.debug_draw(drawoptions)
        _pos = subiter([0,0], camerapos)
        screen.blit(_pymunklayer, _pos)
        if window.gl:
            for item in d3.d3queue:
                item._draw()
                item._update()
        for item in drawqueue:
            if item.camaffect:
                item._draw(screen)
            else:
                item._drawab(screen)
        pygame.display.flip()
        clock.tick(window.fps)
def test():
    mainloop()
if __name__ == "__main__":
    test()