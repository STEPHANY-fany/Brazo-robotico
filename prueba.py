import math 
import random 
import matplotlib.pyplot as plt

class brazoRobotico():
    def __init__(self):
        self.dimension=4
        self.l=[3.0,2.5,2.0,1.5]
        self.mu =15
        self.lam=100 
        self.generaciones = 100
        self.sigma = 0.6
        self.limite_min = math.radians(-180)
        self.limite_max = math.radians (180)
   
    def Aptitud(self,theta,problema=1,peso_esfuerzo=0.1):
        px,py = self.Cinematica(theta)
        if problema ==1:
            objetivo_x, objetivo_y= 5.0,4.0
            return math.sqrt ((px-objetivo_x) ** 2 + (py - objetivo_y) **2)
        if problema==2: 
            objetivo_x,objetivo_y = 5.0, 4.0
            distancia = math.sqrt((px - objetivo_x) ** 2 + (py - objetivo_y) ** 2)
            if self.CruzaMuro (theta):
                distancia +=1000
            return distancia 

            
        if problema ==3:
            objetivo_x, objetivo_y = 7.0, 2.0 
            distancia = math.sqrt((px - objetivo_x) **2 + (py - objetivo_y) **2 )
            esfuerzo = sum(abs (t) for t in theta)
            return distancia + peso_esfuerzo * esfuerzo
        raise ValueError("El problema debe ser 1,2 o 3")

    def Cinematica(self,theta,devolver_puntos=False):
        x=0
        y=0
        angulo_acomulado =0.0
        puntos=[(0.0,0.0)]
        for i in range (4):
            angulo_acomulado += theta[i]
            x += self.l[i] * math.cos(angulo_acomulado)
            y += self.l[i] * math.sin(angulo_acomulado)
            puntos.append((x,y))
        if devolver_puntos:
           return puntos 
        return x,y 

    def CruzaMuro(self, theta):
        puntos = self.Cinematica(theta,devolver_puntos=True)
        muro_x = 4.5
        muro_y_min = 0.0
        muro_y_max = 5.0
        muestras = 100
        for i in range (4): 
            x1, y1 = puntos [i]
            x2, y2 = puntos [i + 1 ]
            for j in range (muestras + 1 ):
                t = j / muestras 
                x = x1 + t * (x2-x1)
                y= y1 + t * (y2 - y1)
                if abs (x - muro_x) <= 0.02 and muro_y_min <= y <= muro_y_max:
                    return True 
        return False 

    def CrearIndividuo(self): 
        return [
            random.uniform(self.limite_min,self.limite_max)
            for _ in range (4)
         ]

    def CrearPoblacion(self):
        return [self.CrearIndividuo() for _ in range(self.mu)]

    def Mutar(self, padre):
        hijo= []
        for angulo in padre:
            nuevo_angulo = angulo + random.gauss(0,self.sigma) 
            nuevo_angulo = max(self.limite_min, min(self.limite_max , nuevo_angulo))
            hijo.append (nuevo_angulo)
        return hijo
        

    def CrearHijo(self,padres): 
        hijos = []
        for _ in range(self.lam):
            padre = random.choice(padres)
            hijo = self.Mutar(padre)
            hijos.append(hijo)
        return hijos

    def EvaluarPoblacion(self, poblacion , problema, peso_esfuerzo):
        evaluados = []

        for individuo in poblacion:
            fitness = self.Aptitud(individuo,problema,peso_esfuerzo)
            evaluados.append( (fitness, individuo))

        evaluados.sort(key=lambda x: x[0])
        return evaluados

    def MutuacionCmasP(self, padres, hijos, problema, peso_esfuerzo):
        candidatos = hijos + padres
        evaluados = self.EvaluarPoblacion(candidatos, problema ,peso_esfuerzo)
        nuevos_padres = [individuo [:] for _, individuo in evaluados [: self.mu]]
        return nuevos_padres

    def MutuacionComa (self, hijos, problema, peso_esfuerzo):
        evaluados = self.EvaluarPoblacion(hijos,problema,peso_esfuerzo)
        nuevos_padres = [individuo [:] for _, individuo in evaluados[:self.mu]]
        return nuevos_padres

    def Central(self,problema=1, metodo = "mas",peso_esfuerzo = 0.1, semilla = None):
        if semilla is not None:
            random.seed(semilla)
        padres=self.CrearPoblacion()
        historial = []
        mejor_global = None 
        mejor_global_fitness = float ("inf")
        for generacion in range (self.generaciones):
            hijos = self.CrearHijo(padres)
            if metodo == "mas":
                padres = self.MutuacionCmasP(padres,hijos,problema,peso_esfuerzo)
            elif metodo == "coma":
                padres = self.MutuacionComa(hijos,problema,peso_esfuerzo)
            else:
                raise ValueError("agrega un metodo realll")

            evaluados= self.EvaluarPoblacion(padres, problema, peso_esfuerzo)
            mejor_fitness, mejor_individuo = evaluados [0]
            historial.append(mejor_fitness)
            if mejor_fitness < mejor_global_fitness:
                mejor_global_fitness = mejor_fitness
                mejor_global = mejor_individuo [:]
            print (f"Generacion {generacion + 1:3d} | "f"metodo {metodo:4s} | mejor aptitud = {mejor_fitness:.6f}")
        return mejor_global, mejor_global_fitness, historial

    def EvaluarMutuaciones(self,problema =1, peso_esfuerzo=0.1, semilla = 10):
        print ("mutuacion mu mas landa")
        mejor_mas, fitness_mas, historial_mas = self.Central(problema = problema, metodo= "mas", peso_esfuerzo = peso_esfuerzo, semilla=semilla)
        mejor_coma, fitness_coma, historial_coma = self.Central(problema = problema, metodo= "coma", peso_esfuerzo= peso_esfuerzo, semilla = semilla)
        print("mutuacion mu + lambda")
        print("Genoma angulos:", [round(math.degrees(t),2) for t in mejor_mas])
        print("Mejor aptitu:", fitness_mas)
        
        print("/n mutuacion mu coma lambda")
        print("Mejor fitness :", fitness_coma)
        print("Genoma angulos: " , [round(math.degrees(t),2) for t in mejor_coma])
        self.Graficar(historial_mas,historial_coma,problema)
        return { "mas":{ "mejor":mejor_mas, "fitness":fitness_mas,"historial":historial_mas},"coma":{"mejor":mejor_coma,"fitness":fitness_coma,"historial": historial_coma}}
   
    def Graficar(self,historial_mas, historial_coma,problema):
        generaciones = range(1, self.generaciones + 1)
        plt.figure(figsize= (10, 5))
        plt.plot(generaciones,historial_mas, label = "(mu + lambda)")
        plt.plot(generaciones, historial_coma, label = "(mu , lambda)")
        plt.xlabel("Generacion")
        plt.ylabel ("Mejor Aptitud")
        plt.title (f"curva de convergencia problema {problema}")
        plt.legend()
        plt.grid(alpha = 0.3)
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    algoritmo = brazoRobotico()
    resultados = algoritmo.EvaluarMutuaciones(problema=3, peso_esfuerzo =0.1, semilla= 10)
        
      
        
            





   


        
# IRONEDIT:1789095512:ux23ii402:676b8ae0cafd85f9f0c18bbf2e32b8a55d9291a3651c2e563ddd8289b5511d9e
