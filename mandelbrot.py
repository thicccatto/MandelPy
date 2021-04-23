import time
import multiprocessing
from PIL import Image
import os

class mandelpy():
    
    def __init__(self):
        
        from jsonargparse import ArgumentParser, ActionConfigFile, ActionJsonSchema, typing
        from PIL import Image
        import multiprocessing
        
        parser = ArgumentParser()
        
        parser.add_argument('--cfg', action=ActionConfigFile)
        
        parser.add_argument('--iterations')
        parser.add_argument('--focus')
        parser.add_argument('--size')
        parser.add_argument('--is_video', type=bool)
        parser.add_argument('--framerate', required=False)
        parser.add_argument('--seconds', required=False)
        parser.add_argument('--zoom_factor', required=False)
        
        cfg = parser.parse_args(['--cfg', 'settings.yaml'])
        
        self.cfg = cfg
        
        self.logical_cores = multiprocessing.cpu_count()
        
        self.check_input()
        
        self.focus = complex(self.cfg.focus.real, self.cfg.focus.imaginary)
        self.points = []

        
    def mandel(self, c, it):
        
        z = 0
        for i in range(it):
            if abs(z) > 2.0: break
            z = z * z + c
        return i
    
    def generate_scale(self, zoom, factor=1):
        
        zoom = zoom / factor
        min_x = (-2.0 / 2 ** zoom + self.focus.real)
        max_x = (2.0 / 2 ** zoom + self.focus.real)
        min_y = (-2.0 / 2 ** zoom + self.focus.imag)
        max_y = (2.0 / 2 ** zoom + self.focus.imag)
        
        return min_x, max_x, min_y, max_y
    
    def generate_scaled_coord(self, xy, scale):
        size = (self.cfg.size.x, self.cfg.size.y)
        cx = xy[0] * (scale[1] - scale[0]) / (size[0] - 1) + scale[0]
        cy = xy[1] * (scale[3] - scale[2]) / (size[1] - 1) + scale[2]
        c = complex(cx, cy)
        return c
    
    def generate_colour(self, it):
        
        r = it % 64 * 4
        g = it % 32 * 8
        b = it % 16 * 16
        return (r,g,b)
        
    def multicore_plot(self, scale, points, queue):
        size = (self.cfg.size.x, self.cfg.size.y)
        it = self.cfg.iterations
        cpu_points = []
        while True:
            y = queue.get()
            
            if type(y) != int:
                points.append(cpu_points)
                queue.task_done()
                break
            
            for x in range(size[0]):
                
                c = self.generate_scaled_coord((x,y), scale)
                i = self.mandel(c, it)
                 
                colour = self.generate_colour(i)
                cpu_points.append([(x,y), colour])
            queue.task_done()
            
        print("process complete")
        
    def video_plot(self, queue, output_dir):
        
        from PIL import Image
        it = self.cfg.iterations
        
        while True:
            frame_data = queue.get()
            
            if type(frame_data) != list:
                queue.task_done()
                break
            
            img = Image.new("RGB", (self.cfg.size.x, self.cfg.size.y))
            
            frame_no = frame_data[0]
            zoom_factor = frame_data[1]
            
            scale = self.generate_scale(frame_no, zoom_factor)
            
            for y in range(self.cfg.size.y):
                for x in range(self.cfg.size.x):
                    xy = (x,y)
                    c = self.generate_scaled_coord(xy, scale)
                    i = self.mandel(c, it)
                 
                    colour = self.generate_colour(i)
                    img.putpixel(xy, colour)
                
            img.save(output_dir + str(frame_no).zfill(4) + '.png')
            print("Image processes")
            queue.task_done()
    
    def base_2(self, i):
        
        while i > 2:
            if i % 2 != 0:
                return False
            i /= 2
        return True
    
    def check_input(self):
        
        if type(self.cfg.iterations) != int: raise TypeError("Iterations must be an integer!")
        if type(self.cfg.size.x) != int: raise TypeError("Size x must be an integer!")
        if type(self.cfg.size.y) != int: raise TypeError("Size y must be an integer!")
        
        
        if type(self.cfg.focus.real) != float: raise TypeError("Real Coordinate must be a float!")
        if type(self.cfg.focus.imaginary) != float: raise TypeError("Imaginary Coordinate must be a float!")
        
        if not self.base_2(self.cfg.iterations): raise ValueError("Iterations must be base 2!")
        if not self.base_2(self.cfg.size.x): raise ValueError("Size x must be base 2!")
        if not self.base_2(self.cfg.size.y): raise ValueError("Size y must be base 2!")

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

if __name__ == '__main__':

    current_dir = os.getcwd()
    if not os.path.isdir(current_dir + r"\generated\animation"):
        os.makedirs(current_dir + r"\generated\animation")
        
    if not os.path.isdir(current_dir + r"\generated\images"):
        os.makedirs(current_dir + r"\generated\images")
    mandeler = mandelpy()

    cpu_count = mandeler.logical_cores
    

    manager = multiprocessing.Manager()
    ns = manager.Namespace()
    
    points = manager.list([])
    processes = []
    q = multiprocessing.JoinableQueue()
    
    
    
    if mandeler.cfg.is_video:
        
        
        location = r"\generated\animation"
        datestr = time.strftime('%H-%M-%S %d-%m-%y', time.localtime())
        path = current_dir + location + "\\" + datestr
        os.makedirs(path)
        path += "\\"
        seconds = mandeler.cfg.seconds
        framerate = mandeler.cfg.framerate
        frame_num = seconds * framerate
        zoom_factor = mandeler.cfg.zoom_factor * framerate
        
        for i in range(frame_num):
            q.put([i, zoom_factor])
            
        for x in range(cpu_count):
            q.put("done")
            x = multiprocessing.Process(target=mandeler.video_plot, args=(q,path))
            processes.append(x)
        
        for x in processes:
            x.start()
        
        q.join()
        
    else:
        
        scale = mandeler.generate_scale(0)
        for i in range(mandeler.cfg.size.y):
            q.put(i)
        
        img = Image.new("RGB", (mandeler.cfg.size.x, mandeler.cfg.size.y))

        for i in range(cpu_count):
            q.put('done')
            x = multiprocessing.Process(target=mandeler.multicore_plot, args=(scale, points, q))
            processes.append(x)
        
        for x in processes:
            x.start()
        
        q.join()
        
        print("All processes complete")

        
        for cpu_points in points:
            for point in cpu_points:
                img.putpixel(point[0], point[1])
            
        img.save("mandelbrot.png")
    
    
    