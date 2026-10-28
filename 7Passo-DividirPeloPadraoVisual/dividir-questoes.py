from PIL import Image
import os

def cor_parecida(pixel, cor_alvo, tolerancia=15):
    """
    Verifica se a cor do pixel está dentro da tolerância aceitável
    """
    if len(pixel) == 4:  # RGBA
        r, g, b, a = pixel
    else:  # RGB
        r, g, b = pixel[:3]
        
    return (abs(r - cor_alvo[0]) <= tolerancia and 
            abs(g - cor_alvo[1]) <= tolerancia and 
            abs(b - cor_alvo[2]) <= tolerancia)

def encontrar_padrao_visual(imagem, tolerancia_cor=15):
    """
    Procura o padrão vertical específico no último pixel da direita.
    Padrão:
    - 3px (35, 31, 32)     -> margem +-2 (1 a 5 px)
    - 3px (255, 255, 255)  -> margem +-2 (1 a 5 px)
    - 3px (35, 31, 32)     -> margem +-2 (1 a 5 px)
    - 8px (64, 193, 243)   -> margem +-2 (6 a 10 px)
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    y = 0
    # Precisamos de pelo menos 1+1+1+6 = 9 pixels de altura mínima para o padrão
    while y < altura - 9:
        y_atual = y
        x_pixel = largura - 1  # Último pixel da direita
        
        # Faixa 1: (35, 31, 32) | 1 a 5 pixels
        cont1 = 0
        while y_atual < altura and cor_parecida(pixels[x_pixel, y_atual], (35, 31, 32), tolerancia_cor):
            cont1 += 1
            y_atual += 1
        if not (1 <= cont1 <= 5):
            y += 1
            continue
            
        # Faixa 2: (255, 255, 255) | 1 a 5 pixels
        cont2 = 0
        while y_atual < altura and cor_parecida(pixels[x_pixel, y_atual], (255, 255, 255), tolerancia_cor):
            cont2 += 1
            y_atual += 1
        if not (1 <= cont2 <= 5):
            y += 1
            continue
            
        # Faixa 3: (35, 31, 32) | 1 a 5 pixels
        cont3 = 0
        while y_atual < altura and cor_parecida(pixels[x_pixel, y_atual], (35, 31, 32), tolerancia_cor):
            cont3 += 1
            y_atual += 1
        if not (1 <= cont3 <= 5):
            y += 1
            continue
            
        # Faixa 4: (64, 193, 243) | 6 a 10 pixels
        cont4 = 0
        while y_atual < altura and cor_parecida(pixels[x_pixel, y_atual], (64, 193, 243), tolerancia_cor):
            cont4 += 1
            y_atual += 1
        if not (6 <= cont4 <= 10):
            y += 1
            continue
            
        # Se passou por todas as verificações, o padrão foi encontrado!
        posicao_corte = y - 17  # Corta 17 pixels antes de iniciar o padrão
        
        if posicao_corte < 0:
            posicao_corte = 0
            
        posicoes_corte.append(posicao_corte)
        print(f"Padrão encontrado iniciando em y={y} (Tamanhos: {cont1}, {cont2}, {cont3}, {cont4}), cortando em y={posicao_corte}")
        
        # Pula toda a extensão do padrão encontrado para evitar detecções sobrepostas
        y = y_atual

    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida):
    """
    Divide a imagem verticalmente cortando ANTES dos padrões visuais
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    # Encontra as posições do padrão
    posicoes_corte = encontrar_padrao_visual(imagem)
    
    if not posicoes_corte:
        print("Nenhum padrão visual encontrado na imagem!")
        return
    
    print(f"Encontrados {len(posicoes_corte)} padrões para corte")
    
    os.makedirs(pasta_saida, exist_ok=True)
    
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
        
        # A próxima seção começa exatamente onde esta foi cortada (para não perder os 6px)
        posicao_anterior = posicao_corte
    
    # Corta a seção final (após o último padrão visual encontrado)
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

    # Executa a divisão
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida)
    
    print("Divisão concluída!")