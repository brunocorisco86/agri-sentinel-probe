import httpx
from typing import Dict, Any, Optional
from app.core.config import settings

async def generate_probe_ai_insight(
    location_name: str,
    device_id: str,
    hardware_model: str,
    days: int,
    total_telemetries: int,
    uptime_pct: float,
    avg_rtt_ms: float,
    max_rtt_ms: float,
    avg_rssi_dbm: float,
    incident_count: int,
    lan_target_ip: str,
    lan_target_mac: str
) -> str:
    """
    Gera parecer executivo de IA via Google Gemini Flash sobre a estabilidade do link rural e do Gateway Dragino.
    """
    if not settings.GEMINI_API_KEY:
        return (
            f"Relatório gerado automaticamente para o período de {days} dias. "
            f"O ponto '{location_name}' registrou disponibilidade de {uptime_pct:.1f}% com latência média no Gateway de {avg_rtt_ms:.1f} ms. "
            f"Sinal Wi-Fi médio em {avg_rssi_dbm:.0f} dBm. Operação estável dentro dos parâmetros esperados."
        )

    prompt = f"""
Você é o Especialista Chefe em Engenharia de Conectividade e IoT Rural da C.Vale.
Analise os dados de telemetria da sonda 'Keepalive Foresight / Agri-Sentinel' nos últimos {days} dias e elabore uma síntese executiva e técnica (máximo de 3 parágrafos concisos):

DADOS TÉCNICOS DA SONDA:
- Ponto / Granja: {location_name} (ID: {device_id})
- Hardware: {hardware_model}
- Período Analisado: Últimos {days} dias ({total_telemetries} batimentos registrados)
- Disponibilidade / Uptime: {uptime_pct:.1f}%
- Alvo Local (Gateway Dragino): IP {lan_target_ip or 'WAN-Only'} (MAC: {lan_target_mac or 'N/A'})
- Latência Média Ping ICMP: {avg_rtt_ms:.1f} ms (Pico Máximo: {max_rtt_ms:.1f} ms)
- Nível de Sinal Wi-Fi Médio: {avg_rssi_dbm:.0f} dBm
- Total de Incidentes de Queda no Período: {incident_count}

DIRETRIZES DA RESPOSTA:
1. Parágrafo 1 - Parecer da Qualidade da Internet (WAN) e do Gateway Local (Dragino): Classifique a estabilidade (Excelente, Boa, Moderada ou Crítica) e analise a latência e o sinal Wi-Fi.
2. Parágrafo 2 - Risco para o Abastecimento de Ração: Avalie se há risco de atraso na leitura dos sensores de silos ou corte na entrega de ração da granja.
3. Parágrafo 3 - Recomendação Técnica Preventiva: Ação prática recomendada para a equipe de campo ou suporte de TI.

Responda em tom executivo, formal e direto em português PT-BR, sem introduções vazias.
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 800
        }
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json", "X-goog-api-key": settings.GEMINI_API_KEY}
            )
            if res.status_code == 200:
                data = res.json()
                parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                text_response = "".join(p.get("text", "") for p in parts if "text" in p).strip()
                if text_response:
                    return text_response
    except Exception as e:
        print(f"[Gemini AI Error] {e}")

    # Fallback determinístico
    return (
        f"Análise de {days} dias para {location_name}: O enlace de comunicação manteve {uptime_pct:.1f}% de disponibilidade "
        f"com latência média de {avg_rtt_ms:.1f} ms no Gateway Dragino. "
        f"Foram registrados {incident_count} incidentes no período. Nível de sinal Wi-Fi médio em {avg_rssi_dbm:.0f} dBm."
    )
