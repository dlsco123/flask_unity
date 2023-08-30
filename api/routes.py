from flask import Blueprint, jsonify
from utils.mediaP import PoseDetection  
import threading

myhome_bp = Blueprint('myhome', __name__, url_prefix='/myhome')

#TODO : Unity 쪽에서는 문자열을 파싱하여 STT: 또는 POSE:로 시작하는 부분을 확인하고, 그에 따라 알맞게 처리
@myhome_bp.route('/startDetection', methods=['POST'],)
def start_detection():
    try:

        # 병렬로 처리될 함수들
        detector = PoseDetection()

        pose_thread = threading.Thread(target=detector.run_pose_detection)
        stt_thread = threading.Thread(target=detector.start_stt)

        pose_thread.start()
        stt_thread.start()

        return jsonify({"message": "Detection started"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
