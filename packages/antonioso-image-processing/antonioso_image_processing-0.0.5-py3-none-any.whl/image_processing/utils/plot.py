import matplotlib.pyplot as plt

def plot_image(image):
    plt.figure(figsize=(12,4))
    plt.imshow(image, ccmap="gray")
    plt.axis("off")
    plt.show()