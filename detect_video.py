import time
from absl import app, flags, logging
from absl.flags import FLAGS
import cv2
import tensorflow as tf
from yolov3_tf2.models import (
    YoloV3, YoloV3Tiny
)
from yolov3_tf2.dataset import transform_images
from yolov3_tf2.utils import draw_outputs


flags.DEFINE_string('classes', './data/coco.names', 'path to classes file')
flags.DEFINE_string('weights', './checkpoints/yolov3.tf',
                    'path to weights file')
flags.DEFINE_boolean('tiny', False, 'yolov3 or yolov3-tiny')
flags.DEFINE_integer('size', 416, 'resize images to')
flags.DEFINE_string('video', './data/video.mp4',
                    'path to video file or number for webcam)')
flags.DEFINE_string('output_video', './data/video_output.mp4','path to where output video will be stored')


def main(_argv):
    if FLAGS.tiny:
        yolo = YoloV3Tiny()
    else:
        yolo = YoloV3()

    yolo.load_weights(FLAGS.weights)
    logging.info('weights loaded')

    class_names = [c.strip() for c in open(FLAGS.classes).readlines()]
    logging.info('classes loaded')

    times = []

    try:
        vid = cv2.VideoCapture(int(FLAGS.video))
        vid.set(3, 3840)
        vid.set(4, 2160)
        vid.set(5, 10)
    except:
        vid = cv2.VideoCapture(FLAGS.video)
    frame_width = int(vid.get(3))
    frame_height = int(vid.get(4))
    vid_out = cv2.VideoWriter(FLAGS.output_video, cv2.VideoWriter_fourcc('M','J','P','G'),30.0, (frame_width,frame_height))

    while True:
        _, img = vid.read()
        if img is None:
            logging.warning("Empty Frame")
            time.sleep(0.1)
            break

        img_in = tf.expand_dims(img, 0)
        img_in = transform_images(img_in, FLAGS.size)

        t1 = time.time()
        boxes, scores, classes, nums = yolo.predict(img_in)
        t2 = time.time()
        times.append(t2-t1)
        times = times[-20:]

        img = draw_outputs(img, (boxes, scores, classes, nums), class_names)
        img = cv2.putText(img, "Time: {:.2f}ms".format(sum(times)/len(times)*1000), (0, 30),
                          cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
        vid_out.write(img)                  
        cv2.imshow('output', img)
        if cv2.waitKey(1) == ord('q'):
            break
    vid_out.release()
    vid.release()
    cv2.destroyAllWindows()
    

if __name__ == '__main__':
    try:
        app.run(main)
    except SystemExit:
        pass
