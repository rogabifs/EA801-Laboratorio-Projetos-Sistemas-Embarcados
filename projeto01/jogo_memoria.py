import machine # Comunicação com o Raspberry 
import utime # Biblioteca padrão de tempo
import neopixel # Controle dos Leds
import random # Geração de aleatoriedade
import ssd1306  # Comunicação com o OLED
import time 

# --- Configurações para a execução no BitDogLab  ---
# Matriz de LEDs e Buzzer
np = neopixel.NeoPixel(machine.Pin(7), 25)  # Inicializa a matriz de 25 LEDs endereçáveis (NeoPixels) conectada ao pino GPIO 7 (Pino dedica à matriz de LEDs).

buzzer = machine.PWM(machine.Pin(21)) # Configura o pino 21 como saída PWM para controlar a frequência sonora do buzzer.

# Botões (Pull-up interno: 0 = Pressionado, 1 = Solto)
btn_a = machine.Pin(10, machine.Pin.IN, machine.Pin.PULL_UP) # VERDE
btn_b = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_UP)  # VERMELHO
btn_c = machine.Pin(6, machine.Pin.IN, machine.Pin.PULL_UP)  # AZUL

# Configuração do Display OLED SSD1306 (I2C1)
# SDA(Serial Data) = GP2, SCL (Serial Clock) = GP3
i2c = machine.I2C(1, scl=machine.Pin(3), sda=machine.Pin(2))
# Inicializa o display OLED de 128x64 no endereço 0x3C.
display = ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)

# Definição de Cores (RGB)
RED = (50, 0, 0)
BLUE = (0, 0, 50)
GREEN = (0, 50, 0)
OFF = (0, 0, 0)

def atualizar_oled(nivel, status="JOGANDO"):
    """
    Atualiza as informações exibidas no display OLED SSD1306.
    """
    # Limpa toda a tela (preenche com a cor 0 - preto)
    display.fill(0)
    
    # Escreve o título do jogo na coordenada x=15, y=0 (topo)
    display.text("BITDOGLAB MEMORY", 0, 0, 1)
    
    # Desenha uma linha separadora usando 15 caracteres "-"
    display.text("-" * 15, 5, 12, 1)
    
    # Exibe o nível atual da sequência (centralizado verticalmente)
    display.text(f"NIVEL: {nivel}", 30, 30, 1)
    
    # Exibe o status do jogo (ex: "JOGANDO", "ERROU!", "SUA VEZ")
    display.text(status, 25, 50, 1)
    
    # Envia todos os dados do buffer para o hardware do display (renderiza)
    display.show()


def tocar_som(freq, duracao):

    # Verifica se a frequência é válida (maior que zero) para evitar erro no PWM
    if freq > 0:
        # Define a nota musical alterando a velocidade da oscilação (frequência)
        buzzer.freq(freq)
        
        # Define o duty cycle em 3000 (de 65535). 
        # Isso "aciona" o som com um volume moderado.
        buzzer.duty_u16(3000)
    
    # Mantém o som tocando pelo tempo determinado na variável 'duracao'
    utime.sleep_ms(duracao)
    
    # Define o duty cycle como 0 para silenciar o buzzer após o tempo acabar
    buzzer.duty_u16(0)


def mostrar_cor(indice, tempo=400):
    """
    Acende a matriz de LEDs com uma cor e toca uma nota musical simultaneamente.
    :param indice: 0 para Vermelho, 1 para Azul, 2 para Verde.
    :param tempo: Duração do sinal em milissegundos.
    """
    # Define a cor (RGB) e a frequência (Hz) baseada no índice recebido
    if indice == 0: # Caso seja 0 (Botão B): Vermelho e Nota Lá (440Hz)
        cor, freq = RED, 440
    elif indice == 1: # Caso seja 1 (Botão C): Azul e Nota Si (494Hz)
        cor, freq = BLUE, 494
    else: # Caso seja 2 (Botão A): Verde e Nota Dó (523Hz)
        cor, freq = GREEN, 523

    # Preenche o buffer de todos os 25 LEDs da matriz com a cor selecionada
    for i in range(25): 
        np[i] = cor
    
    # Envia os dados do buffer para a matriz física para acender os LEDs
    np.write()
    
    # Chama a função de som para tocar a nota durante o tempo definido
    tocar_som(freq, tempo)
    
    # Após o tempo passar, prepara o buffer para desligar todos os LEDs (OFF)
    for i in range(25): 
        np[i] = OFF
    
    # Atualiza a matriz física para apagar as luzes
    np.write()
    
    # Pequena pausa entre cores para que o jogador perceba a separação na sequência
    utime.sleep_ms(150)


