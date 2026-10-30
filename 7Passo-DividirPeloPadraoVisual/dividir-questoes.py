from PIL import Image
import os

def conta_pixels_cor(pixels, largura, y_start, altura, cor_alvo, tolerancia=15):
    """
    Conta quantos pixels consecutivos correspondem à cor alvo, 
    olhando apenas o último pixel da direita (largura - 1).
    """
    count = 0
    y = y_start
    while y < altura:
        pixel = pixels[largura-1, y]  # Alterado para o último pixel da direita
        
        if len(pixel) == 4:  # RGBA
            r, g, b, a = pixel
        else:  # RGB
            r, g, b = pixel[:3]
            
        # Verifica se a cor está dentro da tolerância
        if (abs(r - cor_alvo[0]) <= tolerancia and 
            abs(g - cor_alvo[1]) <= tolerancia and 
            abs(b - cor_alvo[2]) <= tolerancia):
            count += 1
            y += 1
        else:
            break
            
    return count

def encontrar_padrao(imagem, tolerancia=15):
    """
    Procura o padrão sequencial de 4 faixas de cores considerando margem de erro de ±3px.
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    y = 0
    
    # O padrão mínimo tem 23 pixels (2 + 17 + 1 + 3).
    while y < altura - 23:
        
        # Faixa 1: 5px de RGB(35,31,32) [Margem ±3: 2 a 8 pixels]
        count1 = conta_pixels_cor(pixels, largura, y, altura, (35, 31, 32), tolerancia)
        if 2 <= count1 <= 8:
            
            # Faixa 2: 20px de RGB(211,210,210) [Margem ±3: 17 a 23 pixels]
            count2 = conta_pixels_cor(pixels, largura, y + count1, altura, (211, 210, 210), tolerancia)
            if 17 <= count2 <= 23:
                
                # Faixa 3: 4px de RGB(35,31,32) [Margem ±3: 1 a 7 pixels]
                count3 = conta_pixels_cor(pixels, largura, y + count1 + count2, altura, (35, 31, 32), tolerancia)
                if 1 <= count3 <= 7:
                    
                    # Faixa 4: 6px de RGB(255,255,255) [Margem ±3: 3 a 9 pixels]
                    count4 = conta_pixels_cor(pixels, largura, y + count1 + count2 + count3, altura, (255, 255, 255), tolerancia)
                    if 3 <= count4 <= 9:
                        
                        # Padrão encontrado! Corta 9 pixels ANTES de começar
                        posicao_corte = y - 9
                        if posicao_corte < 0: 
                            posicao_corte = 0
                            
                        posicoes_corte.append(posicao_corte)
                        print(f"Padrão detectado em y={y}. Ponto de corte estabelecido em y={posicao_corte}")
                        
                        # Pula o padrão inteiro para não detectar o mesmo bloco duas vezes
                        y += (count1 + count2 + count3 + count4)
                        continue
        y += 1
        
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida):
    """
    Divide a imagem verticalmente cortando ANTES dos padrões.
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    posicoes_corte = encontrar_padrao(imagem)
    
    if not posicoes_corte:
        print("Nenhum padrão visual encontrado na imagem!")
        return
    
    print(f"Encontrados {len(posicoes_corte)} padrões para corte")
    
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        if posicao_corte <= posicao_anterior:
            continue
            
        # Corta a seção até a posição do novo corte
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        # O próximo corte iniciará exatamente neste ponto, garantindo que
        # os 9px de segurança fiquem no topo da próxima imagem cortada
        posicao_anterior = posicao_corte
    
    # Salva a última seção da imagem
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "colunas_concatenadas_verticalmente.png"  # Substitua pelo caminho da sua imagem
    pasta_saida = "questoes"           # Substitua pelo nome da pasta de saída
    
    # Executa a divisão diretamente
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida)
    
    print("Divisão concluída!")