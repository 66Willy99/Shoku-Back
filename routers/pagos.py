from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from transbank.webpay.webpay_plus.transaction import Transaction

router = APIRouter(
    prefix="",
    tags=["Webpay"]
)

# IP y puertos
YOUR_IP = "192.168.18.157"
PORT = 8000
FRONTEND_PORT = 8081

# Crear instancia y configurar
transaction = Transaction()
transaction.configure_for_testing()

@router.get("/pay", response_class=HTMLResponse)
async def crear_transaccion(total: int, orderId: str):
    return_url = f"http://{YOUR_IP}:{PORT}/web-return"
    try:
        response = transaction.create(
            buy_order=str(orderId),
            session_id=f"ORD-{orderId}",
            amount=total,
            return_url=return_url
        )
        return f"""
        <html>
            <body>
                <form id="webpay-form" action="{response['url']}" method="POST">
                    <input type="hidden" name="token_ws" value="{response['token']}" />
                </form>
                <script>document.getElementById('webpay-form').submit();</script>
                <p>Redirigiendo a Webpay…</p>
            </body>
        </html>
        """
    except Exception as e:
        return HTMLResponse(f"<p>Error creando transacción: {e}</p>", status_code=500)

@router.get("/web-return", response_class=HTMLResponse)
async def confirmar_pago(request: Request):
    token = request.query_params.get("token_ws")
    if not token:
        return HTMLResponse("<p>Token no proporcionado</p>", status_code=400)

    approved = False
    try:
        response = transaction.commit(token)
        approved = response['response_code'] == 0
    except Exception as e:
        print("Error en commit:", e)

    app_link = f"myapp://payment-complete?token_ws={token}&approved={approved}"
    web_link = f"http://{YOUR_IP}:{FRONTEND_PORT}/estado?token_ws={token}&approved={approved}"

    return f"""
    <html>
        <head>
            <meta http-equiv="refresh" content="0; URL='{app_link}'" />
        </head>
        <body>
            <p>Pago {'aprobado' if approved else 'rechazado'}.</p>
            <p>Si estás en navegador, haz click <a href="{web_link}">aquí</a>.</p>
        </body>
    </html>
    """
