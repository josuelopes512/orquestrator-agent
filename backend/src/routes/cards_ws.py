from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..services.card_ws import card_ws_manager

router = APIRouter(prefix="/api/cards", tags=["cards-ws"])

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint para notificações de cards"""
    await card_ws_manager.connect(websocket)
    try:
        while True:
            # Mantém conexão aberta
            await websocket.receive_text()
    except WebSocketDisconnect:
        card_ws_manager.disconnect(websocket)
