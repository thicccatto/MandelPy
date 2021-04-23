from PIL import Image
import time
xa = -2.0
xb = 1.0
ya = -1.5
yb = 1.5

class timer():
    
    def __init__(self):
        import time
        
    def start(self):
        self.start_time = time.time()
    
    def stop(self):
        self.end_time = time.time()
       
    def evaluate(self):
        time_taken = self.end_time - self.start_time
        return time_taken
    
def generate_coords(imgx, imgy, zoom=1, focus=-1+0j):

    buffer_zone = 2 * (imgx - imgy) / imgy

    zoom = zoom/12

    min_x = ((-2.0 - buffer_zone) / 2 ** zoom + focus.real)
    max_x = ((2.0 + buffer_zone) / 2 ** zoom + focus.real)
    min_y = (-2.0 / 2 ** zoom + focus.imag)
    max_y = (2.0 / 2 ** zoom + focus.imag)

    return min_x, max_x, min_y, max_y




def mandelbrot(imgx, imgy, coords, max_iterations):
    t = timer()
    img = Image.new("RGB", size)
    for y in range(int(imgy)):
        t.start()
        zy = y * (coords[3] - coords[2]) / (imgy - 1) + coords[2]
        for x in range(imgx):
            zx = x * (coords[1] - coords[0]) / (imgx - 1) + coords[0]
            c = complex(zx, zy)
            z = 0
            iterations = 0
            for i in range(max_iterations):
                if abs(z) > 2.0: break
                z = z*z+c

            r = i % 64 * 4
            g = i % 32 * 8
            b = i % 16 * 16
            
            img.putpixel((x,y), (r,g,b))
        t.stop()
        print(str(t.evaluate()))


    
    name = str(focus) + ',' + str(zoom) + ',' + str(max_iterations) + ',' + str(size)
    img.save(name + ".png")
    print("Completed image with coordinates {0}, zoom: {1}".format(focus, zoom))

zoom = 0
focus = 0 + 0j
imgx = 1024
imgy = 1024
size = (imgx, imgy)
max_iterations = 1024
start_time = time.time()
coords = generate_coords(imgx, imgy, zoom, focus)
mandelbrot(imgx, imgy, coords, max_iterations)
end_time = time.time() - start_time
print("Completed in {0} seconds".format(end_time))