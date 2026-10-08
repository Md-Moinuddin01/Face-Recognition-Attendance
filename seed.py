'''
Seed initial demo data for FaceTrack AI:
- Default Departments
- Super Admin & Staff Users
- Schedules
- Demo Face Enrollments
- Today's sample attendance records
'''
import uuid
from datetime import datetime, timezone, date, timedelta
from app.core.database import SessionLocal, Base, engine
from app.models.models import (
    User, Department, Schedule, AttendanceRecord, FaceEnrollment,
    UserRole, AttendanceStatus, EnrollmentStatus
)
from app.core.security import hash_password
from app.ml.face_service import face_service

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(User).filter(User.email == "admin@facetrack.ai").first():
            print("[Seed] Database already seeded.")
            return

        print("[Seed] Creating departments...")
        eng = Department(name="Engineering", code="ENG", description="Software & AI Engineering")
        des = Department(name="Design", code="DES", description="UI/UX & Creative")
        ops = Department(name="Operations", code="OPS", description="Operations & Management")
        db.add_all([eng, des, ops])
        db.flush()

        print("[Seed] Creating schedules...")
        standard_sched = Schedule(
            name="Standard Office Hours",
            department_id=eng.id,
            start_time="09:00",
            end_time="17:00",
            late_threshold_minutes=15,
            days_of_week="1,2,3,4,5",
            is_active=True,
        )
        db.add(standard_sched)
        db.flush()

        print("[Seed] Creating users...")
        admin = User(
            email="admin@facetrack.ai",
            full_name="Admin Director",
            employee_id="EMP-001",
            hashed_password=hash_password("admin123"),
            role=UserRole.ADMIN,
            is_active=True,
            consent_given=True,
            department_id=eng.id,
        )
        moin = User(
            email="moin@facetrack.ai",
            full_name="Md Moinuddin",
            employee_id="EMP-002",
            hashed_password=hash_password("moin123"),
            role=UserRole.STAFF,
            is_active=True,
            consent_given=True,
            department_id=eng.id,
        )
        sarah = User(
            email="sarah@facetrack.ai",
            full_name="Sarah Chen",
            employee_id="EMP-003",
            hashed_password=hash_password("sarah123"),
            role=UserRole.STAFF,
            is_active=True,
            consent_given=True,
            department_id=des.id,
        )
        alex = User(
            email="alex@facetrack.ai",
            full_name="Alex Rivera",
            employee_id="EMP-004",
            hashed_password=hash_password("alex123"),
            role=UserRole.STAFF,
            is_active=True,
            consent_given=True,
            department_id=ops.id,
        )
        db.add_all([admin, moin, sarah, alex])
        db.flush()

        print("[Seed] Creating demo face enrollments...")
        import json
        for u in [moin, sarah, alex]:
            emb = face_service.get_embedding(b"mock_seed_bytes")
            fe = FaceEnrollment(
                user_id=u.id,
                embedding_json=json.dumps(emb),
                embedding_model="mock",
                num_samples=3,
                status=EnrollmentStatus.ACTIVE,
            )
            db.add(fe)

        print("[Seed] Creating initial attendance records...")
        today = date.today().isoformat()
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        
        db.add(AttendanceRecord(
            user_id=moin.id,
            schedule_id=standard_sched.id,
            status=AttendanceStatus.PRESENT,
            check_in_time=datetime.now(timezone.utc) - timedelta(hours=2),
            confidence_score=0.96,
            liveness_passed=True,
            date=today,
        ))
        db.add(AttendanceRecord(
            user_id=sarah.id,
            schedule_id=standard_sched.id,
            status=AttendanceStatus.LATE,
            check_in_time=datetime.now(timezone.utc) - timedelta(hours=1, minutes=20),
            confidence_score=0.94,
            liveness_passed=True,
            date=today,
        ))
        db.add(AttendanceRecord(
            user_id=alex.id,
            schedule_id=standard_sched.id,
            status=AttendanceStatus.PRESENT,
            check_in_time=datetime.now(timezone.utc) - timedelta(days=1, hours=4),
            confidence_score=0.97,
            liveness_passed=True,
            date=yesterday,
        ))

        db.commit()
        print("[Seed] Database successfully populated with initial test data!")
    except Exception as e:
        db.rollback()
        print(f"[Seed] Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()

