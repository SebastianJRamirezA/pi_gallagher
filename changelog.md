# Changelog

Todas las modificaciones notables realizadas en el proyecto **P.I. Gallagher: The Missing Art** están documentadas en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) y el proyecto se adhiere a versionado semántico.

---

## [1.2.0] - 2026-09-18

### Añadido
- **Pantalla de Victoria (`VictoryState`):**
  - Pantalla de desenlace final tras resolver el careo con Sofía en el Museo Del Roscio.
  - Muestra el expediente del caso, veredicto final, estadísticas de investigación (pistas recogidas, combates superados, tiempo) y opciones interactivas para reiniciar la historia o volver al menú principal.
- **Ilustración de Inicio (`logo.png`):**
  - Integración del arte original ilustrado de portada como fondo de la pantalla de bienvenida (`StartState`), con escalado proporcional y placa inferior Art Déco.
- **Sprites Personalizados de NPCs:**
  - Nuevos sprites y animaciones para Lauren, Sofía, el Policía, el Parroquiano, el Canillita, el Desempleado, Morales y el Curador.
  - Lógica de volteo horizontal dinámico (*flip*) según la orientación del personaje en el mapa.
- **Sprites y Animaciones de Guardias en Sigilo:**
  - Hoja de sprites (spritesheet) para los guardias en el minijuego de sigilo con 4 orientaciones de movimiento (abajo, derecha, izquierda volteada y arriba).
- **Combate contra Niko Stieger (Jefe Final):**
  - Implementación del enfrentamiento climático en el sótano del Club Velvet.
  - Patrón de ataque con ráfagas de ametralladora Thompson, persecución activa y embestida (*dash*).
- **Conexión Narrativa y Clímax:**
  - Transición fluida tras resolver la caja fuerte en el Club Velvet: emboscada cinemática de Stieger, combate y entrega de cartas clave (`C09`, `C11`, `C15`, `C16`, `C18`).
  - Retorno al mapa para dirigirse a la oficina, resolver el corcho y culminar en el careo con Sofía.
- **Diseño Sonoro Completo:**
  - Música de fondo para combates (`combat.ogg`), investigación (`investigate.ogg`), mundo abierto (`world.ogg`) y minijuegos (`minigame.ogg`).
  - Efectos de sonido ambientales para pasos de Gallagher y apertura/cierre de puertas en transiciones de área.

### Cambiado
- **Refactorización de `CombatState`:**
  - Desacoplamiento de la lógica de enemigos mediante configuración modular (*EnemyBehavior* / *CombatConfig*), permitiendo múltiples tipos de arenas y oponentes.
- **Dimensiones de NPCs:**
  - Actualización de medidas de cajas de colisión y cuadros de textura en `settings.py` para sincronizar con los nuevos sprites.
- **Flujo de Reinicio de Historia:**
  - Integración en `StoryManager.reset()` para restablecer el inventario de tarjetas, eventos completados y banderas de progreso al iniciar una nueva partida.

### Eliminado
- **Cajas de Colisión Provisionales:**
  - Removidos los rectángulos de depuración rojos (`(255, 0, 0)`) en los métodos de renderizado de `Actor.py` y `Player.py`.

---

## [1.1.0] - 2026-09-17

### Añadido
- **Sistema de Careos e Interrogatorios (`ConfrontationState`):**
  - Mecánica de confrontación con sospechosos (Morales y Sofía) presentando evidencias del inventario.
  - Barra de paciencia/estrés, consecuencias por evidencia errónea y desenlaces ramificados.
- **Efecto Máquina de Escribir (Typewriter):**
  - Efecto de revelación progresiva de texto en cuadros de diálogo (`DialogueTextBox`).
- **Transiciones y Puertas en el Mapa:**
  - Efectos visuales de fundido/transición al cruzar puertas entre estancias interiores y la ciudad.
  - Detección precisa de áreas de teletransporte vinculadas a objetos del mapa de Tiled.
- **Temporizador de Tensión en Sigilo:**
  - Añadido límite de tiempo y mayor velocidad de reacción de guardias en `StealthMinigameState`.

### Cambiado
- **Estilo Visual de la Caja Fuerte (`SafeCrackerState`):**
  - Rediseño estético metálico y dorado simulando cajas fuertes auténticas de los años 30.
- **Modularización del Corcho de Evidencias (`CorkboardState`):**
  - Descomposición de la interfaz en componentes dedicados (`CardButton`, renderizado de hilos y notas).
  - Eliminación de interacción con ratón en favor de controles por teclado limpios y accesibles.
- **Colisiones del Jugador:**
  - Ajuste y reducción de la caja de colisión de Gallagher a la zona de los pies para facilitar el paso por puertas y pasillos estrechos.

### Corregido
- Corrección de desplazamiento (*scrolling*) al navegar por colecciones grandes de tarjetas en el corcho.
- Eliminación de desfases en las capas de suelo y paredes en la comisaría de policía.

---

## [1.0.0] - 2026-09-16

### Añadido
- **Gestión Narrativa Centralizada (`StoryManager`):**
  - Registro de progreso, control de eventos completados, inventario de pistas y disparadores de misiones.
- **Mundo Abierto y Estancias:**
  - Integración de todas las zonas principales: Oficina de Gallagher, Calles de la Ciudad, Callejón, Museo Del Roscio, Club Velvet y Comisaría de Policía.
- **Minijuego de Archivo Policial (`PoliceArchiveState`):**
  - Deducción por fases (Fase A: correspondencia de casos, Fase B: selección de informes clasificados).
- **Minijuego de Sigilo Inicial (`StealthMinigameState`):**
  - Infiltración evadiendo conos de visión de vigilantes.
- **Minijuego de Caja Fuerte Inicial (`SafeCrackerState`):**
  - Mecánica de ganzúa y combinación por retroalimentación auditiva y visual.
- **Sistema de Combate Básico:**
  - Primer encuentro tutorial de combate y esquiva contra matones en el callejón.
- **Animaciones del Protagonista:**
  - Movimiento multidireccional con animaciones de reposo (*idle*) y caminata (*walk*) para Tim Gallagher.

---

## [0.1.0] - 2026-09-13 a 2026-09-15

### Añadido
- **Estructura y Arquitectura Base del Motor:**
  - Inicialización con el motor **Gale Engine** y Pygame.
  - Resolución virtual fija de 480 × 270 px con escalado a ventana de escritorio.
  - Configuración global de controles, fuentes y recursos en `settings.py`.
- **Máquina de Estados de Juego:**
  - Estados fundacionales: `StartState`, `PlayState`, `DialogueState` y `CorkboardState`.
- **Estructura de Datos de Pistas (`cards.py`):**
  - Definición del modelo de datos para tarjetas de evidencia, descripciones, categorías e hilos de deducción.
- **Mapas y Conjuntos de Azulejos (Tilesets):**
  - Trazado de mapas de Tiled iniciales para la oficina, club nocturno y museo.

