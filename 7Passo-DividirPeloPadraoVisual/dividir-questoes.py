from PIL import Image
import os

def encontrar_faixa_preta(imagem, cor_alvo=(0,0,0), tolerancia=15):
    """
    Encontra posições onde há uma faixa horizontal preta respeitando
    a largura, altura e margens de erro informadas.
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    # A faixa original é de x=7 a x=346. 
    # Com margem de +/- 3px (esquerda/direita), verificamos a "área segura" de x=10 a x=343
    x_inicio = 10
    x_fim = 313
    
    y = 0
    # Evita que a leitura ultrapasse o limite inferior da imagem
    while y < altura - 8: 
        
        linhas_pretas_consecutivas = 0
        
        # Verifica até 9 linhas para cobrir a altura de 5px + margem de 3px (máx 8px)
        for dy in range(9):
            if y + dy >= altura:
                break
                
            linha_eh_preta = True
            
            # Percorre a largura da faixa para garantir que é toda preta
            for x in range(x_inicio, x_fim + 1):
                pixel = pixels[x, y + dy]
                
                # Suporta imagens RGBA e RGB
                if len(pixel) == 4:
                    r, g, b, a = pixel
                else:
                    r, g, b = pixel[:3]
                
                # Verifica se a cor está dentro da tolerância do RGB alvo
                if (abs(r - cor_alvo[0]) > tolerancia or 
                    abs(g - cor_alvo[1]) > tolerancia or 
                    abs(b - cor_alvo[2]) > tolerancia):
                    linha_eh_preta = False
                    break
            
            if linha_eh_preta:
                linhas_pretas_consecutivas += 1
            else:
                break # A faixa preta acabou nesta linha
                
        # Valida se a altura encontrada atende a margem de erro (5px +/- 3px = de 2 a 8 pixels)
        if 2 <= linhas_pretas_consecutivas <= 8:
            # Corta 49 pixels ANTES da faixa preta
            posicao_corte = y - 49
            if posicao_corte < 0:
                posicao_corte = 0
                
            posicoes_corte.append(posicao_corte)
            print(f"Padrão encontrado em y={y} (altura {linhas_pretas_consecutivas}px), cortando em y={posicao_corte}")
            
            # Pula a faixa inteira + os 49 pixels para evitar detecções duplicadas no mesmo bloco
            y += linhas_pretas_consecutivas + 49
        else:
            y += 1
    
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_alvo):
    """
    Divide a imagem verticalmente com base nas posições de corte encontradas
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    # Encontra as posições de corte usando a nova lógica
    posicoes_corte = encontrar_faixa_preta(imagem, cor_alvo)
    
    if not posicoes_corte:
        print("Nenhuma faixa padrão encontrada na imagem!")
        return
    
    print(f"Encontradas {len(posicoes_corte)} faixas para corte")
    
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        if posicao_corte <= posicao_anterior:
            continue
            
        # Corta a seção do ponto anterior até o novo ponto de corte
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        # A próxima imagem começa EXATAMENTE onde essa terminou
        # (Isso garante que os 49px e a faixa fiquem no topo da nova imagem)
        posicao_anterior = posicao_corte 
    
    # Corta a última seção (do último corte até o final da imagem)
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "paginas_concatenadas_verticalmente.png"  # Substitua se necessário
    pasta_saida = "questoes"                                   # Substitua se necessário

    # A cor alvo agora é Preto RGB (0, 0, 0)
    cor_do_padrao = (0, 0, 0)
    print(f"Cor alvo definida: RGB{cor_do_padrao}")
    
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_do_padrao)
    
    print("Divisão concluída!")