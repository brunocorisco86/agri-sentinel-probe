from typing import Tuple

STATE_ONLINE = "ONLINE"
STATE_LAN_FAILURE = "LAN_FAILURE"
STATE_WAN_TIMEOUT = "WAN_TIMEOUT"
STATE_BLACKOUT = "BLACKOUT_GENERAL"

def classify_device_state(is_alive: bool, local_target_enabled: bool, local_target_online: bool) -> Tuple[str, str]:
    """
    Classificação determinística da Matriz Booleana de 4 Estados.
    Retorna: (status_code, descricao_diagnostico)
    """
    if not is_alive:
        return STATE_WAN_TIMEOUT, "Queda de Link WAN ou Falha de Energia na Sonda (Sem resposta na VPS)"
        
    if local_target_enabled and not local_target_online:
        return STATE_LAN_FAILURE, "Falha Local do Gateway Dragino (Internet WAN Saudavel)"
        
    return STATE_ONLINE, "100% Operacional (WAN e LAN Saudaveis)"
