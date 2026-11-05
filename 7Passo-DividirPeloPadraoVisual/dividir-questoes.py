from PIL import Image
import os

def cor_proxima(pixel, cor_alvo, tolerancia=15):
    """
    Verifica se a cor do pixel está dentro da tolerância da cor alvo.
    """
    if len(pixel) == 4:  # RGBA
        r, g, b, a = pixel
    else:  # RGB
        r, g, b = pixel[:3]
        
    return (abs(r - cor_alvo[0]) <= tolerancia and 
            abs(g - cor_alvo[1]) <= tolerancia and 
            abs(b - cor_alvo[2]) <= tolerancia)

def encontrar_padrao_vertical(imagem, tolerancia=15):
    """
    Encontra posições onde há o padrão: 1px branco, 1 a 5px pretos, 1px branco
    no último pixel da direita.
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    # Percorre a imagem de cima para baixo
    y = 0
    # O padrão máximo tem 7 pixels de altura (1 branco + 5 pretos + 1 branco)
    while y < altura - 7:
        # Pega a cor do último pixel da direita
        pixel_atual = pixels[largura - 7, y]
        
        # 1. Verifica se o pixel atual é BRANCO (255, 255, 255)
        if cor_proxima(pixel_atual, (255, 255, 255), tolerancia):
            qtd_preto = 0
            
            # 2. Conta os pixels PRETOS (0, 0, 0) consecutivos logo abaixo
            while (y + 1 + qtd_preto < altura and 
                   cor_proxima(pixels[largura - 7, y + 1 + qtd_preto], (0, 0, 0), tolerancia)):
                qtd_preto += 1
            
            # O padrão pede 3px com margem de 2px (ou seja, de 1 a 5 pixels pretos)
            if 1 <= qtd_preto <= 5:
                pixel_fim = pixels[largura - 7, y + 1 + qtd_preto]
                
                # 3. Verifica se o pixel logo após os pretos é BRANCO (255, 255, 255)
                if cor_proxima(pixel_fim, (255, 255, 255), tolerancia):
                    
                    # Corta 24 pixels ANTES de começar o padrão
                    posicao_corte = y - 24
                    if posicao_corte < 0:
                        posicao_corte = 0
                        
                    posicoes_corte.append(posicao_corte)
                    print(f"Padrão encontrado começando em y={y}, cortando em y={posicao_corte}")
                    
                    # Pula o padrão recém-encontrado para não detectá-lo novamente
                    y += 1 + qtd_preto + 1
                    continue
                    
        y += 1
    
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida):
    """
    Divide a imagem verticalmente usando o padrão definido
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    posicoes_corte = encontrar_padrao_vertical(imagem)
    
    if not posicoes_corte:
        print("Nenhum padrão encontrado na imagem!")
        return
    
    print(f"Encontrados {len(posicoes_corte)} pontos de corte")
    
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        # Ignora cortes redundantes ou inválidos
        if posicao_corte <= posicao_anterior:
            continue
            
        # Corta a seção anterior até a marca de 24px antes do padrão
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        # A próxima questão começa EXATAMENTE onde parou (mantendo os 24px no início da próxima imagem)
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
    caminho_imagem = "colunas_concatenadas_verticalmente.png"  
    pasta_saida = "questoes" 
    
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida)
    
    print("Divisão concluída!")