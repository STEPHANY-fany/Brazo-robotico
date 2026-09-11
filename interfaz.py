import pygame
import math
import sys

from prueba import brazoRobotico

ANCHO = 760
ALTO = 540

FPS = 60

FONDO = "fondo.png"
OBJETIVO = "objeto.png"
MURO = "muri.png"


BASE_X = 145
BASE_Y = 455

ESCALA = 55
OBJETIVO_P1 = (5.0, 4.0)
OBJETIVO_P2 = (5.0, 4.0)

OBJETIVO_P3 = (7.0, 2.0)

MURO_X = 4.5
MURO_Y_MIN = 0.0
MURO_Y_MAX = 5.0

AMARILLO = (255, 170, 20)
AMARILLO_CLARO = (255, 195, 45)

NEGRO = (20, 20, 20)

CIAN = (0, 210, 255)

BLANCO = (245, 245, 245)

def mundo_a_pantalla(x, y):

    px = BASE_X + x * ESCALA
    py = BASE_Y - y * ESCALA

    return int(px), int(py)
def cargar_imagen(nombre, tamaño=None, transparente=False):

    try:

        imagen = pygame.image.load(
            nombre
        ).convert_alpha()

        
        if transparente:

            imagen.set_colorkey(
                (255, 255, 255)
            )

        if tamaño is not None:

            imagen = pygame.transform.smoothscale(
                imagen,
                tamaño
            )

        return imagen

    except pygame.error as error:

        print(
            f"No se pudo cargar {nombre}: {error}"
        )

        return None


def obtener_objetivo(problema):

    if problema == 1:

        return OBJETIVO_P1

    elif problema == 2:

        return OBJETIVO_P2

    elif problema == 3:

        return OBJETIVO_P3

    return OBJETIVO_P1

def dibujar_objetivo(
    pantalla,
    imagen,
    problema
):

    objetivo_x, objetivo_y = obtener_objetivo(
        problema
    )

    px, py = mundo_a_pantalla(
        objetivo_x,
        objetivo_y
    )

    if imagen is not None:

        rect = imagen.get_rect(
            center=(px, py)
        )

        pantalla.blit(
            imagen,
            rect
        )

    else:

        pygame.draw.circle(
            pantalla,
            CIAN,
            (px, py),
            30
        )

def dibujar_muro(
    pantalla,
    imagen
):

    x = MURO_X

    y_medio = (
        MURO_Y_MIN + MURO_Y_MAX
    ) / 2

    px, py = mundo_a_pantalla(
        x,
        y_medio
    )

    ancho = 105

    alto = int(
        (MURO_Y_MAX - MURO_Y_MIN)
        * ESCALA
    )


    if imagen is not None:

        muro = pygame.transform.smoothscale(
            imagen,
            (ancho, alto)
        )

        rect = muro.get_rect(
            center=(px, py)
        )

        pantalla.blit(
            muro,
            rect
        )

    else:
        pygame.draw.rect(
            pantalla,
            (90, 100, 105),
            (
                px - ancho // 2,
                py - alto // 2,
                ancho,
                alto
            )
        )


def dibujar_brazo(
    pantalla,
    algoritmo,
    individuo
):

    puntos = algoritmo.Cinematica(
        individuo,
        devolver_puntos=True
    )


    puntos_pantalla = []


    for x, y in puntos:

        px, py = mundo_a_pantalla(
            x,
            y
        )

        puntos_pantalla.append(
            (px, py)
        )

    for i in range(
        len(puntos_pantalla) - 1
    ):

        inicio = puntos_pantalla[i]

        final = puntos_pantalla[i + 1]


        pygame.draw.line(
            pantalla,
            NEGRO,
            inicio,
            final,
            22
        )


        pygame.draw.line(
            pantalla,
            AMARILLO,
            inicio,
            final,
            15
        )

    for punto in puntos_pantalla:

        pygame.draw.circle(
            pantalla,
            NEGRO,
            punto,
            17
        )

        pygame.draw.circle(
            pantalla,
            AMARILLO_CLARO,
            punto,
            12
        )

        pygame.draw.circle(
            pantalla,
            NEGRO,
            punto,
            5
        )

    base_x, base_y = puntos_pantalla[0]


    pygame.draw.rect(
        pantalla,
        NEGRO,
        (
            base_x - 75,
            base_y - 5,
            150,
            35
        ),
        border_radius=4
    )


    pygame.draw.rect(
        pantalla,
        AMARILLO,
        (
            base_x - 70,
            base_y,
            140,
            25
        ),
        border_radius=3
    )

def dibujar_informacion(
    pantalla,
    fuente_titulo,
    fuente,
    problema,
    metodo,
    generacion,
    fitness,
    individuo
):

    panel = pygame.Surface(
        (255, 225),
        pygame.SRCALPHA
    )

    panel.fill(
        (5, 20, 35, 215)
    )

    pantalla.blit(
        panel,
        (15, 15)
    )

    if problema == 1:

        nombre = "Alcanzar"

    elif problema == 2:

        nombre = "Esquivar"

    else:

        nombre = "Menor movimiento"


    titulo = fuente_titulo.render(
        nombre,
        True,
        CIAN
    )

    pantalla.blit(
        titulo,
        (25, 25)
    )


    for i in range(4):

        grados = math.degrees(
            individuo[i]
        )

        texto = fuente.render(
            f"θ{i + 1}: {grados:8.2f}°",
            True,
            CIAN
        )

        pantalla.blit(
            texto,
            (25, 57 + i * 24)
        )



    texto = fuente.render(
        f"Fitness: {fitness:.6f}",
        True,
        BLANCO
    )

    pantalla.blit(
        texto,
        (25, 158)
    )


    texto = fuente.render(
        f"Método: {metodo}",
        True,
        BLANCO
    )

    pantalla.blit(
        texto,
        (25, 183)
    )


    texto = fuente.render(
        f"Generación: {generacion}/100",
        True,
        BLANCO
    )

    pantalla.blit(
        texto,
        (25, 207)
    )


