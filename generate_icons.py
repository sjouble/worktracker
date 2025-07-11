#!/usr/bin/env python3
"""
PWA 아이콘 생성 스크립트
PIL을 사용하여 간단한 아이콘을 생성합니다.
"""

import os
from PIL import Image, ImageDraw, ImageFont

# 생성할 아이콘 크기들
icon_sizes = [
    (16, 16),
    (32, 32),
    (72, 72),
    (96, 96),
    (128, 128),
    (144, 144),
    (152, 152),
    (192, 192),
    (384, 384),
    (512, 512)
]

def create_icon(size):
    """지정된 크기의 아이콘을 생성합니다."""
    width, height = size
    
    # 새 이미지 생성 (파란색 배경)
    image = Image.new('RGBA', (width, height), (13, 110, 253, 255))
    draw = ImageDraw.Draw(image)
    
    # 원형 배경
    margin = max(4, width // 32)
    draw.ellipse([margin, margin, width - margin, height - margin], 
                 fill=(255, 255, 255, 255), outline=(13, 110, 253, 255), width=max(1, width // 64))
    
    # 중앙에 "W" 텍스트 그리기
    try:
        # 폰트 크기 계산
        font_size = max(8, width // 4)
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        # 폰트를 찾을 수 없으면 기본 폰트 사용
        font = ImageFont.load_default()
    
    # 텍스트 그리기
    text = "W"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    draw.text((x, y), text, fill=(13, 110, 253, 255), font=font)
    
    return image

def generate_icons():
    """아이콘들을 생성합니다."""
    icons_dir = "static/icons"
    
    # 아이콘 디렉토리가 없으면 생성
    if not os.path.exists(icons_dir):
        os.makedirs(icons_dir)
    
    print("PWA 아이콘 생성 중...")
    
    for width, height in icon_sizes:
        filename = f"icon-{width}x{height}.png"
        filepath = os.path.join(icons_dir, filename)
        
        try:
            # 아이콘 생성
            icon = create_icon((width, height))
            icon.save(filepath, 'PNG')
            print(f"✓ {filename} 생성 완료")
        except Exception as e:
            print(f"✗ {filename} 생성 실패: {e}")
    
    print("아이콘 생성 완료!")

if __name__ == "__main__":
    generate_icons() 