# from ping3 import ping
# import cv2
# import serial

# def is_camera_reachable(ip):
#     """ يتحقق مما إذا كان الجهاز يستجيب للـ ping """
#     response = ping(ip)
#     return response is not None

# def is_camera_streaming(ip):
#     """يتحقق مما إذا كانت الكاميرا تعمل عبر RTSP"""
#     stream_url = f"rtsp://{ip}:554/stream"
#     cap = cv2.VideoCapture(stream_url)
#     if cap.isOpened():
#         cap.release()
#         return True
#     return False


# def is_serial_device_available(port):
#     """يتحقق مما إذا كان الجهاز متصلاً بالمنفذ التسلسلي"""
#     try:
#         ser = serial.Serial(port, 9600, timeout=1)
#         ser.close()
#         return True
#     except:
#         return False
