#!/usr/bin/python3
import RPi.GPIO as GPIO #Sisend/valjund viikude paketi lisamine
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.template
import json
import atexit
import os

motor = None

class Motor():

    left = None
    right = None
    running = False

    def __init__(self, left, right):
        self.pwm1bal = 7.0 #esimese mootori nullpunkt, muuta vastavalt oma mootori andmetele
        self.pwm2bal = 7.0 #teise mootori nullpunkt, muuta vastavalt oma mootori andmetele

        GPIO.setwarnings(False) #Hoiatuste valjalulitamine
        GPIO.setmode(GPIO.BOARD) #Viikude nummerduse valimine jarjekorra alusel
        GPIO.setup(left, GPIO.OUT) #Viikude 11 ja 12 valjundiks seadmine
        GPIO.setup(right, GPIO.OUT)
        self.left = GPIO.PWM(left, 50)
        self.right = GPIO.PWM(right, 50)

    def Drive(self, left, right):
        if not self.running:
            return

        try:
            pwm1.ChangeDutyCycle(pwm1bal+x/8+y/8) #Parempoolne mootor kiiruse seadistamine vastavalt nutiseadme x ja y vaartustele
            pwm2.ChangeDutyCycle(pwm2bal-x/8+y/8) #Vasakpoolne mootor kiiruse seadistamine vastavalt nutiseadme x ja y vaartustele
        except RuntimeError as e:
            print(e)
            self.Clean()


    def Reset(self):
        try:
            pwm1.ChangeDutyCycle(pwm1bal) #Parempoolne mootor kiiruse seadistamine vastavalt nutiseadme x ja y vaartustele
            pwm2.ChangeDutyCycle(pwm2bal) #Vasakpoolne mootor kiiruse seadistamine vastavalt nutiseadme x ja y vaartustele
            print("Motor outputs reset")
        except RuntimeError as e:
            print(e)
            self.Clean()
    
    def Clean(self):
        #SPWM.cleanup()

        print("Motor outputs cleaned")

    def TurnOn(self):
        try:
            pwm1.ChangeDutyCycle(pwm1bal) #Parempoolne mootor kiiruse seadistamine vastavalt nutiseadme x ja y vaartustele
            pwm2.ChangeDutyCycle(pwm2bal) #Vasakpoolne mootor kiiruse seadistamine vastavalt nutiseadme x ja y vaartustele
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

motor = Motor(11, 12)

application = tornado.web.Application([
    (r'/ws', WSHandler),
    (r'/', WebHandler),
    (r'/(.*)', tornado.web.StaticFileHandler, {'path': os.path.dirname(__file__)})
])

application.listen(8080)
tornado.ioloop.IOLoop.instance().start()
