from app.modules.auth.models import AdminDoc

async def get_admin_by_email(email: str) -> AdminDoc | None:
    return await AdminDoc.find_one(AdminDoc.email == email)

async def create_admin(email: str, hashed_password: str) -> AdminDoc:
    admin = AdminDoc(email=email, hashed_password=hashed_password)
    return await admin.insert()