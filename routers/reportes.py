from fastapi import APIRouter, Depends, HTTPException, Query
from services.reporte_service import ReportService
from typing import Dict, Any


router = APIRouter(prefix="/reportes", tags=["reportes"])


@router.get("/resumen")
def reporte_resumen(
    user_id: str = Query(..., description="ID del usuario"),
    restaurante_id: str = Query(..., description="ID del restaurante"),
    service: ReportService = Depends(ReportService)
):
    """
    Devuelve el resumen de reportes del restaurante.
    """
    try:
        reporte = service.calcular_reporte(user_id, restaurante_id)
        return reporte
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))