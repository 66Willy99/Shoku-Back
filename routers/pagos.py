from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse
from transbank.webpay.webpay_plus.transaction import Transaction
from firebase_admin import db
import time

router = APIRouter(prefix="", tags=["Webpay"])

YOUR_IP = "192.168.18.57"
PORT = 8000
FRONTEND_PORT = 8081

transaction = Transaction()
transaction.configure_for_testing()


@router.get("/pay", response_class=HTMLResponse)
async def crear_transaccion(
    total: int = Query(...),
    orderId: str = Query(...),
    mesaId: str = Query(...),
    sillaId: str = Query(...),
    userId: str = Query(...),
    restauranteId: str = Query(...),
):
    try:
        assert isinstance(orderId, str) and orderId.strip() != ""
        print(f"✅ Recibido orderId: {orderId}, total: {total}")

        return_url = (
            f"http://{YOUR_IP}:{PORT}/web-return"
            f"?mesa_id={mesaId}"
            f"&silla_id={sillaId}"
            f"&user_id={userId}"
            f"&restaurante_id={restauranteId}"
        )

        response = transaction.create(
            buy_order=orderId[:26],
            session_id=f"ORD-{orderId}",
            amount=total,
            return_url=return_url,
        )

        return f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Redirigiendo a Webpay...</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: #f6f8fa;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    margin: 0;
                    color: #333;
                }}
                .card {{
                    background: white;
                    padding: 2rem;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    text-align: center;
                }}
                .loader {{
                    border: 4px solid #f3f3f3;
                    border-top: 4px solid #4CAF50;
                    border-radius: 50%;
                    width: 40px;
                    height: 40px;
                    animation: spin 1s linear infinite;
                    margin: 1rem auto;
                }}
                @keyframes spin {{
                    0% {{ transform: rotate(0deg); }}
                    100% {{ transform: rotate(360deg); }}
                }}
            </style>
        </head>
        <body>
            <div class="card">
                <h2>Conectando con Webpay...</h2>
                <div class="loader"></div>
                <p>Serás redirigido automáticamente.</p>
                <form id="webpay-form" action="{response['url']}" method="POST">
                    <input type="hidden" name="token_ws" value="{response['token']}" />
                    <noscript>
                        <p>JavaScript deshabilitado. Presiona para continuar.</p>
                        <button type="submit">Pagar</button>
                    </noscript>
                </form>
            </div>
            <script>document.getElementById('webpay-form').submit();</script>
        </body>
        </html>
        """
    except Exception as e:
        print(f"❌ Error en /pay: {e}")
        return HTMLResponse(f"<p>Error creando transacción: {e}</p>", status_code=500)


@router.get("/web-return", response_class=HTMLResponse)
async def confirmar_pago(
    request: Request,
    mesa_id: str = Query(None),
    silla_id: str = Query(None),
    user_id: str = Query(None),
    restaurante_id: str = Query(None),
):
    token = request.query_params.get("token_ws")
    if not token:
        return HTMLResponse("<p>Token no proporcionado</p>", status_code=400)

    approved = False
    order_id = None

    try:
        response = transaction.commit(token)
        approved = response["response_code"] == 0
        print(f"📥 Token recibido: {token}")
        print(f"💳 Resultado commit: {response}")

        if approved:
            session_id = response["session_id"]
            order_id = session_id.replace("ORD-", "")
            print(f"📦 Order ID extraído: {order_id}")

            if not restaurante_id or not mesa_id:
                restaurantes_ref = db.reference("/restaurantes").get()
                for rest_id, rest_data in restaurantes_ref.items():
                    if not isinstance(rest_data, dict):
                        continue
                    mesas = rest_data.get("mesas", {})
                    for mesa_id_candidate, mesa_data in mesas.items():
                        pedidos = mesa_data.get("pedidos", {})
                        if order_id in pedidos:
                            restaurante_id = rest_id
                            mesa_id = mesa_id_candidate
                            print(f"🔍 Pedido encontrado en Firebase: restaurante_id={restaurante_id}, mesa_id={mesa_id}")
                            break
                    if restaurante_id and mesa_id:
                        break

            if restaurante_id and mesa_id and order_id:
                base_path = f"/restaurantes/{restaurante_id}/mesas/{mesa_id}/pedidos/{order_id}"
                db.reference(f"{base_path}/estado_actual").set("pagado")
                db.reference(f"{base_path}/estados/estado_actual").set("pagado")
                db.reference(f"{base_path}/estados/pagado").set(int(time.time() * 1000))
                print(f"✅ Pedido {order_id} marcado como pagado.")
            else:
                print("❌ No se encontró restaurante_id o mesa_id para el pedido.")

    except Exception as e:
        print(f"❌ Error en commit o Firebase: {e}")

    app_link = "myapp://payment-complete"
    web_link = f"http://{YOUR_IP}:{FRONTEND_PORT}/estado"

    for k, v in {
        "mesa_id": mesa_id,
        "silla_id": silla_id,
        "user_id": user_id,
        "restaurante_id": restaurante_id,
    }.items():
        if v:
            app_link += f"{'?' if '?' not in app_link else '&'}{k}={v}"
            web_link += f"{'?' if '?' not in web_link else '&'}{k}={v}"

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Confirmación de Pago</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f6f8fa;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
                color: #333;
            }}
            .card {{
                background: white;
                padding: 2rem;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                text-align: center;
            }}
            .status {{
                font-size: 1.2rem;
                color: {"#4CAF50" if approved else "#F44336"};
                font-weight: bold;
            }}
        </style>
        <script>
            window.onload = function() {{
                console.log("🔁 Intentando redirigir a la app...");
                window.location.href = "{app_link}";

                setTimeout(function() {{
                    console.log("⏳ Redirección a app falló, redirigiendo a versión web.");
                    window.location.href = "{web_link}";
                }}, 1500);
            }};
        </script>
    </head>
    <body>
        <div class="card">
            <h2>Pago {'aprobado' if approved else 'rechazado'}</h2>
            <p class="status">{'¡Gracias por tu compra!' if approved else 'Hubo un error en el pago.'}</p>
            <p>Redirigiendo a la aplicación...</p>
            <p>Si no redirige automáticamente, haz clic <a href="{web_link}">aquí</a>.</p>
        </div>
    </body>
    </html>
    """
