"""
Propósito: Dividir as questões por padrão visual.
Atualização: Busca de padrão tripartite com margem de tolerância em pixels.
"""

from PIL import Image
import os

def cor_dentro_da_tolerancia(pixel, cor_alvo, tolerancia=15):
    """Verifica se o pixel está dentro da margem de erro da cor alvo"""
    if len(pixel) >= 3:
        r, g, b = pixel[:3]
        return (abs(r - cor_alvo[0]) <= tolerancia and 
                abs(g - cor_alvo[1]) <= tolerancia and 
                abs(b - cor_alvo[2]) <= tolerancia)
    return False

def encontrar_padrao_questoes(imagem, tolerancia_cor=15):
    """
    Procura o padrão:
    - 4px (±3) da cor (35, 31, 32)
    - 17px (±3) da cor (189, 188, 188)
    - 4px (±3) da cor (35, 31, 32)
    no último pixel da direita.
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    cor_preta = (35, 31, 32)
    cor_cinza = (189, 188, 188)
    
    y = 0
    while y < altura:
        # Pega o último pixel da direita
        pixel = pixels[largura - 2, y]
        
        # Início potencial do padrão (Faixa 1)
        if cor_dentro_da_tolerancia(pixel, cor_preta, tolerancia_cor):
            h1 = 0
            # Conta altura da Faixa 1 (esperado 4px, margem 1 a 7)
            while y + h1 < altura and h1 <= 7 and cor_dentro_da_tolerancia(pixels[largura - 2, y + h1], cor_preta, tolerancia_cor):
                h1 += 1
            
            if 1 <= h1 <= 7:
                h2 = 0
                # Conta altura da Faixa 2 (esperado 17px, margem 14 a 20)
                while y + h1 + h2 < altura and h2 <= 20 and cor_dentro_da_tolerancia(pixels[largura - 2, y + h1 + h2], cor_cinza, tolerancia_cor):
                    h2 += 1
                    
                if 14 <= h2 <= 20:
                    h3 = 0
                    # Conta altura da Faixa 3 (esperado 4px, margem 1 a 7)
                    while y + h1 + h2 + h3 < altura and h3 <= 7 and cor_dentro_da_tolerancia(pixels[largura - 2, y + h1 + h2 + h3], cor_preta, tolerancia_cor):
                        h3 += 1
                        
                    if 1 <= h3 <= 7:
                        # Padrão completo encontrado! Corta 12 pixels antes de começar o padrão
                        posicao_corte = y - 12
                        if posicao_corte < 0:
                            posicao_corte = 0
                            
                        posicoes_corte.append(posicao_corte)
                        print(f"Padrão encontrado em y={y} (h1={h1}, h2={h2}, h3={h3}), cortando em y={posicao_corte}")
                        
                        # Pula o bloco inteiro para não re-detectar o mesmo padrão
                        y += (h1 + h2 + h3)
                        continue
        y += 1
        
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida):
    """
    Divide a imagem verticalmente cortando ANTES dos padrões identificados
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    # Encontra as posições com base no novo padrão
    posicoes_corte = encontrar_padrao_questoes(imagem)
    
    if not posicoes_corte:
        print("Nenhum padrão encontrado na imagem!")
        return
    
    print(f"Encontrados {len(posicoes_corte)} locais de corte.")
    
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
        
        # A próxima questão começa EXATAMENTE onde esta terminou 
        # (assim os 12px de folga ficam no início da imagem seguinte)
        posicao_anterior = posicao_corte 
    
    # Corta a última seção da imagem
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "colunas_concatenadas_verticalmente.png"
    pasta_saida = "questao" 
    
    # Executa a divisão diretamente
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida)
    
    print("Divisão concluída!")