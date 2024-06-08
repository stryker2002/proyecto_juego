import pygame
import random
import os

# Inicialización de Pygame
pygame.init()

# Configuración de la pantalla
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
INFO_PANEL_HEIGHT = 150  # Aumentado para más espacio de información
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT + INFO_PANEL_HEIGHT))
pygame.display.set_caption("Juego de Aventura")

# Definición de colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Fuente para el texto
font = pygame.font.Font(None, 36)

# Definición de clases

class Personaje:
    def __init__(self, nombre, img_personaje, x, y):
        self.nombre = nombre
        self.vida = 100
        self.ataque = 10
        self.defensa = 5
        self.nivel = 1
        self.experiencia = 0
        self.inventario = []
        self.rect = pygame.Rect(x, y, 50, 50)
        self.game_over = False
        self.img_personaje = img_personaje

    def mover(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def atacar(self, enemigo):
        daño = self.ataque - enemigo.defensa
        if daño > 0:
            enemigo.vida -= daño

    def subir_nivel(self):
        self.nivel += 1
        self.ataque += 5
        self.defensa += 3

    def ganar_experiencia(self, cantidad):
        self.experiencia += cantidad
        if self.experiencia >= 100:
            self.experiencia -= 100
            self.subir_nivel()

    def dibujar(self, screen):
        screen.blit(self.img_personaje, self.rect.topleft)

    def mostrar_estadisticas(self, screen):
        stats = [
            f"Vida: {self.vida}",
            f"Ataque: {self.ataque}",
            f"Defensa: {self.defensa}",
            f"Nivel: {self.nivel}",
            f"Experiencia: {self.experiencia}"
        ]
        for i, stat in enumerate(stats):
            text = font.render(stat, True, BLACK)
            screen.blit(text, (10, SCREEN_HEIGHT + 10 + i * 30))

    def verificar_vida(self):
        if self.vida <= 0:
            self.game_over = True

class Enemigo:
    def __init__(self, tipo, x, y, img_enemigo):
        self.tipo = tipo
        self.vida = random.randint(50, 150)
        self.ataque = random.randint(5, 15)
        self.defensa = random.randint(3, 8)
        self.rect = pygame.Rect(x, y, 50, 50)
        self.img_enemigo = img_enemigo

    def atacar(self, personaje):
        daño = self.ataque - personaje.defensa
        if daño > 0:
            personaje.vida -= daño

    def dibujar(self, screen):
        screen.blit(self.img_enemigo, self.rect.topleft)

class Objeto:
    def __init__(self, nombre, tipo, x, y, img_objeto):
        self.nombre = nombre
        self.tipo = tipo
        self.rect = pygame.Rect(x, y, 30, 30)
        self.img_objeto = img_objeto

    def dibujar(self, screen):
        screen.blit(self.img_objeto, self.rect.topleft)

class Juego:
    def __init__(self):
        self.img_personaje = self.cargar_imagen("proyecto_juego/imagenes/cuadro_verde.png", (50, 50))
        self.img_enemigo = self.cargar_imagen("proyecto_juego/imagenes/cuadro_rojo.png", (50, 50))
        self.img_objeto = self.cargar_imagen("proyecto_juego/imagenes/cuadro_azul.png", (30, 30))

        self.personaje = self.generar_personaje()
        self.enemigos = self.generar_enemigos(5, self.img_enemigo)
        self.objetos = self.generar_objetos(6, self.img_objeto)

        self.running = True

    def cargar_imagen(self, ruta, tamaño):
        imagen = pygame.image.load(os.path.join(ruta)).convert_alpha()
        return pygame.transform.scale(imagen, tamaño)

    def generar_posicion_aleatoria(self, ancho, alto):
        x = random.randint(0, SCREEN_WIDTH - ancho)
        y = random.randint(0, SCREEN_HEIGHT - alto)
        return x, y

    def generar_personaje(self):
        x, y = self.generar_posicion_aleatoria(50, 50)
        return Personaje("Héroe", self.img_personaje, x, y)

    def generar_enemigos(self, cantidad, img_enemigo):
        enemigos = []
        while len(enemigos) < cantidad:
            x, y = self.generar_posicion_aleatoria(50, 50)
            nuevo_enemigo = Enemigo("volador", x, y, img_enemigo)
            if not any(enemigo.rect.colliderect(nuevo_enemigo.rect) for enemigo in enemigos) and not nuevo_enemigo.rect.colliderect(self.personaje.rect):
                enemigos.append(nuevo_enemigo)
        return enemigos

    def generar_objetos(self, cantidad, img_objeto):
        return [Objeto("Tesoro", "tesoro", random.randint(0, SCREEN_WIDTH - 30), random.randint(0, SCREEN_HEIGHT - 30), img_objeto) for _ in range(cantidad)]

    def run(self):
        clock = pygame.time.Clock()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.personaje.mover(-5, 0)
            if keys[pygame.K_RIGHT]:
                self.personaje.mover(5, 0)
            if keys[pygame.K_UP]:
                self.personaje.mover(0, -5)
            if keys[pygame.K_DOWN]:
                self.personaje.mover(0, 5)

            screen.fill(WHITE)

            # Dibuja personaje, enemigos y objetos
            if not self.personaje.game_over:
                self.personaje.dibujar(screen)
                for enemigo in self.enemigos:
                    enemigo.dibujar(screen)
                for objeto in self.objetos:
                    objeto.dibujar(screen)

                # Detectar colisiones con enemigos
                for enemigo in self.enemigos:
                    if self.personaje.rect.colliderect(enemigo.rect):
                        self.personaje.atacar(enemigo)
                        enemigo.atacar(self.personaje)
                        if enemigo.vida <= 0:
                            self.enemigos.remove(enemigo)
                            self.personaje.ganar_experiencia(20)

                # Detectar colisiones con objetos
                for objeto in self.objetos:
                    if self.personaje.rect.colliderect(objeto.rect):
                        self.personaje.inventario.append(objeto)
                        self.objetos.remove(objeto)

                # Verificar si se recolectaron todos los objetos
                if len(self.objetos) == 0:
                    self.personaje.subir_nivel()
                    self.personaje.ganar_experiencia(10)
                    self.enemigos = self.generar_enemigos(5 + self.personaje.nivel, self.img_enemigo)
                    self.objetos = self.generar_objetos(6, self.img_objeto)

                self.personaje.verificar_vida()
            else:
                game_over_text = font.render("Game Over", True, BLACK)
                screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))

            # Mostrar estadísticas
            pygame.draw.rect(screen, WHITE, (0, SCREEN_HEIGHT, SCREEN_WIDTH, INFO_PANEL_HEIGHT))
            self.personaje.mostrar_estadisticas(screen)

            pygame.display.flip()
            clock.tick(30)

        pygame.quit()

if __name__ == "__main__":
    juego = Juego()
    juego.run()