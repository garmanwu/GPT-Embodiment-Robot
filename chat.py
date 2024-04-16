import json
import socket
from openai import OpenAI
import pygame
import struct

OPEN_API_KEY='your_api_key'

client = OpenAI(api_key=OPEN_API_KEY)

def send_to_iphone(kaomoji, audio_file):
    HOST = 'iPhone_IP_address'  
    PORT = 12345
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            kaomoji_data = kaomoji.encode()
            kaomoji_len = len(kaomoji_data)
            with open(audio_file, 'rb') as f:
                audio_data = f.read()
            audio_len = len(audio_data)
            data = struct.pack(f'!I{kaomoji_len}sI{audio_len}s', kaomoji_len, kaomoji_data, audio_len, audio_data)
            s.sendall(data)
    except:
        print("iPhone连接失败,请检查IP地址和端口号。")

def play_audio(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.delay(100)
    pygame.mixer.quit()

while True:
    prompt = input("请输入对话内容,输入quit退出: ")
    if prompt.lower() == 'quit':
        break

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "假设你是一个可以和人类对话的具身机器人,反应内容包括响应内容,以及对应的kaomoji表情和头部动作(双轴舵机转动参数)。以json格式返回，响应内容定义为response，表情定义为kaomoji，kaomoji表情要反映响应内容情感。与表情对应的头部动作水平角度（无需单位）为servoX，范围是10~170，面向正前方是90。与表情对应的头部动作垂直角度（无需单位）为servoY，范围是10~170，水平面是90。"},
            {"role": "user", "content": prompt},
        ]
    )

    result = json.loads(response.choices[0].message.content)
    print(response.choices[0].message.content)

    # 将response内容转为实时语音
    speech_response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=result['response'],
    )

    speech_response.stream_to_file("output.mp3")
    send_to_iphone(result['kaomoji'], "output.mp3")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('127.0.0.1', 7892))
        data = json.dumps({"servoX": result['servoX'], "servoY": result['servoY']}).encode()
        s.sendall(data)