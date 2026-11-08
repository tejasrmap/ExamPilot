from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.app.db.session import get_db
from backend.app.db.models import Profile, APIProvider
from backend.app.core.deps import get_current_user
from backend.app.core.security import encrypt_api_key, decrypt_api_key, mask_api_key
from backend.app.providers.registry import provider_registry
from backend.app.providers.base import ModelInfo

router = APIRouter(prefix="/providers", tags=["API Providers"])

class SaveProviderRequest(BaseModel):
    provider: str # openai, gemini, anthropic, openrouter
    api_key: str
    default_model: Optional[str] = None
    is_default: bool = False

class TestKeyRequest(BaseModel):
    provider: str
    api_key: Optional[str] = None # If omitted, tests existing saved key for this provider

class SetDefaultRequest(BaseModel):
    provider: str
    default_model: Optional[str] = None

class ProviderResponse(BaseModel):
    id: str
    provider: str
    masked_key: str
    default_model: Optional[str] = None
    status: str
    is_default: bool
    last_verified_at: Optional[datetime] = None
    created_at: datetime

@router.get("", response_model=List[ProviderResponse])
def get_user_providers(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    providers = db.query(APIProvider).filter(APIProvider.user_id == current_user.id).all()
    return [
        ProviderResponse(
            id=p.id,
            provider=p.provider,
            masked_key=p.masked_key,
            default_model=p.default_model,
            status=p.status,
            is_default=p.is_default,
            last_verified_at=p.last_verified_at,
            created_at=p.created_at
        )
        for p in providers
    ]

@router.get("/models")
async def get_models(
    provider: Optional[str] = None,
    current_user: Profile = Depends(get_current_user)
):
    all_models = await provider_registry.get_all_models()
    if provider:
        clean = provider.lower().strip()
        return all_models.get(clean, [])
    return all_models

@router.post("/test")
async def test_provider_connection(
    req: TestKeyRequest,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    prov_adapter = provider_registry.get_provider(req.provider)
    key_to_test = req.api_key

    if not key_to_test:
        # Check if saved in database
        saved = db.query(APIProvider).filter(
            APIProvider.user_id == current_user.id,
            APIProvider.provider == req.provider.lower().strip()
        ).first()
        if not saved:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No saved API key found for {req.provider}. Please supply an API key to test."
            )
        try:
            key_to_test = decrypt_api_key(saved.encrypted_api_key)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to decrypt stored credentials: {str(e)}"
            )

    is_valid = await prov_adapter.validate_key(key_to_test)
    if not is_valid:
        return {
            "success": False,
            "provider": req.provider,
            "status": "failed",
            "message": f"Connection test failed for {req.provider}. Please verify that the API key is active and has appropriate permissions."
        }
    
    # If saved in DB, update status
    saved = db.query(APIProvider).filter(
        APIProvider.user_id == current_user.id,
        APIProvider.provider == req.provider.lower().strip()
    ).first()
    if saved:
        saved.status = "connected"
        saved.last_verified_at = datetime.utcnow()
        db.commit()

    return {
        "success": True,
        "provider": req.provider,
        "status": "connected",
        "message": f"Connection verified successfully with {req.provider}!"
    }

@router.post("", response_model=ProviderResponse)
async def save_provider(
    req: SaveProviderRequest,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    prov_clean = req.provider.lower().strip()
    prov_adapter = provider_registry.get_provider(prov_clean)
    
    # 1. Test key validity
    is_valid = await prov_adapter.validate_key(req.api_key)
    conn_status = "connected" if is_valid else "failed"

    # 2. Encrypt at rest with AES-256-GCM
    encrypted = encrypt_api_key(req.api_key)
    masked = mask_api_key(req.api_key)

    # 3. Check default model selection
    default_model = req.default_model
    if not default_model:
        models = await prov_adapter.list_models()
        if models:
            default_model = models[0].id

    # 4. If setting as default, unset other defaults
    if req.is_default:
        db.query(APIProvider).filter(APIProvider.user_id == current_user.id).update({"is_default": False})

    # 5. Check if provider record already exists
    existing = db.query(APIProvider).filter(
        APIProvider.user_id == current_user.id,
        APIProvider.provider == prov_clean
    ).first()

    now = datetime.utcnow()
    if existing:
        existing.encrypted_api_key = encrypted
        existing.masked_key = masked
        existing.default_model = default_model
        existing.status = conn_status
        existing.last_verified_at = now if is_valid else existing.last_verified_at
        if req.is_default:
            existing.is_default = True
        db.commit()
        db.refresh(existing)
        target = existing
    else:
        # If this is the user's first provider, make it default automatically
        count = db.query(APIProvider).filter(APIProvider.user_id == current_user.id).count()
        is_def = req.is_default or (count == 0)
        
        target = APIProvider(
            user_id=current_user.id,
            provider=prov_clean,
            encrypted_api_key=encrypted,
            masked_key=masked,
            default_model=default_model,
            status=conn_status,
            is_default=is_def,
            last_verified_at=now if is_valid else None
        )
        db.add(target)
        db.commit()
        db.refresh(target)

    return ProviderResponse(
        id=target.id,
        provider=target.provider,
        masked_key=target.masked_key,
        default_model=target.default_model,
        status=target.status,
        is_default=target.is_default,
        last_verified_at=target.last_verified_at,
        created_at=target.created_at
    )

@router.post("/default")
def set_default_provider(
    req: SetDefaultRequest,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    prov_clean = req.provider.lower().strip()
    target = db.query(APIProvider).filter(
        APIProvider.user_id == current_user.id,
        APIProvider.provider == prov_clean
    ).first()
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider {req.provider} not found for this account."
        )

    db.query(APIProvider).filter(APIProvider.user_id == current_user.id).update({"is_default": False})
    target.is_default = True
    if req.default_model:
        target.default_model = req.default_model
    db.commit()
    return {"message": f"{req.provider} set as default provider."}

@router.delete("/{provider_id}")
def delete_provider(
    provider_id: str,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    target = db.query(APIProvider).filter(
        APIProvider.id == provider_id,
        APIProvider.user_id == current_user.id
    ).first()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")
    
    db.delete(target)
    db.commit()
    return {"message": "Provider key deleted successfully."}