def esperar_jogada():
    """
    Bloqueia a execução do programa até que um dos três botões seja pressionado.
    Retorna o índice correspondente ao botão pressionado.
    """
    while True:
        # Verifica se o Botão B (Vermelho) foi pressionado (leitura 0 devido ao Pull-up)
        if btn_b.value() == 0: 
            utime.sleep_ms(200) # Debounce: evita que um único clique seja lido várias vezes
            return 0            # Retorna o índice 0 e encerra a função
            
        # Verifica se o Botão C (Azul) foi pressionado
        if btn_c.value() == 0: 
            utime.sleep_ms(200) # Pausa para estabilização mecânica do contato
            return 1            # Retorna o índice 1
            
        # Verifica se o Botão A (Verde) foi pressionado
        if btn_a.value() == 0: 
            utime.sleep_ms(200) # Debounce para garantir um clique limpo
            return 2            # Retorna o índice 2
            
        # Pequena pausa de 10ms para não sobrecarregar o processador durante o loop
        utime.sleep_ms(10)
        
        
def irriga():
    print("sdsdfsdfs 1")
    rele = machine.Pin(8, machine.Pin.OUT)
    sensor = machine.Pin(4, machine.Pin.IN)

    # Estado inicial do relé
    rele.value(1) # 1 equivale a HIGH
    sensor.value(1)
    print("sdsdfsdfs")

    # Loop principal (Equivalente ao loop)
    while True:
        print("sdsdfsdfs")
        irrigar = sensor.value() # Lê o valor digital do sensor (1 ou 0)
        
        if irrigar:
            rele.value(0) # 0 equivale a LOW
        else:
            rele.value(1) # 1 equivale a HIGH
            
        time.sleep_ms(500) # Pausa de 500 milissegundos


def iniciar_jogo():
    print("asdasda 0")
    irriga()
    """
    Controla o fluxo principal do jogo: gera a sequência, exibe-a e 
    gerencia os turnos do jogador.
    """
    # Lista vazia que armazenará a sequência de cores do jogo
    sequencia = []
    
    while True:
        # Adiciona um novo número aleatório (0, 1 ou 2) ao final da sequência
        sequencia.append(random.randint(0, 2))
        
        # Calcula o nível atual baseado na quantidade de itens na lista
        nivel_atual = len(sequencia)
        
        # Atualiza o display OLED avisando que a sequência será mostrada
        atualizar_oled(nivel_atual, "OLHE A MATRIZ")
        
        # Aguarda 1 segundo para o jogador se preparar
        utime.sleep(1)
        
        # --- TURNO DO COMPUTADOR: Mostra a sequência atual ---
        for cor_id in sequencia:
            # Acende os LEDs e toca o som correspondente a cada item da lista
            mostrar_cor(cor_id)
        
        # --- TURNO DO JOGADOR ---
        # Atualiza o display informando que é a vez do usuário repetir
        atualizar_oled(nivel_atual, "SUA VEZ!")

        
        # Turno do jogador
        for correto in sequencia:
            jogada = esperar_jogada()
            mostrar_cor(jogada, 200)
            
            if jogada != correto:
                atualizar_oled(nivel_atual, "GAME OVER!")
                # Sinal de erro (Vermelho pisca)
                for _ in range(3):
                    for i in range(25): np[i] = RED
                    np.write()
                    tocar_som(150, 150)
                    for i in range(25): np[i] = OFF
                    np.write()
                    utime.sleep_ms(100)
                utime.sleep(2)
                return # Reinicia do zero

        utime.sleep(0.5)

# Início do programa
if __name__ == "__main__":
    atualizar_oled(0, "START!")
    utime.sleep(1)
    while True:
        iniciar_jogo()

