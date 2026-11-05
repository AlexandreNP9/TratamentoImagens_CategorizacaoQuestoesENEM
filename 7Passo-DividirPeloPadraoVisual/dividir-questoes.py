"""
Propósito: Dividir as questões por padrão. Observa-se que ao início de cada questão tem uma faixa de alguma cor, que é o padrão de início de cada questão
Autor: Alexandre Nassar de Peder
Criação: 02/10/2025
Atualização: 03/06/2026

OBS1: puxe a imagem "colunas_concatenadas_verticalmente.png" do passo 6 para essa pasta do passo 7
OBS2: puxe a pasta "inteiras" do passo 5 para essa pasta do passo 7
OBS3, OBS4, OBS5, OBS6, OBS7, OBS8: (Mantidas do original, código atualizado para novo padrão)
"""

from PIL import Image
import os

def cor_parecida(pixel, cor_alvo, tolerancia=20):
    """ Verifica se a cor do pixel está dentro da tolerância do RGB alvo """
    if len(pixel) == 4:  # RGBA
        r, g, b, a = pixel
    else:  # RGB
        r, g, b = pixel[:3]
        
    return (abs(r - cor_alvo[0]) <= tolerancia and 
            abs(g - cor_alvo[1]) <= tolerancia and 
            abs(b - cor_alvo[2]) <= tolerancia)

def encontrar_padrao_questoes(imagem, tolerancia_cor=20):
    """
    Percorre o último pixel da direita buscando um dos dois padrões verticais:
    Padrão 1: 4px(35,31,32) -> 7px(255,255,255) -> 10px(189,188,188) -> 4px(35,31,32)
    Padrão 2: 4px(35,31,32) -> 1px(189,188,188) -> 7px(255,255,255) -> 10px(189,188,188) -> 4px(35,31,32)
    Com margem de erro de ±3px em cada faixa de altura.
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    posicoes_corte = []
    
    # Cores do padrão
    c1_preto = (35, 31, 32)
    c2_branco = (255, 255, 255)
    c3_cinza = (189, 188, 188)
    
    # Posição X é o último pixel da direita
    x = largura - 2 
    
    y = 0
    while y < altura:
        px = pixels[x, y]
        
        # Início de um possível padrão (Primeira faixa preta)
        if cor_parecida(px, c1_preto, tolerancia_cor):
            y_inicio_padrao = y
            
            # Conta pixels da primeira faixa preta (Esperado: 4px | Margem: 1 a 7)
            count_preto1 = 0
            while y < altura and cor_parecida(pixels[x, y], c1_preto, tolerancia_cor):
                count_preto1 += 1
                y += 1
                
            if not (1 <= count_preto1 <= 7):
                continue # Fora da margem de erro, recomeça a busca
                
            if y >= altura: break
            
            # Verifica qual é a próxima cor (Branco para Padrão 1, Cinza para Padrão 2)
            px_seguinte = pixels[x, y]
            
            # ========= TENTA PADRÃO 1 =========
            if cor_parecida(px_seguinte, c2_branco, tolerancia_cor):
                # Faixa branca (Esperado: 7px | Margem: 4 a 10)
                count_branco = 0
                while y < altura and cor_parecida(pixels[x, y], c2_branco, tolerancia_cor):
                    count_branco += 1
                    y += 1
                if not (4 <= count_branco <= 10): continue
                
                # Faixa cinza (Esperado: 10px | Margem: 7 a 13)
                count_cinza = 0
                while y < altura and cor_parecida(pixels[x, y], c3_cinza, tolerancia_cor):
                    count_cinza += 1
                    y += 1
                if not (7 <= count_cinza <= 13): continue
                
                # Faixa preta final (Esperado: 4px | Margem: 1 a 7)
                count_preto2 = 0
                while y < altura and cor_parecida(pixels[x, y], c1_preto, tolerancia_cor):
                    count_preto2 += 1
                    y += 1
                if not (1 <= count_preto2 <= 7): continue
                
                # Padrão 1 encontrado! Corta 12 pixels antes do início.
                corte = max(0, y_inicio_padrao - 12)
                posicoes_corte.append((corte, y))
                print(f"Padrão 1 encontrado em y={y_inicio_padrao}, cortando em y={corte}")
                
            # ========= TENTA PADRÃO 2 =========
            elif cor_parecida(px_seguinte, c3_cinza, tolerancia_cor):
                # Faixa cinza fina (Esperado: 1px | Margem: 1 a 4) -> (1-3 <= 0, então mínimo 1)
                count_cinza1 = 0
                while y < altura and cor_parecida(pixels[x, y], c3_cinza, tolerancia_cor):
                    count_cinza1 += 1
                    y += 1
                if not (1 <= count_cinza1 <= 4): continue
                
                # Faixa branca (Esperado: 7px | Margem: 4 a 10)
                count_branco = 0
                while y < altura and cor_parecida(pixels[x, y], c2_branco, tolerancia_cor):
                    count_branco += 1
                    y += 1
                if not (4 <= count_branco <= 10): continue
                
                # Faixa cinza grossa (Esperado: 10px | Margem: 7 a 13)
                count_cinza2 = 0
                while y < altura and cor_parecida(pixels[x, y], c3_cinza, tolerancia_cor):
                    count_cinza2 += 1
                    y += 1
                if not (7 <= count_cinza2 <= 13): continue
                
                # Faixa preta final (Esperado: 4px | Margem: 1 a 7)
                count_preto2 = 0
                while y < altura and cor_parecida(pixels[x, y], c1_preto, tolerancia_cor):
                    count_preto2 += 1
                    y += 1
                if not (1 <= count_preto2 <= 7): continue
                
                # Padrão 2 encontrado! Corta 12 pixels antes do início.
                corte = max(0, y_inicio_padrao - 12)
                posicoes_corte.append((corte, y))
                print(f"Padrão 2 encontrado em y={y_inicio_padrao}, cortando em y={corte}")
            
            else:
                # Se não for nem branco nem cinza, apenas recomeça o loop na nova posição de Y
                pass 
        else:
            y += 1
            
    # Retorna apenas os pontos de corte 
    return [c[0] for c in posicoes_corte]

def dividir_imagem_por_padrao(caminho_imagem, pasta_saida):
    """
    Divide a imagem verticalmente cortando ANTES dos padrões visuais encontrados
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    posicoes_corte = encontrar_padrao_questoes(imagem)
    
    if not posicoes_corte:
        print("Nenhum padrão de questão encontrado na imagem!")
        return
    
    print(f"Encontrados {len(posicoes_corte)} padrões para corte")
    
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        if posicao_corte <= posicao_anterior:
            continue
            
        # Corta do final da última seção até 12 pixels antes do novo padrão
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        # Atualiza a posição anterior para ser onde a nova questão deve começar (no corte atual)
        posicao_anterior = posicao_corte 
    
    # Corta a seção final (após o último corte até o fim da imagem)
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
    
    # Executa a divisão sem necessidade da função antiga de conversão do GIMP
    dividir_imagem_por_padrao(caminho_imagem, pasta_saida)
    
    print("Divisão concluída!")