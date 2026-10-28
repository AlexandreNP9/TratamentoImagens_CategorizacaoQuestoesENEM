from PIL import Image
import os

def encontrar_padrao_visual(imagem, cor_alvo, tolerancia_cor=15, altura_esperada=29, margem_erro=3): 
    """
    Encontra posições onde há um padrão visual da cor especificada
    na faixa de pixels horizontais de 1000 a 1030.
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    altura_min = altura_esperada - margem_erro
    altura_max = altura_esperada + margem_erro
    
    # Percorre a imagem de cima para baixo
    y = 0
    while y < altura:
        altura_atual = 0
        
        # Conta a altura consecutiva de linhas que combinam com o padrão
        while y + altura_atual < altura:
            linha_valida = True
            
            # Percorre a faixa horizontal dos pixels 1000 ao 1030
            for x in range(1000, 1031):
                # Evita erro se a imagem for menor que 1030 de largura
                if x >= largura:
                    continue
                    
                pixel = pixels[x, y + altura_atual]
                
                if len(pixel) == 4:  # RGBA
                    r, g, b, a = pixel
                else:  # RGB
                    r, g, b = pixel[:3]
                
                # Verifica se a cor está dentro da tolerância
                if (abs(r - cor_alvo[0]) > tolerancia_cor or 
                    abs(g - cor_alvo[1]) > tolerancia_cor or 
                    abs(b - cor_alvo[2]) > tolerancia_cor):
                    linha_valida = False
                    break # Sai do loop do 'x' se um pixel falhar
            
            if linha_valida:
                altura_atual += 1
            else:
                break # Sai do loop da 'altura' se a linha não for toda válida
        
        # Se a faixa contínua encontrada estiver dentro da margem de erro
        if altura_min <= altura_atual <= altura_max:
            # Corta 6 pixels ANTES do padrão começar
            posicao_corte = y - 6
            if posicao_corte < 0:  
                posicao_corte = 0
                
            posicoes_corte.append(posicao_corte)
            print(f"Padrão encontrado começando em y={y} (altura: {altura_atual}px), cortando em y={posicao_corte}")
            
            # Pula a altura encontrada para não repetir detecção
            y += altura_atual
        else:
            # Avança o loop. Se encontrou uma linha ou mais válidas (mas fora da margem), pula elas.
            if altura_atual > 0:
                y += altura_atual
            else:
                y += 1
    
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_alvo):
    # Abre a imagem
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    # Encontra as posições dos padrões
    posicoes_corte = encontrar_padrao_visual(imagem, cor_alvo)
    
    if not posicoes_corte:
        print("Nenhum padrão visual encontrado na imagem!")
        return
    
    print(f"Encontrados {len(posicoes_corte)} padrões para corte")
    
    # Cria a pasta de saída se não existir
    os.makedirs(pasta_saida, exist_ok=True)
    
    # Corta as seções da imagem
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        # Garantir que a posição de corte é válida e evitar cortes vazios
        if posicao_corte <= posicao_anterior:
            continue
            
        # Corta a seção (do início anterior até a nova posição de corte)
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        # Salva a imagem cortada
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        # ATUALIZAÇÃO CRUCIAL: A próxima seção começa exatamente de onde cortamos.
        # Assim, os 6 pixels mantidos no corte ficarão no TOPO da próxima imagem.
        posicao_anterior = posicao_corte
    
    # Corta a seção final (após o último corte)
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "colunas_concatenadas_verticalmente.png"  # Substitua pelo caminho da sua imagem
    pasta_saida = "divididas" # Substitua pelo nome da pasta de saída desejada

    # Passando diretamente a cor RGB solicitada
    cor_do_padrao = (222, 221, 222)
    print(f"Cor alvo: RGB{cor_do_padrao}")
    
    # Executa a divisão
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_do_padrao)
    
    print("Divisão concluída!")