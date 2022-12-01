import os

import cv2
import ffmpeg

# import google.cloud.storage
import requests
from flask import jsonify
from google.oauth2 import service_account

# import shlex
# import subprocess


def classification(request):
    # 結合する動画のパス
    video_path = request.json["video_path"]
    # 結合する音楽のパス
    music_path = request.json["music_path"]
    # 結合した動画のパス
    new_video_path = request.json["new_video_path"]

    # 動画の再生時間
    video = cv2.VideoCapture(video_path)
    video_frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
    video_fps = video.get(cv2.CAP_PROP_FPS)
    video_sec = video_frame_count / video_fps
    # 音楽の再生時間
    music_info = ffmpeg.probe(
        music_path,
    )
    music_sec = float(music_info["streams"][0]["duration"])

    # 音楽の再生時間が動画の再生時間より長いときは動画の再生時間に合わせる
    if video_sec <= music_sec:
        music_sec = video_sec

    # 動画と音楽の結合
    instream1 = ffmpeg.input(video_path)
    instream2 = ffmpeg.input(music_path, t=music_sec)
    stream = ffmpeg.output(
        # instream1, instream2, new_video_path, vcodec="copy", acodec="aac"
        instream1,
        instream2,
        new_video_path,
        # acodec="aac",
    )
    ffmpeg.run(stream, overwrite_output=True)

    # 結合した動画をLolipopへ転送
    url = "https://iut-b.main.jp/up"
    files = {"file": open(new_video_path, "rb")}
    res = requests.post(url, files=files)

    return jsonify({"new_video_path": res.status_code}), 201
