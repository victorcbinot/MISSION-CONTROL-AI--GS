"""
src/alertas.py — Thresholds e lógica de decisão em código Python.
Toda decisão de status está aqui — a IA só interpreta, não decide.
"""


def avaliar_status(telemetria: dict) -> str:
    """
    Avalia todos os parâmetros e retorna o status mais grave.
    Lógica 100% em Python — não depende da IA para classificar.
    """
    temperatura = telemetria["sensor_termico"]
    energia = telemetria["energia"]
    sensor_optico = telemetria["sensor_optico"]
    buffer = telemetria["buffer_imagens"]
    geolocalizacao = telemetria["geolocalizacao"]
    focos = telemetria.get("focos_detectados", 0)
    downlink = telemetria.get("qualidade_downlink", 100)

    # ── CRÍTICO ────────────────────────────────────────────
    if temperatura > 90:
        return "CRITICO"
    if energia < 20:
        return "CRITICO"
    if sensor_optico == "FALHA":
        return "CRITICO"
    if geolocalizacao < 70:
        return "CRITICO"
    if buffer > 400:
        return "CRITICO"
    if focos >= 20:
        return "CRITICO"
    if downlink < 40:
        return "CRITICO"

    # ── ALERTA ─────────────────────────────────────────────
    if temperatura > 70:
        return "ALERTA"
    if energia < 50:
        return "ALERTA"
    if sensor_optico == "DEGRADADO":
        return "ALERTA"
    if buffer > 200:
        return "ALERTA"
    if geolocalizacao < 90:
        return "ALERTA"
    if focos >= 8:
        return "ALERTA"
    if downlink < 70:
        return "ALERTA"

    return "NORMAL"


def aplicar_resposta_automatica(telemetria: dict, status: str) -> list:
    """
    Respostas automatizadas para situações críticas.
    Retorna lista de ações disparadas automaticamente pelo sistema.
    """
    acoes = []

    energia = telemetria["energia"]
    buffer = telemetria["buffer_imagens"]
    focos = telemetria.get("focos_detectados", 0)
    sensor_optico = telemetria["sensor_optico"]
    downlink = telemetria.get("qualidade_downlink", 100)

    if energia < 15:
        acoes.append("🔴 AÇÃO AUTOMÁTICA: SAFE_MODE ativado. Sensores não-essenciais desligados.")
    elif energia < 20:
        acoes.append("🟠 AÇÃO AUTOMÁTICA: Modo economia ativado. Resolução reduzida para 60m/pixel.")

    if buffer > 400:
        acoes.append("🔴 AÇÃO AUTOMÁTICA: Imageamento SUSPENSO. Downlink de emergência iniciado.")
    elif buffer > 200:
        acoes.append("🟠 AÇÃO AUTOMÁTICA: Downlink prioritário ativado. Compressão aumentada.")

    if focos >= 20:
        acoes.append("🔴 AÇÃO AUTOMÁTICA: Alerta de EMERGÊNCIA enviado ao IBAMA e brigadas estaduais.")
    elif focos >= 8:
        acoes.append("🟠 AÇÃO AUTOMÁTICA: Notificação enviada ao INPE e centro de controle ambiental.")

    if sensor_optico == "FALHA":
        acoes.append("🔴 AÇÃO AUTOMÁTICA: Diagnóstico de hardware iniciado. Imageamento suspenso.")

    if downlink < 40:
        acoes.append("🔴 AÇÃO AUTOMÁTICA: Switching para antena secundária. Taxa de transmissão reduzida.")

    return acoes


def gerar_resumo_alertas(telemetria: dict, status: str) -> str:
    """
    Gera texto com todos os alertas identificados.
    Usado para injeção no prompt da IA — dados reais, não hardcoded.
    """
    alertas = []

    temperatura = telemetria["sensor_termico"]
    energia = telemetria["energia"]
    sensor_optico = telemetria["sensor_optico"]
    buffer = telemetria["buffer_imagens"]
    geolocalizacao = telemetria["geolocalizacao"]
    focos = telemetria.get("focos_detectados", 0)
    downlink = telemetria.get("qualidade_downlink", 100)

    if temperatura > 90:
        alertas.append(
            f"🔴 [CRÍTICO] Sensor térmico em {temperatura}°C — "
            f"risco de dano permanente. Impacto: perda de detecção de focos."
        )
    elif temperatura > 70:
        alertas.append(
            f"🟡 [ALERTA] Sensor térmico em {temperatura}°C — acima do normal, monitorar."
        )

    if energia < 20:
        alertas.append(
            f"🔴 [CRÍTICO] Energia em {energia}% — operação comprometida. "
            f"Impacto: imageamento em risco, possível perda do satélite."
        )
    elif energia < 50:
        alertas.append(
            f"🟡 [ALERTA] Energia em {energia}% — monitorar consumo. "
            f"Impacto: capacidade de imageamento pode ser reduzida."
        )

    if sensor_optico == "FALHA":
        alertas.append(
            "🔴 [CRÍTICO] Sensor óptico em FALHA — impossível capturar imagens. "
            "Impacto: dados para DETER/PRODES indisponíveis."
        )
    elif sensor_optico == "DEGRADADO":
        alertas.append(
            "🟡 [ALERTA] Sensor óptico DEGRADADO — qualidade reduzida. "
            "Impacto: imagens de desmatamento com menor precisão."
        )

    if buffer > 400:
        alertas.append(
            f"🔴 [CRÍTICO] Buffer em {buffer} MB — risco de perda de imagens. "
            f"Impacto: dados de focos e desmatamento podem ser perdidos permanentemente."
        )
    elif buffer > 200:
        alertas.append(
            f"🟡 [ALERTA] Buffer em {buffer} MB — downlink prioritário necessário. "
            f"Impacto: atraso na entrega de imagens ao INPE."
        )

    if geolocalizacao < 70:
        alertas.append(
            f"🔴 [CRÍTICO] Geolocalização em {geolocalizacao}% — coordenadas não confiáveis. "
            f"Impacto: brigadas podem ser enviadas para local errado."
        )
    elif geolocalizacao < 90:
        alertas.append(
            f"🟡 [ALERTA] Geolocalização em {geolocalizacao}% — leve imprecisão. "
            f"Impacto: coordenadas reportadas ao INPE com margem de erro."
        )

    if focos >= 20:
        alertas.append(
            f"🔴 [EMERGÊNCIA] {focos} focos detectados — emergência ambiental ativa. "
            f"Impacto: incêndio em larga escala, risco imediato à biodiversidade."
        )
    elif focos >= 8:
        alertas.append(
            f"🟡 [ALERTA] {focos} focos detectados — brigadas devem ser notificadas. "
            f"Impacto: múltiplos focos ativos precisam de resposta coordenada."
        )

    if downlink < 40:
        alertas.append(
            f"🔴 [CRÍTICO] Downlink em {downlink}% — transmissão comprometida. "
            f"Impacto: imagens retidas no satélite, INPE sem dados atualizados."
        )
    elif downlink < 70:
        alertas.append(
            f"🟡 [ALERTA] Downlink em {downlink}% — transmissão instável. "
            f"Impacto: possível atraso na entrega de imagens ao DETER."
        )

    if not alertas:
        return "✅ Nenhum alerta ativo. Todos os parâmetros dentro das faixas normais."

    return "\n".join(alertas)