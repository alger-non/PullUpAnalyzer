import cv2

import Utils
import os
import sys
import pickle


input_source = "test_videos/video2.mp4"
model = "COCO"

filename = os.path.basename(input_source).split('.')[0]
output_data = open(f'test_videos/{filename}_{model}', 'wb')
protoFile, weightsFile = Utils.set_model(model)

inWidth = 368
inHeight = 368


cap = cv2.VideoCapture(input_source)
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print('Frame count:', frame_count)

net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)


while cv2.waitKey(1) < 0:
    print('Position:', int(cap.get(cv2.CAP_PROP_POS_FRAMES)))
    hasFrame, frame = cap.read()
    if not hasFrame:
        break

    inpBlob = cv2.dnn.blobFromImage(frame, 1.0 / 255, (inWidth, inHeight),
                                    (0, 0, 0), swapRB=False, crop=False)
    net.setInput(inpBlob)
    output = net.forward()
    pickle.dump(output, output_data)


output_data.close()
cap.release()
