from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse
from transbank.webpay.webpay_plus.transaction import Transaction
from firebase_admin import db
import time
from config import BACKEND_IP, BACKEND_PORT, FRONTEND_PORT, FRONTEND_IP
from services.pedido_service import PedidoService

router = APIRouter(prefix="", tags=["Webpay"])


transaction = Transaction()
transaction.configure_for_testing()


@router.get("/pay", response_class=HTMLResponse)
async def crear_transaccion(
    total: int = Query(...),
    pedidos: str = Query(...),  # JSON string con array de pedido IDs
    mesaId: str = Query(...),
    sillaId: str = Query(...),
    userId: str = Query(...),
    restauranteId: str = Query(...),
):
    try:
        import json
        
        # Parsear los pedidos
        pedidos_list = json.loads(pedidos)
        assert isinstance(pedidos_list, list) and len(pedidos_list) > 0
        
        # Crear el registro de pago en Firebase usando tu estructura
        restaurante_ref = db.reference(f"usuarios/{userId}/restaurantes/{restauranteId}")
        pagos_ref = restaurante_ref.child("pagos")
        nuevo_pago_ref = pagos_ref.push()
        pago_id = nuevo_pago_ref.key
        
        pago_data = {
            "pedidos": pedidos_list,
            "tipo": "webpay",
            "total": total,
            "estado": "pendiente",
            "fecha_creacion": int(time.time() * 1000),
            "mesa_id": mesaId,
            "silla_id": sillaId
        }
        
        nuevo_pago_ref.set(pago_data)
        print(f"✅ Pago creado: {pago_id}, pedidos: {pedidos_list}, total: {total}")

        return_url = (
            f"http://{BACKEND_IP}:{BACKEND_PORT}/web-return"
            f"?mesa_id={mesaId}"
            f"&silla_id={sillaId}"
            f"&user_id={userId}"
            f"&restaurante_id={restauranteId}"
            f"&pago_id={pago_id}"
        )

        response = transaction.create(
            buy_order=pago_id[:26],  # Usar pago_id como buy_order
            session_id=f"PAY-{pago_id}",  # Usar pago_id en session_id
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
    pago_id: str = Query(None),
):
    token = request.query_params.get("token_ws")
    if not token:
        return HTMLResponse("<p>Token no proporcionado</p>", status_code=400)

    approved = False
    
    try:
        response = transaction.commit(token)
        approved = response["response_code"] == 0
        print(f"📥 Token recibido: {token}")
        print(f"💳 Resultado commit: {response}")

        if approved and pago_id:
            session_id = response["session_id"]
            extracted_pago_id = session_id.replace("PAY-", "")
            print(f"📦 Pago ID extraído: {extracted_pago_id}")

            # Actualizar el registro de pago usando tu estructura
            restaurante_ref = db.reference(f"usuarios/{user_id}/restaurantes/{restaurante_id}")
            pago_ref = restaurante_ref.child("pagos").child(extracted_pago_id)
            pago_data = pago_ref.get()
            
            if pago_data:
                # Actualizar estado del pago
                pago_ref.update({
                    "estado": "pagado",
                    "fecha_pago": int(time.time() * 1000),
                    "transaccion_id": response.get("authorization_code", ""),
                    "response_code": response["response_code"]
                })
                
                # Actualizar todos los pedidos asociados
                pedidos_list = pago_data.get("pedidos", [])
                pedidos_ref = restaurante_ref.child("pedidos")
                
                for pedido_id in pedidos_list:
                    pedido_ref = pedidos_ref.child(pedido_id)
                    estados_ref = pedido_ref.child("estados")
                    estados_ref.update({
                        "estado_actual": "pagado",
                        "pagado": int(time.time() * 1000)
                    })
                    pedido_ref.update({"pago_id": extracted_pago_id})
                
                # Verificar si todos los pedidos de la mesa están pagados usando PedidoService
                pedido_service = PedidoService()
                try:
                    pedidos_mesa_response = pedido_service.obtener_pedidos_mesa(user_id, restaurante_id, mesa_id)
                    pedidos_mesa = pedidos_mesa_response.get("pedidos", {})
                except Exception as e:
                    print(f"⚠️ Error obteniendo pedidos de la mesa: {e}")
                    pedidos_mesa = {}
                
                # Verificar si todos los pedidos de la mesa están pagados
                todos_pagados = True
                if pedidos_mesa:
                    for pedido_id, pedido in pedidos_mesa.items():
                        estado_actual = pedido.get("estados", {}).get("estado_actual")
                        if estado_actual != "pagado":
                            todos_pagados = False
                            break
                    
                    print(f"📊 Mesa {mesa_id}: {len(pedidos_mesa)} pedidos encontrados, todos pagados: {todos_pagados}")
                else:
                    print(f"⚠️ No se encontraron pedidos para la mesa {mesa_id}")
                    todos_pagados = False
                
                # Solo actualizar estado de mesa si TODOS los pedidos están pagados
                if todos_pagados:
                    mesa_ref = restaurante_ref.child("mesas").child(mesa_id)
                    mesa_data = mesa_ref.get()
                    if mesa_data:
                        mesa_ref.update({
                            "estado": "pagado",
                            "fecha_pago": int(time.time() * 1000)
                        })
                        print(f"✅ Mesa {mesa_data.get('numero', mesa_id)} marcada como PAGADO (todos los pedidos pagados).")
                    else:
                        print(f"⚠️ No se encontró la mesa {mesa_id} para actualizar su estado.")
                else:
                    print(f"⏸️ Mesa {mesa_id} NO se marca como pagado porque aún hay pedidos pendientes.")
                
                print(f"✅ Pago {extracted_pago_id} y pedidos {pedidos_list} marcados como pagados.")
            else:
                print("❌ No se encontró el registro de pago.")

    except Exception as e:
        print(f"❌ Error en commit o Firebase: {e}")

    app_link = "myapp://payment-complete"
    web_link = f"http://{FRONTEND_IP}:{FRONTEND_PORT}/estado"

    for k, v in {
        "mesa_id": mesa_id,
        "silla_id": silla_id,
        "user_id": user_id,
        "restaurante_id": restaurante_id,
        "pago_id": pago_id,
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
