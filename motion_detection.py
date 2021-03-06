
import numpy as np
import datetime, time, os
import timelapse
import picamera.array
from threading import Thread

class MyMotionDetector(picamera.array.PiMotionAnalysis):

    def __init__(self, camera, detected):
       super().__init__(camera)
       self.detected = detected

    def analyse(self, a):
        '''https://picamera.readthedocs.io/en/release-1.12/recipes2.html
        '''
        a = np.sqrt(
            np.square(a['x'].astype(np.float)) +
            np.square(a['y'].astype(np.float))
            ).clip(0, 255).astype(np.uint8)
        # If there're more than 10 vectors with a magnitude greater
        # than 60, then say we've detected motion
        if (a > 50).sum() > 5:
            self.detected['detected'] = True
        else:#?#
            pass #--++==**ooGGWWMMWWGGoo**==++--

class SimpleMotionDetection(Thread): # I's going to be a daemon thread in the future
    '''Detects motion analyzing camera output.
    '''

    def __init__(self,
                 group=None,
                 target=None,
                 name="MD-thread",
                 args=(),
                 kwargs=None,
                 verbose=None):
        super().__init__()
        #def __init__(self, camera, connection, camera_options, raspeye_path):
        import os, constants

        self.camera, self.conn, self.cam_opt, self.raspeye_path = args
        self.detected = {'detected': False}
        the_file = os.path.join(self.raspeye_path, 'md-timetable.txt')
        if not os.path.isfile(the_file):
            filehnd = open(the_file, 'w')
            filehnd.close()
        self.theday = datetime.date.today().isoformat()
        self.thefile = the_file
        self.DIR_NAME = constants.MD_DIR_NAME
        self.update_path()
        self.timedelta = datetime.timedelta(seconds=1)
        self.lastpic = datetime.datetime.now()
        self.pictaken = 0

    def update_path(self):
        the_path = os.path.join(self.raspeye_path, self.DIR_NAME, self.theday)
        if not os.path.isdir(the_path):
            os.makedirs(the_path, exist_ok=True)
        self.thepath = the_path

    def update_md_times(self):
        '''writing the time to the time-table file and pictures.
            Up to 2 pictures per second (the second one has 'b' at the end of its name).
        '''
        filehnd = open(self.thefile, 'a')
        filehnd.write(datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S.%f\n"))
        filehnd.close()
        if datetime.datetime.now() >= self.lastpic + self.timedelta:
            self.pictaken = 0
            #timelapse.timelapse_start(self.thepath, self.camera, self.cam_opt, md=True)
            current_pic_name = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.%f.jpg")
            self.camera.capture(os.path.join(self.thepath, current_pic_name),
                                use_video_port=True,
                                splitter_port=3,
                                quality=85)
            self.lastpic = datetime.datetime.now()
            self.pictaken += 1
        else:
            if self.pictaken <= 1:
                current_pic_name = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.%f_b.jpg")
                self.camera.capture(os.path.join(self.thepath, current_pic_name),
                                use_video_port=True,
                                splitter_port=3,
                                quality=85)
                self.pictaken += 1

        return


    def run(self):
        if 'md_active' in self.cam_opt['running']: # this is just in case, probably not needed at all
             self.cam_opt['md_exit'] = True
        #     del self.cam_opt['runnig']['md_active']
        # else:
        if self.cam_opt['md_exit']: # for testing
            if 'md_active' in self.cam_opt['running']:
                del self.cam_opt['running']['md_active']
            self.cam_opt['md_exit'] = 0
            return
        self.cam_opt['running']['md_active'] = 1 #self
        self.camera.resolution = (640, 480)
        self.camera.framerate = 30
        self.camera.start_recording('/dev/null', format='h264', motion_output=MyMotionDetector(self.camera, self.detected))
        while (not self.cam_opt['md_exit']) and (not self.cam_opt['exit']):
            if self.detected['detected']:
                self.detected['detected'] = False
                self.update_md_times()
            if self.theday != datetime.date.today().isoformat():
                self.theday = datetime.date.today().isoformat()
                self.update_path()
        print('[MD] Received <exit> signal!')
        self.camera.stop_recording()
        if 'md_active' in self.cam_opt['running']:
            del self.cam_opt['running']['md_active']
        self.cam_opt['md_exit'] = 0
        return

# def mo_detect(camera, connection, cam_opt, raspeye_path):
#     md_instance = SimpleMotionDetection(camera, connection, cam_opt, raspeye_path)
#     md_instance.start_md()
#     return

if __name__ == '__main__':
        print("It's a module for rapeye - srv.py\nStart raspeye - srv.py!")
