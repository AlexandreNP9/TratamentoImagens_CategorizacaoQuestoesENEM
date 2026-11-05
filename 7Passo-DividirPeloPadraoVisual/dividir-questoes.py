from PIL import Image
import os

def encontrar_padrao_vertical(imagem, tolerancia=15):
    """
    Encontra posições onde há o padrão vertical específico no último pixel da direita.
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    # Define a sequência do padrão: (Cor RGB, Altura esperada em pixels)
    padroes = [
        ((35, 31, 32), 9),
        ((255, 255, 255), 5),
        ((35, 31, 32), 4),
        ((255, 255, 255), 5),
        ((35, 31, 32), 9)
    ]
    
    def cor_parecida(pixel, cor_alvo):
        # Extrai RGB ignorando Alpha se houver
        if len(pixel) == 4: r, g, b, _ = pixel
        else: r, g, b = pixel[:3]
        
        return (abs(r - cor_alvo[0]) <= tolerancia and 
                abs(g - cor_alvo[1]) <= tolerancia and 
                abs(b - cor_alvo[2]) <= tolerancia)

    # Percorre a imagem de cima para baixo
    y = 0
    while y < altura:
        y_atual = y
        padrao_encontrado = True
        
        # Verifica cada uma das faixas do padrão sequencialmente
        for cor_alvo, altura_esperada in padroes:
            min_alt = max(1, altura_esperada - 3) # Margem de erro de -3px
            max_alt = altura_esperada + 3         # Margem de erro de +3px
            
            contagem = 0
            
            # Conta quantos pixels seguidos batem com a cor alvo (no último pixel da direita: largura - 1)
            while y_atual < altura and cor_parecida(pixels[largura-10, y_atual], cor_alvo):
                contagem += 1
                y_atual += 1
                if contagem > max_alt:
                    break # Interrompe se a faixa for maior que o limite máximo
            
            # Se a faixa lida não estiver dentro da margem de tolerância de altura
            if not (min_alt <= contagem <= max_alt):
                padrao_encontrado = False
                break
        
        if padrao_encontrado:
            # Corta 10 pixels ANTES do padrão começar
            posicao_corte = y - 10
            if posicao_corte < 0:  # Evitar posições negativas
                posicao_corte = 0
                
            posicoes_corte.append(posicao_corte)
            print(f"Padrão encontrado começando em y={y}, cortando em y={posicao_corte}")
            
            # Pula todo o padrão lido para continuar a busca a partir de onde ele terminou
            y = y_atual
        else:
            # Se não encontrou, desce apenas 1 pixel e tenta novamente
            y += 1
    
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida):
    """
    Divide a imagem verticalmente cortando ANTES das faixas
    """
    # Abre a imagem
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    # Encontra as posições com base no novo padrão
    posicoes_corte = encontrar_padrao_vertical(imagem)
    
    if not posicoes_corte:
        print("Nenhum padrão encontrado na imagem!")
        return
    
    print(f"Encontrados {len(posicoes_corte)} padrões para corte")
    
    # Cria a pasta de saída se não existir
    os.makedirs(pasta_saida, exist_ok=True)
    
    # Corta as seções da imagem
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        # Garantir que a posição de corte é válida (ignora se o corte for no topo extremo)
        if posicao_corte <= posicao_anterior:
            continue
            
        # Corta a seção
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        # Salva a imagem cortada
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        # A próxima seção começa EXATAMENTE onde esta terminou 
        # (assim os 10px e o padrão permanecem no início da próxima imagem)
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
    caminho_imagem = "colunas_concatenadas_verticalmente.png"  
    pasta_saida = "questoes" 

    # Executa a divisão (as cores agora estão fixadas dentro da própria função de busca)
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida)
    
    print("Divisão concluída!")