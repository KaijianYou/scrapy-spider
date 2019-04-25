import hashlib
import base64


def get_md5(bs: bytes) -> str:
    md5 = hashlib.md5()
    md5.update(bs)
    return md5.hexdigest()


def save_img_from_base64_text(text: str, file_path: str):
    """从Baser64编码文本中解码图片，并把文件保存到 file_path"""
    code = text.replace('data:image/jpg;base64,', '').replace('%0A', '')
    with open(file_path, 'wb') as f:
        f.write(base64.b64decode(code))
