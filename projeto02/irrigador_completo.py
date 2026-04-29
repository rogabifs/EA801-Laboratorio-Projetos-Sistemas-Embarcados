from machine import Pin, I2C, PWM
import utime
import neopixel
import ssd1306

# ==========================================
# CONFIGURAÇÃO DE HARDWARE
# ==========================================

# 1. Atuador e Sensor
rele_bomba = Pin(8, Pin.OUT)
sensor_umidade = Pin(4, Pin.IN)

# 2. Botões de Interface
btn_verde = Pin(10, Pin.IN, Pin.PULL_UP)   # Botão A - Pausar/Retomar Sistema
btn_vermelho = Pin(5, Pin.IN, Pin.PULL_UP) # Botão B - Forçar Rega Manual

# 3. Feedbacks (Visual e Sonoro)
buzzer = PWM(Pin(21))
buzzer.duty_u16(0) # Garante que inicie desligado

np = neopixel.NeoPixel(Pin(7), 25) # Matriz de 25 LEDs

# Configuração do I2C1 para o Display OLED (Pinos 2 e 3)
i2c = I2C(1, scl=Pin(3), sda=Pin(2))
display = ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)

# Cores para a Matriz (R, G, B)
COR_REGANDO = (0, 0, 50)    # Azul
COR_UMIDO = (0, 50, 0)      # Verde
COR_PAUSADO = (30, 20, 0)   # Laranja/Amarelo
COR_OFF = (0, 0, 0)

# ==========================================
# FUNÇÕES DE INTERFACE
# ==========================================

def tocar_beep(frequencia, duracao):
    """Gera um feedback sonoro rápido para botões ou alertas."""
    if frequencia > 0:
        buzzer.freq(frequencia)
        buzzer.duty_u16(2000) # Volume moderado
    utime.sleep_ms(duracao)
    buzzer.duty_u16(0)

def atualizar_matriz(cor):
    """Pinta toda a matriz NeoPixel de uma vez."""
    for i in range(25):
        np[i] = cor
    np.write()

def atualizar_tela(status_solo, bomba_ligada, sistema_ativo, rega_manual):
    """Renderiza todas as informações de telemetria no Display OLED."""
    display.fill(0)
    
    # Cabeçalho
    display.text("IRRIGADOR", 12, 0, 1)
    display.text("-" * 15, 4, 10, 1)
    
    # Status do Sistema
    estado_sys = "ON" if sistema_ativo else "PAUSADO"
    display.text(f"Sistema: {estado_sys}", 0, 25, 1)
    
    # Status Físico
    display.text(f"Solo: {status_solo}", 0, 40, 1)
    
    # Indicadores Inferiores
    if bomba_ligada:
        display.text(">> BOMBA ON <<", 12, 55, 1)
    elif rega_manual:
        display.text("[MODO MANUAL]", 12, 55, 1)
        
    display.show()

# ==========================================
# ESTADO INICIAL
# ==========================================
# 0 Desliga o transistor -> Relé desliga a bomba
rele_bomba.value(0) 

sistema_ativo = True
rega_manual = False

ultimo_teste_tempo = 0
intervalo_teste = 2000 # Lê o sensor a cada 2 segundos (2000 ms)

atualizar_tela("Iniciando...", False, sistema_ativo, rega_manual)
tocar_beep(523, 300) # Dó

# ==========================================
# LOOP PRINCIPAL
# ==========================================
while True:
    agora = utime.ticks_ms()
    
    # --- 1. LEITURA DOS BOTÕES (INTERFACE DO USUÁRIO) ---
    
    # Botão Verde: Alterna entre Sistema Automático Ligado / Pausado
    if btn_verde.value() == 0:
        sistema_ativo = not sistema_ativo
        tocar_beep(800 if sistema_ativo else 400, 150) # Som agudo pra ligar, grave pra pausar
        utime.sleep_ms(300) # Debounce
        
    # Botão Vermelho: Força a bomba a ligar independente do sensor
    if btn_vermelho.value() == 0:
        rega_manual = not rega_manual
        tocar_beep(1200, 100)
        utime.sleep_ms(300)

    # --- 2. CONTROLE DE IRRIGAÇÃO (TEMPORIZADO) ---
    
    # Só executa a leitura física a cada 2 segundos
    if utime.ticks_diff(agora, ultimo_teste_tempo) > intervalo_teste:
        ultimo_teste_tempo = agora
        
        # Se o sistema foi pausado pelo usuário
        if not sistema_ativo:
            rele_bomba.value(0) # Garante bomba desligada
            atualizar_matriz(COR_PAUSADO)
            atualizar_tela("STANDBY", False, sistema_ativo, rega_manual)
            
        # Se o sistema está operando
        else:
            irrigar = sensor_umidade.value() # 1 = Seco, 0 = Úmido
            status_texto = "SECO" if irrigar == 1 else "UMIDO"
            
            # A bomba liga se o sensor pedir OU se o usuário apertou rega manual
            if irrigar == 1 or rega_manual:
                rele_bomba.value(1) # Aciona Transistor -> Liga Bomba
                atualizar_matriz(COR_REGANDO)
                atualizar_tela(status_texto, True, sistema_ativo, rega_manual)
                
                # Bipe curtinho para avisar que a água está correndo
                tocar_beep(1500, 50) 
            else:
                rele_bomba.value(0) # Corta Transistor -> Desliga Bomba
                atualizar_matriz(COR_UMIDO)
                atualizar_tela(status_texto, False, sistema_ativo, rega_manual)

    # Pequena pausa apenas para não superaquecer a CPU no loop infinito
    utime.sleep_ms(50)