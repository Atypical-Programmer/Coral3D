import os
from tqdm import tqdm
import numpy as np
import cv2

def func(img, depth=1, blue_tint=0.2):
    
    def color_attenuation(img, depth):
        attenuation = np.array([0.9, 0.8 * depth, 0.6 * depth])
        attenuated = img * attenuation
        return np.clip(attenuated, 0, 255).astype(np.uint8)
    
    def add_particles(image, num_particles=2000, particle_size_range=(1, 8), brightness_range=(200, 255)):
        h, w = image.shape[:2]
        particles_layer = np.zeros((h, w), dtype=np.uint8)        
        for _ in range(num_particles):
            x = np.random.randint(0, w)
            y = np.random.randint(0, h)
            size = np.random.randint(particle_size_range[0], particle_size_range[1])
            brightness = np.random.randint(brightness_range[0], brightness_range[1])
            cv2.circle(particles_layer, (x, y), size, brightness, -1)        
        particles_layer = cv2.GaussianBlur(particles_layer, (5, 5), 0)        
        particles_colored = cv2.merge([particles_layer] * 3)
        particles_overlay = cv2.addWeighted(image, 1.0, particles_colored, 0.2, 0)        
        return particles_overlay    
    
    def add_haze(img, intensity=0.8):
        haze = cv2.GaussianBlur(img, (15, 15), 3)
        return cv2.addWeighted(img, 1 - intensity, haze, intensity, 0)
    
    def create_vignette(image, strength=0.5):
        rows, cols = image.shape[:2]
        kernel_x = cv2.getGaussianKernel(cols, cols)
        kernel_y = cv2.getGaussianKernel(rows, rows)
        kernel = kernel_y * kernel_x.T
        mask = 255 * kernel / np.linalg.norm(kernel)
        vignette = np.copy(image)
        for i in range(3):
            vignette[:,:,i] = vignette[:,:,i] * (1 - strength * (1 - mask / 255))
        return vignette
    
    img = color_attenuation(img, depth)    
    blue_channel = img[:,:,0]
    img[:,:,0] = np.clip(blue_channel + blue_channel * blue_tint, 0, 255).astype(np.uint8)
    img = add_haze(img)
    img = add_particles(img)
    
    return img


if __name__ == "__main__":

    source_dir = './data4coral/images'
    target_dir = './data4coral/images_color'

    if not os.path.exists(target_dir):
        os.mkdir(target_dir)

    for img_path in tqdm(os.listdir(source_dir)):
        img = cv2.imread(os.path.join(source_dir, img_path))
        img = func(img)
        cv2.imwrite(os.path.join(target_dir, img_path), img)