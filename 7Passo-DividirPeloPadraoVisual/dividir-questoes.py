from PIL import Image
import os

def encontrar_padrao_visual(imagem, tolerancia_cor=15):
    """
    Encontra as posições percorrendo o último pixel da direita de cima para baixo.
    Procura a sequência exata de cores e tamanhos (com margem de erro de +/- 2px).
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    # Função auxiliar para verificar se a cor do pixel bate com a cor alvo
    def cor_combina(pixel, cor_alvo):
        if len(pixel) == 4:  # RGBA
            r, g, b, a = pixel
        else:  # RGB
            r, g, b = pixel[:3]
        return (abs(r - cor_alvo[0]) <= tolerancia_cor and 
                abs(g - cor_alvo[1]) <= tolerancia_cor and 
                abs(b - cor_alvo[2]) <= tolerancia_cor)

    # Função auxiliar para contar quantos pixels seguidos têm a mesma cor
    def contar_pixels(y_start, cor_alvo, max_h):
        h = 0
        # largura - 1 é o último pixel da direita
        while y_start + h < altura and h <= max_h and cor_combina(pixels[largura-1, y_start + h], cor_alvo):
            h += 1
        return h

    y = 0
    while y < altura:
        # 1ª Faixa: 9px (margem 7 a 11) - RGB (35, 31, 32)
        h1 = contar_pixels(y, (35, 31, 32), 11)
        if 7 <= h1 <= 11:
            y2 = y + h1
            # 2ª Faixa: 4px (margem 2 a 6) - RGB (255, 255, 255)
            h2 = contar_pixels(y2, (255, 255, 255), 6)
            if 2 <= h2 <= 6:
                y3 = y2 + h2
                # 3ª Faixa: 5px (margem 3 a 7) - RGB (35, 31, 32)
                h3 = contar_pixels(y3, (35, 31, 32), 7)
                if 3 <= h3 <= 7:
                    y4 = y3 + h3
                    # 4ª Faixa: 4px (margem 2 a 6) - RGB (255, 255, 255)
                    h4 = contar_pixels(y4, (255, 255, 255), 6)
                    if 2 <= h4 <= 6:
                        y5 = y4 + h4
                        # 5ª Faixa: 99px (margem 97 a 101) - RGB (35, 31, 32)
                        h5 = contar_pixels(y5, (35, 31, 32), 101)
                        if 7 <= h5 <= 11:
                            
                            # Padrão completo encontrado! Cortar 10 pixels ANTES do início do padrão
                            posicao_corte = y - 10
                            if posicao_corte < 0:
                                posicao_corte = 0
                                
                            posicoes_corte.append(posicao_corte)
                            print(f"Padrão encontrado iniciando em y={y}. Ponto de corte: y={posicao_corte}")
                            
                            # Pula o padrão inteiro para não detectar o mesmo bloco novamente
                            y = y5 + h5
                            continue
        y += 1
    
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida):
    """
    Divide a imagem verticalmente cortando ANTES dos padrões visuais identificados
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    # Encontra as posições dos padrões
    posicoes_corte = encontrar_padrao_visual(imagem)
    
    if not posicoes_corte:
        print("Nenhum padrão visual encontrado na imagem!")
        return
    
    print(f"Encontrados {len(posicoes_corte)} pontos de corte")
    
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        if posicao_corte <= posicao_anterior:
            continue
            
        # Corta a seção
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        # A próxima imagem começa exatamente no corte atual para manter os 10px no topo
        posicao_anterior = posicao_corte 
    
    # Salva a última parte (após o último corte até o fim da imagem)
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
    
    # Executa a divisão
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida)
    
    print("Divisão concluída!")