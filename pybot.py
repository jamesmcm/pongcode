import os
import numpy as np
import pylab as pb

class Bot(object):
#TODO decide frameskip
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

    def runloop(self):
        # TODO Add loop for keyboard play and recording observations
        # Add loop for agent play

        prevscreen=np.zeros((210,160))
        for i in range(1000000):
            input1 = self.fin.readline()
            if i>120:
                    screen=input1[:-6]
                    screen=map(''.join, zip(*[iter(screen)]*2))
                    screen=map(lambda x: int(x,16), screen)
                    screen=np.array(screen)
                    screen=screen.reshape((210,160))
                    screen=screen[34:194,:]
                    screen[screen==34]=0
                    #print np.unique(screen)
                    #print screen
                    rightpos=(139,np.nonzero(screen[:,141])[0][0])
                    leftpos=(19, np.nonzero(screen[:,19])[0][0])
                    ball=np.argmax(screen==10)
                    ball=(ball/160,ball%160)
                    print leftpos, rightpos, ball
                    #pb.matshow(screen)
                    #pb.show()
                    #raw_input()
                    print screen.shape
                    print i

            self.fout.write("18,18\n")
            self.fout.flush()

if __name__ == '__main__':
    bot = Bot()
    bot.runloop()
