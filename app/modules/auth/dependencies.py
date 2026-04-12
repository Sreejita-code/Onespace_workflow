from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.modules.auth.service import decode_access_token
from app.modules.auth.models import AdminDoc

security = HTTPBearer()

async def require_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> AdminDoc:
    token = credentials.credentials
    admin_id = decode_access_token(token)
    
    if not admin_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    admin = await AdminDoc.get(admin_id)
    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin not found")
        
    return admin