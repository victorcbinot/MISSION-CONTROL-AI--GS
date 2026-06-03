"""
src/telemetria.py — Geração de dados simulados de telemetria do EnviroSat.
Simula satélite de observação ambiental similar ao Amazônia-1 / Landsat.
"""

import random
import json
from datetime import datetime


def gerar_telemetria_simulada() -> dict:
    """
    Gera dados simulados com chance de anomalia a cada chamada.
    Retorna dicionário com todos os parâmetros monitorados.
    """

    def valor_com_anomalia(minimo: float, maximo: float, chance: float = 0.15) -> float:
        if random.random() < chance:
            desvio = (maximo - minimo) * random.uniform(0.2, 0.6)
            if random.random() < 0.5:
                return round(minimo - desvio, 2)
            else:
                return round(maximo + desvio, 2)
        return round(random.uniform(minimo, maximo), 2)

    sensor_termico = valor_com_anomalia(18.0, 45.0, chance=0.12)
    energia = max(0.0, valor_com_anomalia(30.0, 100.0, chance=0.12))
    buffer_imagens = round(max(0.0, valor_com_anomalia(0.0, 250.0, chance=0.15)), 1)
    geolocalizacao = min(100.0, valor_com_anomalia(85.0, 100.0, chance=0.10))
    focos_detectados = max(0, int(valor_com_anomalia(0, 8, chance=0.20)))
    qualidade_downlink = valor_com_anomalia(70.0, 100.0, chance=0.10)
    cobertura_nuvens = round(max(0.0, valor_com_anomalia(0.0, 40.0, chance=0.18)), 1)

    opcoes_optico = (
        ["OPERACIONAL"] * 8 +
        ["DEGRADADO"] * 1 +
        ["FALHA"] * 1
    )
    sensor_optico = random.choice(opcoes_optico)

    areas = [
        "Amazônia Legal - PA/AM",
        "Cerrado - MT/GO",
        "Pantanal - MS",
        "Mata Atlântica - SP/RJ",
        "Caatinga - BA/PE",
    ]

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "orbita": random.randint(1200, 9999),
        "area_monitorada": random.choice(areas),
        "sensor_termico": sensor_termico,
        "sensor_optico": sensor_optico,
        "buffer_imagens": buffer_imagens,
        "geolocalizacao": geolocalizacao,
        "energia": energia,
        "focos_detectados": focos_detectados,
        "qualidade_downlink": qualidade_downlink,
        "cobertura_nuvens": cobertura_nuvens,
    }


def carregar_cenario(nome_cenario: str) -> dict:
    """Carrega cenário pré-definido do JSON para testes."""
    with open("data/cenarios.json", "r", encoding="utf-8") as arquivo:
        cenarios = json.load(arquivo)
    return cenarios[nome_cenario]


def formatar_para_prompt(telemetria: dict) -> str:
    """Formata telemetria em texto estruturado para injeção no prompt da IA."""
    return f"""
=== TELEMETRIA ENVIROSAT — {telemetria.get('timestamp', 'N/A')} ===
Órbita #: {telemetria.get('orbita', 'N/A')}
Área monitorada: {telemetria.get('area_monitorada', 'N/A')}

[SENSORES]
- Sensor térmico (temperatura): {telemetria['sensor_termico']} °C
- Sensor óptico (status):       {telemetria['sensor_optico']}
- Focos de calor detectados:    {telemetria.get('focos_detectados', 'N/A')}
- Cobertura de nuvens:          {telemetria.get('cobertura_nuvens', 'N/A')} %

[OPERAÇÕES]
- Buffer de imagens:            {telemetria['buffer_imagens']} MB
- Precisão de geolocalização:   {telemetria['geolocalizacao']} %
- Energia disponível:           {telemetria['energia']} %
- Qualidade de downlink:        {telemetria.get('qualidade_downlink', 'N/A')} %
""".strip()