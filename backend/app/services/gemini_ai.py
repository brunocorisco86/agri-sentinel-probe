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
    Gera parecer técnico operacional e executivo emitido pela equipe de Engenharia de Telecom / NOC.
    """
    if not settings.GEMINI_API_KEY:
        return (
            f"Avaliação técnica do período de {days} dias para a unidade '{location_name}': "
            f"O enlace registrou índice de disponibilidade de {uptime_pct:.1f}% com latência média de resposta de {avg_rtt_ms:.1f} ms no Gateway Dragino. "
            f"Sinal Wi-Fi aferido em {avg_rssi_dbm:.0f} dBm. Sistema operando dentro dos parâmetros de confiabilidade estabelecidos para a telemetria avícola."
        )

    prompt = f"""
Você é o Engenheiro Chefe de Telecomunicações e Infraestrutura de TI da C.Vale.
Analise os dados consolidados da sonda de conectividade nos últimos {days} dias e emita o parecer técnico oficial de engenharia (máximo de 3 parágrafos concisos):

DADOS TÉCNICOS:
- Ponto / Granja: {location_name} (ID: {device_id})
- Hardware: {hardware_model}
- Período: Últimos {days} dias ({total_telemetries} batimentos analisados)
- Disponibilidade Registrada: {uptime_pct:.1f}%
- Gateway Local (Dragino): IP {lan_target_ip or 'WAN-Only'} (MAC: {lan_target_mac or 'N/A'})
- Latência Média ICMP: {avg_rtt_ms:.1f} ms (Pico: {max_rtt_ms:.1f} ms)
- Nível de Sinal Wi-Fi: {avg_rssi_dbm:.0f} dBm
- Incidentes Registrados: {incident_count}

DIRETRIZES DE REDAÇÃO:
1. Escreva como um engenheiro humano especialista em redes rurais e automação avícola da C.Vale.
2. NUNCA mencione inteligência artificial, IA, Gemini, modelo de linguagem, robô ou Google. O texto deve soar 100% como uma análise técnica humana corporativa oficial.
3. Estruture em 3 parágrafos:
   - Diagnóstico do Enlace & Estabilidade: Avaliação da latência, sinal Wi-Fi e qualidade do link.
   - Impacto na Operação e Ração: Impacto na confiabilidade da transmissão dos dados de nível dos silos e confirmação de pedidos no TMS.
   - Recomendações Técnicas: Ações preventivas recomendadas para a equipe de suporte e campo.

Tom: Estritamente profissional, técnico, executivo e assertivo em português PT-BR.
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
            "temperature": 0.25,
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
        print(f"[Telecom Engine] {e}")

    return (
        f"Avaliação técnica do período de {days} dias para a unidade '{location_name}': "
        f"O enlace registrou índice de disponibilidade de {uptime_pct:.1f}% com latência média de resposta de {avg_rtt_ms:.1f} ms no Gateway Dragino. "
        f"Foram registrados {incident_count} incidentes de oscilação no período com sinal Wi-Fi médio em {avg_rssi_dbm:.0f} dBm."
    )
