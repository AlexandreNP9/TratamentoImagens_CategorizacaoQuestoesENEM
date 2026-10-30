from PIL import Image
import os

def cor_dentro_da_tolerancia(pixel, cor_alvo, tolerancia=15):
    """
    Verifica se a cor do pixel está dentro da tolerância da cor alvo
    """
    if len(pixel) == 4:  # RGBA
        r, g, b, a = pixel
    else:  # RGB
        r, g, b = pixel[:3]
        
    return (abs(r - cor_alvo[0]) <= tolerancia and 
            abs(g - cor_alvo[1]) <= tolerancia and 
            abs(b - cor_alvo[2]) <= tolerancia)

def encontrar_padrao(imagem, tolerancia=15):
    """
    Encontra posições onde há o padrão de 3 faixas consecutivas 
    na última coluna de pixels da direita.
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    y = 0
    ultimo_pixel_x = largura - 1  # Percorrer o último pixel (canto direito)
    
    while y < altura - 40:  # margem de segurança para o tamanho mínimo do padrão
        
        # 1. Verifica a 1ª faixa: ~30px (27 a 33px) da cor RGB (211, 210, 210)
        tam_faixa1 = 0
        while y + tam_faixa1 < altura and cor_dentro_da_tolerancia(pixels[ultimo_pixel_x, y + tam_faixa1], (211, 210, 210), tolerancia):
            tam_faixa1 += 1
            
        if 27 <= tam_faixa1 <= 33:  # 30px com margem de 3px pra mais/menos
            
            # 2. Verifica a 2ª faixa: ~5px (2 a 8px) da cor RGB (255, 255, 255)
            y2 = y + tam_faixa1
            tam_faixa2 = 0
            while y2 + tam_faixa2 < altura and cor_dentro_da_tolerancia(pixels[ultimo_pixel_x, y2 + tam_faixa2], (255, 255, 255), tolerancia):
                tam_faixa2 += 1
                
            if 2 <= tam_faixa2 <= 8:  # 5px com margem de 3px pra mais/menos
                
                # 3. Verifica a 3ª faixa: ~5px (2 a 8px) da cor RGB (35, 31, 32)
                y3 = y2 + tam_faixa2
                tam_faixa3 = 0
                while y3 + tam_faixa3 < altura and cor_dentro_da_tolerancia(pixels[ultimo_pixel_x, y3 + tam_faixa3], (35, 31, 32), tolerancia):
                    tam_faixa3 += 1
                    
                if 2 <= tam_faixa3 <= 8:  # 5px com margem de 3px pra mais/menos
                    
                    # Padrão completo encontrado!
                    posicao_corte = y - 9  # Corta 9px ANTES do padrão começar
                    if posicao_corte < 0:
                        posicao_corte = 0
                        
                    posicoes_corte.append(posicao_corte)
                    print(f"Padrão encontrado começando em y={y}, cortando em y={posicao_corte}")
                    
                    # Pula o padrão inteiro para continuar a busca a partir dali
                    y = y3 + tam_faixa3
                    continue
        
        # Se não encontrou ou não validou a sequência completa, avança apenas 1 pixel e tenta de novo
        y += 1
    
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida):
    """
    Divide a imagem verticalmente cortando ANTES das faixas, sem descartar pixels do meio.
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    # Encontra as posições com base no padrão multi-faixa
    posicoes_corte = encontrar_padrao(imagem)
    
    if not posicoes_corte:
        print("Nenhum padrão encontrado na imagem!")
        return
    
    print(f"Encontrados {len(posicoes_corte)} padrões para corte")
    
    # Cria a pasta de saída se não existir
    os.makedirs(pasta_saida, exist_ok=True)
    
    # Corta as seções da imagem
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        if posicao_corte <= posicao_anterior:
            continue
            
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        # A próxima imagem começa EXATAMENTE no corte atual (para os 9px entrarem no início dela)
        posicao_anterior = posicao_corte
    
    # Corta a seção final (após o último padrão)
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "colunas_concatenadas_verticalmente.png"  # Substitua pelo caminho da sua imagem
    pasta_saida = "questoes"           # Substitua pelo nome da pasta de saída desejada
    
    # Executa a divisão (As cores estão definidas diretamente na função encontrar_padrao)
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida)
    
    print("Divisão concluída!")