# backend/init_admin.py

from backend.database import SessionLocal
from backend.auth.models import User
from backend.auth.auth_utils import hash_password

def create_admin():
    db = SessionLocal()
    username = "T0"
    email = "t0_admin@example.com"  # 你可以自定义
    password = "123456"
    password_hash = hash_password(password)

    # 检查是否已存在
    exists = db.query(User).filter((User.username == username) | (User.email == email)).first()
    if exists:
        print("管理员已存在，无需重复添加。")
        return

    admin = User(
        username=username,
        email=email,
        password_hash=password_hash,
        is_admin=True
    )
    db.add(admin)
    db.commit()
    db.close()
    print("管理员账号已初始化：用户名 T0，密码 123456")

if __name__ == "__main__":
    create_admin()
