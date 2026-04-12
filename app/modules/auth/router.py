from fastapi import APIRouter, HTTPException, Response, status
from app.modules.auth.schemas import LoginRequest, TokenResponse
from app.modules.auth import service, repository

router = APIRouter(tags=["Auth"])

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, response: Response):
    admin = await repository.get_admin_by_email(request.email)
    if not admin or not service.verify_password(request.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = service.create_access_token(admin.id)
    
    # Optional: Set a refresh token in a secure HttpOnly cookie here if needed
    
    return {"access_token": access_token, "token_type": "bearer"}

# --- TEMPORARY ROUTE: Remove before production! ---
@router.post("/setup-first-admin")
async def setup_admin(request: LoginRequest):
    existing = await repository.get_admin_by_email(request.email)
    if existing:
        raise HTTPException(status_code=400, detail="Admin already exists")
    
    hashed = service.hash_password(request.password)
    admin = await repository.create_admin(request.email, hashed)
    return {"message": f"Admin {admin.email} created successfully."}