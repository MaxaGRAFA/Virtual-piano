import cv2
import pyglet 
import math
import numpy as np

class piano():
    def __init__(self) -> None:
        self.num_keys = 14
        self.keys_coordinates = {}

        #range of the key pressed (zeros mean that no key was pressed)
        self.pressed_key_range = [0,0]
        #The last time when used a key
        self.last_using = 0
        
    #Draw keys
    def draw(self, frame, timestamp):
        
        frame = np.copy(frame)

        self.timestamp = timestamp

        #determine the coordinates where the keys will be
        if not self.keys_coordinates:
            self.add_coordinates(frame)
 
        key_width = frame.shape[1] // self.num_keys

        for i in range(self.num_keys):
            x1= i * key_width
            x2= (i + 1) * key_width

            #place to draw the key
            range_1 = (x1, 0)
            range_2 = (x2, 70)

            cv2.rectangle(frame, range_1, range_2, (255, 255, 255), -1)
            cv2.rectangle(frame, range_1, range_2, (0, 0, 0))       
        
            #if a key is pressed, paint it gray
            if (self.pressed_key_range[0], self.pressed_key_range[1]) == (range_1, range_2):

                cv2.rectangle(frame, range_1, range_2, (200, 200, 200), -1)

                #If enough time has passed, then reset the key pressed
                if (self.timestamp - self.last_using) > 6:
                    self.pressed_key_range = [0,0]


        for i in range(self.num_keys - 1):
            if i % 7 not in {2, 5}:  # Skip space for black keys
                x = (i + 1) * key_width
                cv2.rectangle(frame, (x, 0), (x + key_width // 2, 70 // 2), (0, 0, 0), -1)

        return frame
    #Adding key coordinates
    def add_coordinates(self, frame):
        
        key_width = frame.shape[1] // self.num_keys

        keys = (
            'sound\key01.wav',
            'sound\key02.wav',
            'sound\key03.wav',
            'sound\key04.wav',
            'sound\key05.wav', 
            'sound\key06.wav',
            'sound\key07.wav',
            'sound\key08.wav', 
            'sound\key09.wav',
            'sound\key10.wav',
            'sound\key11.wav', 
            'sound\key12.wav',
            'sound\key13.wav',
            'sound\key14.wav'
              )

        for i in range(self.num_keys):
            x1= i * key_width
            x2= (i + 1) * key_width
            self.keys_coordinates[(x1, 0),(x2, 70)] = keys[i]


    def play_sound(self, pointer, thumb):
        

        distance = math.sqrt((pointer[0] - thumb[0])**2 + (pointer[1] - thumb[1])**2)

        #If the distance between the index finger and thumb is less than 20 
        # and some time has passed since the last use

        if distance < 16 and (self.timestamp - self.last_using) > 8:

            x = pointer[0]
            y = pointer[1]

            selected_range = None

            #select the range(key) in which there is an index finger
            for range_ in self.keys_coordinates:
                
                x1, y1 = range_[0]
                x2, y2 = range_[1]
                if x1 <= x <= x2 and y1 <= y <= y2:
                    selected_range = range_

            
            note = self.keys_coordinates.get(selected_range)

            if note != None:
                music = pyglet.media.load(note)
                music.play()

                self.pressed_key_range = (selected_range[0], selected_range[1])

                self.last_using = self.timestamp



