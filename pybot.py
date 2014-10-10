import os
import numpy as np
import pylab as pb
from threading import Thread
from Queue import Queue


from Xlib.display import Display
from Xlib import X
from Xlib.ext import record
from Xlib.protocol import rq


#TODO: Fix output, write Ipython code to split in to wins, remove null frames

class Bot(object):
#TODO: decide frameskip
    def __init__(self, display_screen="true", skip_frames=0,
                 max_num_episodes=1, romfile="./src/pong.bin"):
        '''Start pipe and initialise agent'''

        self.display_screen = display_screen
        self.skip_frames = skip_frames
        self.max_num_episodes = max_num_episodes
        #: create FIFO pipes
        os.system("mkfifo ale_fifo_out")
        os.system("mkfifo ale_fifo_in")

        #: launch ALE with appropriate commands in the background
        command = './ale -max_num_episodes ' + str(self.max_num_episodes)\
            + ' -game_controller fifo_named -disable_colour_averaging true -run_length_encoding false -frame_skip '\
            + str(self.skip_frames)+' -display_screen ' +\
            self.display_screen + " " + romfile + " &"

        os.system(command)

        #: open communication with pipes
        self.fin = open('ale_fifo_out')
        self.fout = open('ale_fifo_in', 'w')

        input = self.fin.readline()[:-1]
        self.size = input.split("-")
        # saves the image sizes (160*210) for breakout

        # first thing we send to ALE is the output options
        #  we want to get only image data
        # and episode info(hence the zeros)
        self.fout.write("1,0,0,1\n")
        self.fout.flush()  # send the lines written to pipe

        #: initialize the variables that we will start receiving from ./ale
        self.next_image = []
        self.game_over = True
        self.current_reward = 0
        self.action=1
        self.logfile=open("logfile.txt","w")

    def runloop(self):
        # TODO Add loop for keyboard play and recording observations
        # Add loop for agent play
        self.disp = Display()
        self.root = self.disp.screen().root

        # Monitor keypres112s and button press
        t = Thread(target=self.getButton)
        t.daemon = True
        t.start()

        #print "RUN"
        self.logfile.write("leftpos,rightpos,ball,leftvel,rightvel,ballvel,action,reward,framei,i,terminate\n")
        self.q=Queue()
        prevscreen=np.zeros((210,160))
        #for i in range(1000000):
        i=0;
        prevrpos=None
        prevlpos=None
        prevball=None
        framei=0
        while True:
            input1 = self.fin.readline()
            temp=input1[-6:]
            
            terminate=int(temp.replace(":","").split(",")[0])
            reward=int(temp.replace(":","").split(",")[1])
            if terminate!=0:
                break
            
            if i>50:
                if reward!=0:
                    framei=0
                screen=input1[:-6]
                screen=map(''.join, zip(*[iter(screen)]*2))
                screen=map(lambda x: int(x,16), screen)
                screen=np.array(screen)
                screen=screen.reshape((210,160))
                screen=screen[34:194,:]
                screen[screen==34]=0
                #print np.unique(screen)
                #print screen
                try:
                    rightpos=(139,np.nonzero(screen[:,141])[0][0])
                except:
                    rightpos=None
                try:
                    leftpos=(19, np.nonzero(screen[:,19])[0][0])
                except:
                    leftpos=None
                try:
                    ball=np.argmax(screen==10)
                    ball=(ball/160,ball%160)
                except:
                    ball=None
                try:
                    ballvel=(ball[0]-prevball[0],ball[1]-prevball[1])
                except:
                    ballvel=None
                try:
                    rightvel=rightpos[1]-prevrpos[1]
                except:
                    rightvel=None
                try:
                    leftvel=leftpos[1]-prevlpos[1]
                except:
                    leftvel=None
                #print leftpos, rightpos, ball
                #pb.matshow(screen)
                #pb.show()
                #raw_input()
                #print screen.shape
                #print i
                action=self.action
                prevrpos=rightpos
                prevlpos=leftpos
                prevball=ball
                self.logfile.write(str(leftpos) +"," +str(rightpos) + "," + str(ball) +"," + str(leftvel) + "," + str(rightvel) + "," + str(ballvel) + "," + str(action) +"," + str(reward) + "," + str(framei) +","  + str(i) + "," +str(terminate)+"\n")

            self.fout.write(str(self.action)+",18\n")
            self.fout.flush()
            self.action=1
            i+=1
            framei+=1

        self.logfile.close()

    def getButton(self):
        ctx = self.disp.record_create_context(
                    0,
                    [record.AllClients],
                    [{
                            'core_requests': (0, 0),
                            'core_replies': (0, 0),
                            'ext_requests': (0, 0, 0, 0),
                            'ext_replies': (0, 0, 0, 0),
                            'delivered_events': (0, 0),
                            'device_events': (X.KeyReleaseMask, X.ButtonReleaseMask),
                            'errors': (0, 0),
                            'client_started': False,
                            'client_died': False,
                    }])


        self.disp.record_enable_context(ctx, self.handler)
        self.disp.record_free_context(ctx)


        while 1:
            # Infinite wait, doesn't do anything as no events are grabbed
            event = self.root.display.next_event()


    def handler(self, reply):
        """ This function is called when a xlib event is fired """
        data = reply.data
        while len(data):
            event, data = rq.EventField(None).parse_binary_value(data, self.disp.display, None, None)

            # # KEYCODE IS FOUND USERING event.detail
            # print event.detail

            # if event.type == X.KeyPress:
            #     # BUTTON PRESSED
            #     print "pressed"
            # elif event.type == X.KeyRelease:
            #     # BUTTON RELEASED
            #     print "released"
            # CODE HERE
            if event.detail == 10:
                #print "1 pressed"
                self.action=3
                pass
            elif event.detail == 11:
                #2 pressed
                #print "2 pressed"
                self.action=7
                pass



if __name__ == '__main__':
    bot = Bot()
    bot.runloop()
