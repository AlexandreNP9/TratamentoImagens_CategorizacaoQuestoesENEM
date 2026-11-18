"""
Propósito: remover as bordas externas das páginas
Autor: Alexandre Nassar de Peder
Criação: 02/10/2025
Atualização: 03/06/2026

OBS1: puxe a pasta "imagens-convertidas" do passo 1 para essa pasta do passo 2

OBS2: abra a imagem no GIMP e conte pixels para saber quanto de borda tem que cortar.

OBS3: atualize a linha 33 com os valores corretos de corte (esquerda, superior, direita, inferior)

OBS4: tenha em mente desde já que você vai usar as imagens futuramente, então corte pensando na melhor maneira para executar todos os 12 passos

OBS5: execute o código, e abra as imagens para conferir se as bordas foram removidas corretamente. Se não, ajuste os valores de corte e execute novamente.
"""

from PIL import Image
import os

pasta_imagens = "imagens-convertidas"
pasta_saida = "sem-bordas-externas"

os.makedirs(pasta_saida, exist_ok=True)

for nome_arquivo in os.listdir(pasta_imagens):
    if nome_arquivo.lower().endswith(".png"):
        caminho_entrada = os.path.join(pasta_imagens, nome_arquivo)
        imagem = Image.open(caminho_entrada)

        largura, altura = imagem.size
        
        # Extrai o número do nome do arquivo (ex: "pagina_enem_10.png" -> "10" -> 10)
        numero_pagina = int(nome_arquivo.split('_')[2].split('.')[0])

        # Verifica se a página é ímpar ou par para definir a caixa de corte
        if numero_pagina % 2 != 0:
            # Caixa de corte para páginas ÍMPARES
            caixa_corte = (260, 390, largura - 280, altura - 280)
        else:
            # Caixa de corte para páginas PARES
            caixa_corte = (280, 390, largura - 260, altura - 280)

        imagem_cortada = imagem.crop(caixa_corte)

        caminho_saida = os.path.join(pasta_saida, nome_arquivo)
        imagem_cortada.save(caminho_saida)

print("Recorte das bordas concluído.")