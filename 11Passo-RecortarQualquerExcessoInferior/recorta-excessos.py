from PIL import Image
import os
import shutil

def encontrar_borda_inferior(imagem, cor_alvo, tolerancia=15):
    """
    Encontra a faixa de 4px descrita de baixo para cima (apenas na metade inferior).
    Retorna a posição Y onde deve ser feito o corte (acima da faixa) ou None se não encontrar.
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    # Percorre a imagem de baixo para cima, até a metade da imagem
    limite_metade = altura // 2
    
    for y in range(altura - 1, limite_metade + 3, -1):
        faixa_encontrada = True
        
        # Verifica os 4 pixels de altura (y-3 até y)
        for dy in range(4):
            pixel_y = y - dy
            
            # Verifica por toda a largura da imagem
            for x in range(largura):
                pixel = pixels[x, pixel_y]
                
                if len(pixel) >= 4:  # RGBA
                    r, g, b, a = pixel
                else:  # RGB
                    r, g, b = pixel[:3]
                
                # Verifica se a cor está dentro da tolerância
                if (abs(r - cor_alvo[0]) > tolerancia or 
                    abs(g - cor_alvo[1]) > tolerancia or 
                    abs(b - cor_alvo[2]) > tolerancia):
                    faixa_encontrada = False
                    break # Interrompe o x imediatamente se não for a cor alvo
            
            if not faixa_encontrada:
                break # Interrompe o dy imediatamente
        
        if faixa_encontrada:
            print(f"Faixa encontrada! Cortando na posição y={y-3}")
            return y - 3  # Retorna a posição acima da faixa de 4px
    
    return None

def processar_imagens(pasta_origem, pasta_destino, cor_alvo):
    """
    Processa todas as imagens da pasta origem, recortando as que têm faixa inferior
    e copiando todas para a pasta destino
    """
    # Cria a pasta de destino se não existir
    os.makedirs(pasta_destino, exist_ok=True)
    
    # Lista todos os arquivos da pasta origem
    arquivos = [f for f in os.listdir(pasta_origem) 
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
    
    print(f"Encontrados {len(arquivos)} arquivos para processar")
    
    for arquivo in arquivos:
        caminho_origem = os.path.join(pasta_origem, arquivo)
        caminho_destino = os.path.join(pasta_destino, arquivo)
        
        try:
            # Abre a imagem
            with Image.open(caminho_origem) as imagem:
                print(f"\nProcessando: {arquivo} ({imagem.width}x{imagem.height})")
                
                # Procura pela faixa inferior
                posicao_corte = encontrar_borda_inferior(imagem, cor_alvo)
                
                if posicao_corte is not None and posicao_corte > 0:
                    # Se encontrou a faixa, recorta a imagem
                    area_corte = (0, 0, imagem.width, posicao_corte)
                    imagem_recortada = imagem.crop(area_corte)
                    imagem_recortada.save(caminho_destino)
                    print(f"✓ Imagem recortada: {imagem_recortada.width}x{imagem_recortada.height}")
                else:
                    # Se não encontrou faixa, copia a imagem original
                    shutil.copy2(caminho_origem, caminho_destino)
                    print(f"✓ Imagem mantida original (sem faixa detectada)")
                    
        except Exception as e:
            print(f"✗ Erro ao processar {arquivo}: {e}")
            # Tenta copiar o arquivo mesmo com erro
            try:
                shutil.copy2(caminho_origem, caminho_destino)
                print(f"✓ Arquivo copiado mesmo com erro")
            except:
                print(f"✗ Não foi possível copiar o arquivo")

# Função principal
if __name__ == "__main__":
    # Configurações
    pasta_origem = "./questoes"
    pasta_destino = "finalizadas"
    cor_alvo = (35, 31, 32)  # Cor da faixa conforme nova regra
    
    print("Iniciando processamento de imagens...")
    print(f"Pasta origem: {pasta_origem}")
    print(f"Pasta destino: {pasta_destino}")
    print(f"Cor alvo: RGB{cor_alvo}")
    
    # Verifica se a pasta origem existe
    if not os.path.exists(pasta_origem):
        print(f"Erro: A pasta '{pasta_origem}' não existe!")
        exit(1)
    
    # Executa o processamento
    processar_imagens(pasta_origem, pasta_destino, cor_alvo)
    
    print("\n" + "="*50)
    print("Processamento concluído!")
    print(f"Todas as imagens foram salvas em: {pasta_destino}")