def reiniciar_algoritmo(
    algoritmo,
    problema
):

    padres = algoritmo.CrearPoblacion()


    evaluados = algoritmo.EvaluarPoblacion(
        padres,
        problema=problema,
        peso_esfuerzo=0.1
    )


    fitness, individuo = evaluados[0]


    return padres, individuo, fitness


def avanzar_generacion(
    algoritmo,
    padres,
    metodo,
    problema
):

    hijos = algoritmo.CrearHijo(
        padres
    )

    if metodo == "mas":

        nuevos_padres = algoritmo.MutuacionCmasP(
            padres,
            hijos,
            problema=problema,
            peso_esfuerzo=0.1
        )

    else:

        nuevos_padres = algoritmo.MutuacionComa(
            hijos,
            problema=problema,
            peso_esfuerzo=0.1
        )

    evaluados = algoritmo.EvaluarPoblacion(
        nuevos_padres,
        problema=problema,
        peso_esfuerzo=0.1
    )


    fitness, individuo = evaluados[0]


    return nuevos_padres, individuo, fitness

def main():

    pygame.init()


    pantalla = pygame.display.set_mode(
        (ANCHO, ALTO)
    )


    pygame.display.set_caption(
        "Brazo Robótico "
    )


    reloj = pygame.time.Clock()


    
    fuente = pygame.font.SysFont(
        "Arial",
        15
    )


    fuente_titulo = pygame.font.SysFont(
        "Arial",
        17,
        bold=True
    )


    
    fondo = cargar_imagen(
        FONDO,
        (ANCHO, ALTO)
    )


    objetivo = cargar_imagen(
        OBJETIVO,
        (85, 85)
    )


  
    muro = cargar_imagen(
        MURO,
        transparente=True
    )


    

    algoritmo = brazoRobotico()


    problema = 1


    metodo = "mas"

    nombre_metodo = "(μ + λ)"



    padres, mejor_individuo, fitness = (
        reiniciar_algoritmo(
            algoritmo,
            problema
        )
    )



    generacion = 1



    tiempo = 0

    DURACION_GENERACION = 0.7


    pausado = False

    ejecutando = True


    while ejecutando:

        dt = reloj.tick(
            FPS
        ) / 1000.0

        for evento in pygame.event.get():

            if evento.type == pygame.QUIT:

                ejecutando = False


            if evento.type == pygame.KEYDOWN:

                if evento.key == pygame.K_SPACE:

                    pausado = not pausado

                elif evento.key == pygame.K_1:

                    problema = 1

                    (
                        padres,
                        mejor_individuo,
                        fitness
                    ) = reiniciar_algoritmo(
                        algoritmo,
                        problema
                    )

                    generacion = 1


             

                elif evento.key == pygame.K_2:

                    problema = 2

                    (
                        padres,
                        mejor_individuo,
                        fitness
                    ) = reiniciar_algoritmo(
                        algoritmo,
                        problema
                    )

                    generacion = 1


               

                elif evento.key == pygame.K_3:

                    problema = 3

                    (
                        padres,
                        mejor_individuo,
                        fitness
                    ) = reiniciar_algoritmo(
                        algoritmo,
                        problema
                    )

                    generacion = 1

                elif evento.key == pygame.K_TAB:

                    if metodo == "mas":

                        metodo = "coma"

                        nombre_metodo = "(μ , λ)"

                    else:

                        metodo = "mas"

                        nombre_metodo = "(μ + λ)"


                    # Reiniciar para comparar
                    (
                        padres,
                        mejor_individuo,
                        fitness
                    ) = reiniciar_algoritmo(
                        algoritmo,
                        problema
                    )


                    generacion = 1


               

                elif evento.key == pygame.K_r:

                    (
                        padres,
                        mejor_individuo,
                        fitness
                    ) = reiniciar_algoritmo(
                        algoritmo,
                        problema
                    )


                    generacion = 1



        if not pausado:

            tiempo += dt


            if tiempo >= DURACION_GENERACION:

                tiempo = 0


                if generacion < 100:

                    (
                        padres,
                        mejor_individuo,
                        fitness
                    ) = avanzar_generacion(
                        algoritmo,
                        padres,
                        metodo,
                        problema
                    )


                    generacion += 1



        if fondo:

            pantalla.blit(
                fondo,
                (0, 0)
            )

        else:

            pantalla.fill(
                (10, 15, 20)
            )



        if problema == 2:

            dibujar_muro(
                pantalla,
                muro
            )


        
        dibujar_objetivo(
            pantalla,
            objetivo,
            problema
        )


     
        dibujar_brazo(
            pantalla,
            algoritmo,
            mejor_individuo
        )


        dibujar_informacion(
            pantalla,
            fuente_titulo,
            fuente,
            problema,
            nombre_metodo,
            generacion,
            fitness,
            mejor_individuo
        )


        
        pygame.display.flip()


    pygame.quit()

    sys.exit()



if __name__ == "__main__":

    main()
# IRONEDIT:1789099341:ux23ii402:a8eb73d4623ff77004db5ae53b10d49c930d0dcc5d4a59ee3edd0ba793033b88
