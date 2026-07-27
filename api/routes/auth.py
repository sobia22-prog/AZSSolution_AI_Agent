from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from api.db import db_client
from api.db.models import UserModel
from api.enums import PostHogEvent
from api.schemas.auth import AuthResponse, LoginRequest, SignupRequest, UserResponse
from api.services.auth.depends import create_user_configuration_with_mps_key, get_user
from api.services.posthog_client import capture_event
from api.utils.auth import create_jwt_token, hash_password, verify_password

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/signup", response_model=AuthResponse)
async def signup(request: SignupRequest):
    raise HTTPException(
        status_code=403,
        detail="Public registration is disabled on this instance."
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    from api.constants import ADMIN_EMAIL, ADMIN_PASSWORD

    # 1. Check if email matches configured bootstrap admin (case-insensitive)
    if request.email.lower() == ADMIN_EMAIL.lower():
        if request.password != ADMIN_PASSWORD:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Get or create the bootstrap admin user in the database.
        user = await db_client.get_user_by_email(ADMIN_EMAIL)
        if not user:
            hashed = hash_password(ADMIN_PASSWORD)
            user = await db_client.create_user_with_email(
                email=ADMIN_EMAIL.lower(),
                password_hash=hashed,
                name="Admin",
            )

            # Create organization for the user
            org_provider_id = f"org_{user.provider_id}"
            organization, _ = await db_client.get_or_create_organization_by_provider_id(
                org_provider_id=org_provider_id, user_id=user.id
            )

            # Link user to organization
            await db_client.add_user_to_organization(user.id, organization.id)
            await db_client.update_user_selected_organization(user.id, organization.id)

            # Create default service configuration
            try:
                mps_config = await create_user_configuration_with_mps_key(
                    user.id, organization.id, user.provider_id
                )
                if mps_config:
                    await db_client.update_user_configuration(user.id, mps_config)
            except Exception:
                logger.warning(
                    "Failed to create default configuration for auto-seeded Admin user", exc_info=True
                )
                
            # Re-fetch user to make sure all properties are up to date
            user = await db_client.get_user_by_email(ADMIN_EMAIL)
    else:
        # 2. Check the database for custom created admin accounts
        user = await db_client.get_user_by_email(request.email)
        if not user or not user.password_hash:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Verify password using bcrypt check
        if not verify_password(request.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")

    # Create JWT token
    token = create_jwt_token(user.id, user.email)

    capture_event(
        distinct_id=str(user.provider_id),
        event=PostHogEvent.SIGNED_IN,
        properties={
            "organization_id": user.selected_organization_id,
            "auth_provider": "local",
        },
    )

    return AuthResponse(
        token=token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            name="Admin",
            organization_id=user.selected_organization_id,
            provider_id=user.provider_id,
        ),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(user: UserModel = Depends(get_user)):
    return UserResponse(
        id=user.id,
        email=user.email,
        organization_id=user.selected_organization_id,
        provider_id=user.provider_id,
    )
