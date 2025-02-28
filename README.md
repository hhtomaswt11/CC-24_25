# Comunicações Por Computador - Universidade do Minho 

(Ano letivo 2024/2025)

#### Média dos Trabalhos Práticos: 16.5/20.0  ★

Estes dois trabalhos foram desenvolvidos por [Tomás Melo (A104529)](https://github.com/hhtomaswt11), [José Vasconcelos (A100763)](https://github.com/josevasconcelos2002) e [João Serrão (A104444)](https://github.com/Joao-Serrao), durante o 1º semestre do 3º ano da licenciatura em Engenharia Informática. 

## Trabalho Prático Nº1 – Protocolos da Camada de Transporte
### Avaliação: 18.1/20.0 ★

#### Objetivo 

1. Familiarizar com ferramentas que serão utilizadas ao longo do curso, CORE, Wireshark e seus recursos.
2. Testar a conectividade e analisar as características gerais dos links (ligações com diferentes larguras de banda, diferentes atrasos e perdas de pacotes) utilizando os comandos “ping”, “traceroute” e “iperf”;
3. Realizar a transferência de ficheiros entre dispositivos com protocolos que se utilizam de diferentes protocolos de transporte e analisar o seu uso em condições de rede.

Este trabalho foi dividido em três partes:
1. **Instalação, configuração e validação da rede de testes**
2. **Uso da camada de transporte por parte das aplicações**
3. **Utilização de serviços de transferência de ficheiro no ambiente CORE.**

## Trabalho Prático Nº2 – Monitorização Distribuída de Redes
### Avaliação: 16.2/20.0 ★

#### Objetivo

Este trabalho tem como objetivo o desenvolvimento de um sistema de gestão de redes (Network Monitoring System – NMS) capaz de fornecer informação detalhada sobre o estado dos links e dos dispositivos numa rede, bem como gerar alertas caso sejam detetadas anomalias. Este sistema deverá ser desenvolvido como uma aplicação distribuída com base num modelo cliente-servidor onde uma aplicação cliente (NMS_Agent) é responsável por recolher diferentes métricas de interesse e de as reportar a um servidor centralizado (NMS_Server). Dois protocolos aplicacionais deverão ser desenvolvidos para permitir uma eficiente troca de mensagens entre o NMS_Agent e o NSM_Server, nomeadamente:
1. **NetTask** *(utilizando UDP)* para a comunicação de tarefas e a coleta contínua de métricas.
2. **AlertFlow** *(utilizando TCP)* para notificação de alterações críticas no estado dos dispositivos de rede.

Em suma, este trabalho visa familiarizar os alunos com o desenvolvimento de protocolos aplicacionais e a utilização de sockets para comunicação em rede, explorando a resiliência e robustez de soluções distribuídas. O NMS proposto é levemente inspirado no protocolo “NetFlow”.


#### Setup ⚙️

Ecolher/criar uma topologia no emulador CORE 7.5 e abrir o terminal de cada um dos PCs (utilizar a topologia CC-Topo-2024 como padrão).

No terminal do PC visto como servidor, executar:
```text
python3 server_main.py <storage_path> <json_file_path>
```

Neste terminal são impressas, em tempo real, mensagens que indicam a conclusão de tasks. 

Nos restantes terminais, vistos como clientes, executar: 
```text
python3 client_main.py <device_number> <server_ip>
```

Assim, os clientes são capazes de executar tarefas recebidas do servidor, monitorar métricas e enviar os dados para o servidor. 






