# Drone Simulation Project

Este projeto simula o comportamento de um esquadrão de drones em um ambiente de rede, com um drone master e vários drones followers. 

## Configuração e Execução

### Pré-Requisitos
- Python 3
- Mininet-WiFi

### Instruções para Execução

1. **Limpar a Mininet-WiFi:**
   - Para garantir que a Mininet-WiFi esteja limpa antes de iniciar a simulação, execute:
     ```bash
     sudo mn -c
     ```

2. **Executar a Simulação:**
   - Execute o script da simulação com o seguinte comando:
     ```bash
     sudo python3 simulation.py
     ```
   - A senha para o `sudo` é: `wifi`

### Link do Drive

Os arquivos e recursos adicionais para este projeto podem ser encontrados no seguinte link do Google Drive: 
[https://drive.google.com/drive/folders/1ft__26_KDYsyZUrgu5HnC1UXtJ-QlHVr](https://drive.google.com/drive/folders/1ft__26_KDYsyZUrgu5HnC1UXtJ-QlHVr)

## Implementações e Funcionalidades

- **Timeout para Mensagens:** Um timeout foi implementado para controlar o tempo de espera por mensagens dos followers.
- **Panic Mode:** Se o drone master não receber resposta de nenhum follower, ele entra em "panic mode". Nesse modo, o master envia mensagens de pânico para os followers e retorna para o ponto inicial (P1).
- **Reação dos Followers ao Panic Mode:** Se os followers detectarem que o master está em "panic mode" (seja por falta de comunicação ou recebimento de uma mensagem de pânico), eles também retornarão para P1.
- **Retorno Automático dos Followers:** Se os followers pararem de receber mensagens do master, eles retornarão automaticamente para P1.

## Feedbacks e Melhorias

- **Melhoria na Visualização:** A visualização fornecida pelo Matplotlib precisa ser aprimorada para melhor compreensão dos movimentos dos drones.
- **Associação de Mensagens aos Followers:** As mensagens devem indicar claramente qual follower está associado a cada uma delas.
- **Distribuição dos Drones no Espaço:** Evitar enviar todos os drones para o mesmo ponto exato no espaço, promovendo uma distribuição mais realista.

## Simulação Desejada

A simulação idealizada envolve os seguintes passos:
1. Todos os drones começam a se mover em direção ao ponto P2.
2. O drone master entra em "panic mode" no meio do caminho.
3. Os followers percebem que o master não está mais respondendo (por não receberem mais mensagens ou por receberem uma mensagem de pânico) e começam a retornar para o ponto inicial P1.
