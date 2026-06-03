"""Motor de análise da Mission Control AI."""
import os
from ollama import Client
from dotenv import load_dotenv
from pathlib import Path

from src.telemetria import gerar_telemetria_simulada, formatar_para_prompt
from src.alertas import avaliar_status, gerar_resumo_alertas, aplicar_resposta_automatica

load_dotenv()

# Identificação da trilha — ALTEREM conforme a escolha do grupo
TRILHA = "envirosat"  # "agrosat" | "envirosat" | "connectsat" | "mobilitysat"

client = Client(
    host="https://ollama.com",
    headers={'Authorization': 'Bearer ' + os.environ.get('OLLAMA_API_KEY', '')}
)


def llm(prompt, system=None, max_tokens=1200, temperature=0.3): #Os tokens foram aumentados para 1200 porque o modelo estava dando respostas incompletas
    """Envia prompt ao gpt-oss:120b via Ollama Cloud."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    try:
        return client.chat(
            model="gpt-oss:120b",
            messages=messages,
            options={"num_predict": max_tokens, "temperature": temperature},
            stream=False
        )['message']['content'].strip()
    except Exception as e:
        return f"⚠️ Erro ao consultar IA: {e}"


def load_system_prompt():
    """Lê o system prompt do arquivo prompts/system_prompt.md"""
    path = Path("prompts/system_prompt.md")
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "Você é um assistente."  # fallback genérico


class MissionEngine:
    """Motor de análise — vocês completam os métodos abaixo."""

    def __init__(self):
        self.trilha = TRILHA
        self.system_prompt = load_system_prompt()
        self._historico_ciclos = []
        self._max_historico = 3

    def is_ready(self):
        return True

    def status_snapshot(self):
        """Retorna texto resumindo o estado atual da telemetria."""
        dados = gerar_telemetria_simulada()
        status = avaliar_status(dados)
        acoes = aplicar_resposta_automatica(dados, status)
        resumo = gerar_resumo_alertas(dados, status)

        emoji = {"NORMAL": "✅", "ALERTA": "🟡", "CRITICO": "🔴"}.get(status, "❓")

        linhas = [
            f"🛰️  EnviroSat — Órbita #{dados.get('orbita', 'N/A')}",
            f"📅 {dados['timestamp']}",
            f"🗺️  Área: {dados.get('area_monitorada', 'N/A')}",
            f"⚡ Status geral: {emoji} {status}",
            "",
            "── PARÂMETROS ──────────────────────────────",
            f"  🌡️  Sensor térmico:        {dados['sensor_termico']} °C",
            f"  📷 Sensor óptico:          {dados['sensor_optico']}",
            f"  🔥 Focos detectados:       {dados.get('focos_detectados', 'N/A')}",
            f"  ☁️  Cobertura de nuvens:   {dados.get('cobertura_nuvens', 'N/A')} %",
            f"  💾 Buffer de imagens:      {dados['buffer_imagens']} MB",
            f"  📍 Geolocalização:         {dados['geolocalizacao']} %",
            f"  🔋 Energia disponível:     {dados['energia']} %",
            f"  📡 Qualidade downlink:     {dados.get('qualidade_downlink', 'N/A')} %",
            "",
            "── ALERTAS ─────────────────────────────────",
            resumo,
        ]

        if acoes:
            linhas.append("")
            linhas.append("── AÇÕES AUTOMÁTICAS ───────────────────────")
            linhas.extend(acoes)

        return "\n".join(linhas)

    def analyze(self, pergunta_usuario):
        """Analisa a pergunta com base na telemetria + alertas + IA."""

        # 1. Coletar dados via src.telemetria
        dados = gerar_telemetria_simulada()

        # 2. Avaliar alertas via src.alertas
        status = avaliar_status(dados)
        resumo_alertas = gerar_resumo_alertas(dados, status)
        acoes = aplicar_resposta_automatica(dados, status)
        texto_acoes = "\n".join(acoes) if acoes else "Nenhuma ação automática necessária."

        # Histórico dos últimos ciclos (memória de contexto)
        self._historico_ciclos.append({
            "timestamp": dados["timestamp"],
            "energia": dados["energia"],
            "focos": dados.get("focos_detectados", 0),
            "status": status,
        })
        if len(self._historico_ciclos) > self._max_historico:
            self._historico_ciclos.pop(0)

        historico_txt = ""
        if len(self._historico_ciclos) > 1:
            linhas_hist = ["=== HISTÓRICO DOS ÚLTIMOS CICLOS ==="]
            for c in self._historico_ciclos[:-1]:
                linhas_hist.append(
                    f"[{c['timestamp']}] Energia:{c['energia']}% | "
                    f"Focos:{c['focos']} | Status:{c['status']}"
                )
            historico_txt = "\n".join(linhas_hist)

        # 3. Montar prompt com dados + alertas + pergunta
        prompt = f"""
{formatar_para_prompt(dados)}

=== STATUS CALCULADO PELO SISTEMA ===
{status}

=== ALERTAS IDENTIFICADOS PELO SISTEMA ===
{resumo_alertas}

=== AÇÕES AUTOMÁTICAS JÁ DISPARADAS ===
{texto_acoes}

{historico_txt}

=== PERGUNTA DO OPERADOR ===
{pergunta_usuario}

Responda em português brasileiro. Conecte sempre a análise técnica
ao impacto concreto no território brasileiro e para as personas atendidas
(operador do INPE, coordenador de brigada, analista de compliance).
Baseie-se exclusivamente nos dados fornecidos acima.
""".strip()

        # 4. Chamar llm(prompt, system=self.system_prompt)
        resposta = llm(prompt, system=self.system_prompt)

        # 5. Retornar a resposta
        if status == "CRITICO":
            resposta = "🔴 SITUAÇÃO CRÍTICA DETECTADA\n\n" + resposta
        elif status == "ALERTA":
            resposta = "🟡 ATENÇÃO — PARÂMETROS FORA DO NORMAL\n\n" + resposta

        return resposta