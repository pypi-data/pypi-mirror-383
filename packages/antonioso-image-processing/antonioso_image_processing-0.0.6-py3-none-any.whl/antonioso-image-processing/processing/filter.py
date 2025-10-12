import cv2
import numpy as np

def filtro_media(imagem, size=3):
    """
    Aplica um filtro da média (blur) em uma imagem.

    Parâmetros:
        imagem (numpy.ndarray): imagem de entrada (BGR ou grayscale)
        size (int): tamanho do kernel (deve ser ímpar, ex: 3, 5, 7)

    Retorna:
        numpy.ndarray: imagem filtrada
    """
    # Verifica se o tamanho é ímpar
    if size % 2 == 0:
        raise ValueError("O tamanho do kernel deve ser ímpar (ex: 3, 5, 7).")

    # Cria o kernel da média
    kernel = np.ones((size, size), np.float32) / (size ** 2)

    # Aplica o filtro de convolução
    imagem_filtrada = cv2.filter2D(imagem, -1, kernel)

    return imagem_filtrada
