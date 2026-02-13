# app/crud/device_data.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.device_data import DeviceData
from app.schemas.device_data import DeviceDataCreate

async def create_device_data_in_db(device_id: str, data: dict, db: AsyncSession = None):
    from app.db.session import async_session  # fallback if db is None

    payload = DeviceData(
        device_id=device_id,
        timestamp=data.get("timestamp"),
        data=data.get("sensors")
    )

    if db is None:
        async with async_session() as session:
            async with session.begin():
                session.add(payload)
    else:
        db.add(payload)
        await db.flush()
