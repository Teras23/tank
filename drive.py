#!/usr/bin/python3
import CHIP_IO.SOFTPWM as SPWM
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.template
import json
import atexit
import os

motor = None

class Motor():

    left_forward = None
    right_forward = None
    left_backward = None
    right_backward = None
    running = False

    def __init__(self, left_forward, right_forward, left_backward, right_backward):
        self.left_forward = left_forward
        self.right_forward = right_forward
        self.left_backward = left_backward
        self.right_backward = right_backward

    def Drive(self, left, right):
        if not self.running:
            return
        leftf = 0
        leftb = 0
        rightf = 0
        rightb = 0

        if left >= 0:
            leftf = left
        else:
            leftb = abs(left)

        if right >= 0:
            rightf = right
        else:
            rightb = abs(right)

        try:
            SPWM.set_duty_cycle(self.left_forward, leftf * 100)
            SPWM.set_duty_cycle(self.right_forward, rightf * 100)
            SPWM.set_duty_cycle(self.left_backward, leftb * 100)
            SPWM.set_duty_cycle(self.right_backward, rightb * 100)
        except RuntimeError as e:
            print(e)
            self.Clean()


    def Reset(self):
        try:
            SPWM.set_duty_cycle(self.left_forward, 0)
            SPWM.set_duty_cycle(self.right_forward, 0)
            SPWM.set_duty_cycle(self.left_backward, 0)
            SPWM.set_duty_cycle(self.right_backward, 0)
            print("Motor outputs reset")
        except RuntimeError as e:
            print(e)
            self.Clean()
    
    def Clean(self):
        SPWM.cleanup()
        print("Motor outputs cleaned")

    def TurnOn(self):
        try:
            SPWM.start(self.left_forward, 0)
            SPWM.start(self.right_forward, 0)
            SPWM.start(self.left_backward, 0)
            SPWM.start(self.right_backward, 0)
            self.running = True
            print("Motor turned on")
        except RuntimeError as e:
            print(e)
            self.Clean()

    def TurnOff(self):
        self.running = False
        self.Clean()
        print("Motor turned off")

class WebHandler(tornado.web.RequestHandler):
    def get(self):
        loader = tornado.template.Loader(".")
        self.render("index.html")

class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("Connection made")
        if motor.running:
            self.write_message("on")
        else:
            self.write_message("off")
    
    def on_message(self, message):
        jsonmsg = json.loads(message)
        if jsonmsg["moveData"]:
            leftspeed = jsonmsg["left"]
            rightspeed = jsonmsg["right"]
            
            if motor.running:
                motor.Drive(leftspeed, rightspeed)
                self.write_message("on")
        else:
            if not jsonmsg["motorOn"]:
                motor.TurnOff()
                self.write_message("off")
            else:
                motor.TurnOn()
                self.write_message("on")
    
    def on_close(self):
        print("Client lost")
        motor.TurnOff()
        pass

def exit():
    if motor != None:
        motor.Reset()
        motor.Clean()
    print("Exiting")

atexit.register(exit)

motor = Motor("XIO-P1", "XIO-P2", "XIO-P0", "XIO-P3")

application = tornado.web.Application([
    (r'/ws', WSHandler),
    (r'/', WebHandler),
    (r'/(.*)', tornado.web.StaticFileHandler, {'path': os.path.dirname(__file__)})
])

application.listen(8080)
tornado.ioloop.IOLoop.instance().start()