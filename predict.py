from ultralytics import YOLO
from ultralytics.solutions import speed_estimation
from ultralytics.solutions import object_counter
import cv2

from db_handler import db_insert_cars_detected
from auto_report import send_email
# from ocr_reader import ocr_image


def predict(video_path):
    model = YOLO("yolov8n.pt")
    names = model.model.names

    cap = cv2.VideoCapture(video_path)
    # cap = cv2.VideoCapture("/Users/Ryuuu/Desktop/240226_CS301/05_Code/02_Traffic Surveillance System/01_Cloud Platform/static/files/test3.mp4")
    assert cap.isOpened(), "Error reading video file"
    w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

    # Video writer
    video_writer = cv2.VideoWriter("speed_estimation.avi",
                                cv2.VideoWriter_fourcc(*'mp4v'),
                                fps,
                                (w, h))

    ##########################################
    # Speed Calculations
    ##########################################
    line_points = [(0, 440), (1280, 440)]

    # Init speed-estimation obj
    speed_obj = speed_estimation.SpeedEstimator()
    speed_obj.set_args(reg_pts=line_points,
                    names=names,
                    view_img=True,
                    line_thickness=2,
                    region_thickness=1,
                    spdl_dist_thresh = 10)




    ##########################################
    # Counter
    ##########################################

    # Init Object Counter
    counter = object_counter.ObjectCounter()
    counter.set_args(view_img=True,
                    reg_pts=line_points,
                    classes_names=model.names,
                    draw_tracks=True,
                    line_thickness=3,
                    region_thickness=1,
                    count_bg_color=(0, 185, 255),
                    )


    while cap.isOpened():
        success, im0 = cap.read()
        if not success:
            print("Video frame is empty or video processing has been successfully completed.")
            break

        tracks = model.track(im0, 
                        tracker= "botsort.yaml",
                        conf=0.2,
                        iou=0.5,
                        persist=True, 
                        show=False, 
                        verbose=True)

        im0 = speed_obj.estimate_speed(im0, tracks)
        im0 = counter.start_counting(im0, tracks)
        # im0 = speed_obj.ocr_image(im0, tracks)
        
        # video_writer.write(im0)
    
        yield im0
        
    
    # num_detected_objects = len(speed_obj.trk_idslist)
    for i in speed_obj.trk_idslist:
        db_insert_cars_detected(speed_obj, i)
        
        
        # # Auto_Report
        # detected_speed = speed_obj.dist_data[i]
        # if detected_speed > 120:
        #     send_email(speed_obj.detected_cars[i], speed_obj.dist_data[i])
            
    
    # show In Count
    # speed_obj.output()
    
    # speed_obj.report_cars()
    

# cap.release()
# video_writer.release()
cv2.destroyAllWindows()








# def predict(video_path):
#     model = YOLO("yolov8n.pt")
#     speed_obj = speed_estimation.SpeedEstimator()
#     cap = cv2.VideoCapture(video_path)
    
#     while cap.isOpened():
#         success, im0 = cap.read()
#         tracks = model.track(im0, 
#                         tracker= "botsort.yaml",
#                         conf=0.2,
#                         iou=0.5,
#                         persist=True, 
#                         show=False, 
#                         verbose=True)
        
#         im0 = speed_obj.estimate_speed(im0, tracks)
    
#         yield im0
        
        