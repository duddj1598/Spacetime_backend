"""
데이터베이스 마이그레이션 스크립트
기존 테이블에 새로운 컬럼을 추가합니다.

실행 방법:
python migrate_db.py
"""

from sqlalchemy import create_engine, text
from app.database import SQLALCHEMY_DATABASE_URL

def migrate_database():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            # User 테이블에 profile_image 컬럼 추가
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN profile_image TEXT
            """))
            print("✅ profile_image 컬럼이 추가되었습니다.")
        except Exception as e:
            print(f"⚠️ profile_image 컬럼 추가 실패 (이미 존재할 수 있음): {e}")
        
        try:
            # User 테이블에 monthly_note 컬럼 추가
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN monthly_note TEXT
            """))
            print("✅ monthly_note 컬럼이 추가되었습니다.")
        except Exception as e:
            print(f"⚠️ monthly_note 컬럼 추가 실패 (이미 존재할 수 있음): {e}")
        
        conn.commit()
    
    print("\n✅ 데이터베이스 마이그레이션이 완료되었습니다.")

if __name__ == "__main__":
    migrate_database()