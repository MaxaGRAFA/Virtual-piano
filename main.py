from mediapipe.framework.formats import landmark_pb2
from mediapipe.tasks import python
from mediapipe import solutions
import mediapipe as mp
import numpy as np
import piano_
import math
import cv2

class HandTracker():
    def __init__(self) -> None:
        self.base_option = python.BaseOptions(model_asset_path='hand_landmarker.task')
        self.options = mp.tasks.vision.HandLandmarkerOptions(
                                    self.base_option,
                                    running_mode=mp.tasks.vision.RunningMode.LIVE_STREAM, 
                                    result_callback=self.callback,
                                    num_hands=2)
        

        self.results = None
        self.piano = piano_.piano()
        self.pointers_coord = 0 # pointer finger coordinates 
        self.thumbs_coord = 0 # thumb finger coordinates

    def start_live_stream(self):
        cap = cv2.VideoCapture(0)
        timestamp = 0

        with mp.tasks.vision.HandLandmarker.create_from_options(self.options) as landmarker:
            while True:
                ret, frame = cap.read()

                if not ret:
                    print("camera doesn't work")
                    break    

                imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                numpy_frame = np.array(imgRGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=numpy_frame)


                landmarker.detect_async(mp_image, timestamp)

                
                #play the note if possible
                self.play_note()
                
                #display piano on the screen
                frame = self.draw_piano(frame, timestamp)

                frame = self.show_landmark(frame, self.results)

                timestamp += 1

                cv2.imshow('OutPut', frame)

                if cv2.waitKey(1) == ord('q'):
                    break

            
            cap.release()
            cv2.destroyAllWindows()

    #Show hand landmarks
    def show_landmark(self, rgb_image, detection_result):
        if detection_result is None:
            return rgb_image
        
        annotated_image = np.copy(rgb_image)
        hand_landmarks_list = detection_result.hand_landmarks

        #save new finger coordinates
        if len(hand_landmarks_list) != 0:
            
            self.pointers_coord, self.thumbs_coord = self.save_fingers_coordinates(hand_landmarks_list, rgb_image)

            #Draw landmarks
            for hand_landmarks in hand_landmarks_list:
                hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
                hand_landmarks_proto.landmark.extend([
                    landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
                ])

                #draw landmarks
                solutions.drawing_utils.draw_landmarks(
                    annotated_image,
                    hand_landmarks_proto,
                    solutions.hands.HAND_CONNECTIONS,
                    solutions.drawing_utils.DrawingSpec(color=(0,0,0),thickness=2, circle_radius=2),
                    solutions.drawing_utils.DrawingSpec(color=(20,20,20),thickness=2, circle_radius=2)
                )

        return annotated_image
    
    #saving coordinates for the index finger and thumb
    def save_fingers_coordinates(self, hand_landmarks_list, rgb_image):
        h, w, _ = rgb_image.shape # h-height w-width

        #Save for two hands
        if len(hand_landmarks_list) == 2:
            pointers = (
                (hand_landmarks_list[0][8].x * w), (hand_landmarks_list[0][8].y * h),
                (hand_landmarks_list[1][8].x * w), (hand_landmarks_list[1][8].y * h)
            )
            thumbs = (
                (hand_landmarks_list[0][4].x * w), (hand_landmarks_list[0][4].y * h),
                (hand_landmarks_list[1][4].x * w), (hand_landmarks_list[1][4].y * h)
            )

        #Save for one hand
        else:
            pointers = (
                (hand_landmarks_list[0][8].x * w), (hand_landmarks_list[0][8].y * h),
                None, None
            )
            thumbs = (
                (hand_landmarks_list[0][4].x * w), (hand_landmarks_list[0][4].y * h),
                None, None
            )

        return pointers, thumbs
    
    #Play sound
    def play_note(self):
        if self.pointers_coord == 0 or self.thumbs_coord == 0:
            return
        
        first_pointer = (self.pointers_coord[0], self.pointers_coord[1])
        second_pointer = (self.pointers_coord[2], self.pointers_coord[3])

        first_thumb = (self.thumbs_coord[0], self.thumbs_coord[1])
        second_thumb = (self.thumbs_coord[2], self.thumbs_coord[3])

        for pointer, thumb in [(first_pointer, first_thumb), (second_pointer, second_thumb)]:
            if pointer == (None, None) or thumb == (None, None):
                return
            
            self.piano.play_sound(pointer, thumb)

    def draw_piano(self, frame, timestamp):
        frame = self.piano.draw(frame, timestamp)
        return frame

    def callback(self, result: mp.tasks.vision.HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
        self.results = result

if __name__ == "__main__":
    hand_tracker = HandTracker()
    hand_tracker.start_live_stream()
