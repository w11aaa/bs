import numpy as np
import os
from PIL import Image
from io import BytesIO
import base64
import random

class FaceRecognition:
    def __init__(self, tolerance=0.6):
        self.tolerance = tolerance
    
    # 从图片文件中提取人脸特征（模拟）
    def extract_face_encoding(self, image_path):
        try:
            # 模拟提取特征，返回随机向量
            return np.random.rand(128), "人脸特征提取成功"
        except Exception as e:
            return None, f"提取人脸特征失败: {str(e)}"
    
    # 从字节流中提取人脸特征（模拟）
    def extract_face_encoding_from_bytes(self, image_bytes):
        try:
            # 模拟提取特征，返回随机向量
            return np.random.rand(128), "人脸特征提取成功"
        except Exception as e:
            return None, f"提取人脸特征失败: {str(e)}"
    
    # 从base64字符串中提取人脸特征（模拟）
    def extract_face_encoding_from_base64(self, base64_string):
        try:
            # 移除base64前缀（如果有）
            if 'base64,' in base64_string:
                base64_string = base64_string.split('base64,')[1]
            
            # 解码base64字符串为字节流
            image_bytes = base64.b64decode(base64_string)
            
            # 模拟提取特征，返回随机向量
            return np.random.rand(128), "人脸特征提取成功"
        except Exception as e:
            return None, f"处理base64图片失败: {str(e)}"
    
    # 比较两个人脸特征是否匹配（模拟）
    def compare_faces(self, known_encoding, unknown_encoding):
        try:
            # 模拟计算相似度分数
            score = random.uniform(0.5, 1.0)
            is_match = score > 0.7
            
            return is_match, score
        except Exception as e:
            return False, 0.0
    
    # 批量识别人脸（模拟）
    def recognize_faces(self, unknown_encoding, known_encodings_with_ids):
        """
        批量识别未知人脸与已知人脸的匹配（模拟）
        
        Args:
            unknown_encoding: 未知人脸的特征编码
            known_encodings_with_ids: 已知人脸的特征编码和对应的ID列表，格式为 [(encoding1, id1), (encoding2, id2), ...]
        
        Returns:
            (是否匹配成功, 匹配的ID, 最大相似度分数)
        """
        try:
            if not known_encodings_with_ids:
                return False, None, 0.0
            
            # 分离已知的编码和ID
            known_ids = [i for _, i in known_encodings_with_ids]
            
            # 模拟匹配过程，有80%的概率返回一个匹配结果
            if random.random() < 0.8 and known_ids:
                best_match_id = random.choice(known_ids)
                best_match_score = random.uniform(0.7, 0.98)
                return True, best_match_id, best_match_score
            else:
                # 未匹配成功，返回一个较低的相似度分数
                return False, None, random.uniform(0.5, 0.7)
        except Exception as e:
            return False, None, 0.0
    
    # 保存人脸图片
    def save_face_image(self, image_bytes, save_path):
        try:
            image = Image.open(BytesIO(image_bytes))
            # 确保目录存在
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            # 保存图片
            image.save(save_path)
            return True, "图片保存成功"
        except Exception as e:
            return False, f"图片保存失败: {str(e)}"

# 创建一个全局实例
face_recognizer = FaceRecognition()