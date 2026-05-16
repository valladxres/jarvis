# 👏 Jarvis — Automatización con aplausos

Aplaude dos veces y Jarvis te da la bienvenida, abre Spotify con tu canción favorita, lanza Claude Desktop y abre la terminal, todo automáticamente.

Funciona en **macOS** y **Windows**.

---

## Demo

> Aplaude dos veces → Jarvis habla → Spotify suena → Claude y la terminal se abren solos.

---

## ¿Qué necesitas tener instalado?

| Requisito | Para qué |
|-----------|----------|
| [Python 3.9+](https://www.python.org/downloads/) | Ejecutar el script |
| [Spotify](https://www.spotify.com/download/) | Reproducir la música |
| [Claude Desktop](https://claude.ai/download) | La app que Jarvis abre |
| Micrófono | Detectar los aplausos |

---

## Instalación

### macOS

```bash
# 1. Clona el repositorio
git clone https://github.com/tu-usuario/jarvis.git
cd jarvis

# 2. Instala las dependencias
pip install sounddevice numpy

# 3. Configura tu .env
cp .env.example .env
# Abre .env con cualquier editor y personaliza los valores

# 4. Ejecuta
python jarvis.py
```

> **Nota:** La primera vez que ejecutes, macOS pedirá permiso de micrófono. Ve a **Preferencias del Sistema → Privacidad y Seguridad → Micrófono** y actívalo para Terminal.

### Windows

```powershell
# 1. Clona el repositorio
git clone https://github.com/tu-usuario/jarvis.git
cd jarvis

# 2. Instala las dependencias
pip install sounddevice numpy pyttsx3

# 3. Configura tu .env
copy .env.example .env
# Abre .env con el Bloc de notas y personaliza los valores

# 4. Ejecuta
python jarvis.py
```

---

## Configuración

Edita el archivo `.env` (copia de `.env.example`) con tus preferencias:

| Variable | Descripción | Default |
|----------|-------------|---------|
| `JARVIS_NOMBRE` | Tu nombre para el saludo | *(vacío)* |
| `JARVIS_SPOTIFY_URL` | Link de tu canción en Spotify | canción de ejemplo |
| `JARVIS_APPS` | Apps a abrir (separadas por coma) | `Terminal,Claude` |
| `JARVIS_THRESHOLD` | Sensibilidad del micrófono (0.0–1.0) | `0.20` |
| `JARVIS_VOICE_MAC` | Voz de macOS | `Monica` |
| `JARVIS_VOICE_LANG` | Idioma de voz en Windows | `es` |
| `JARVIS_VOICE_RATE` | Velocidad de habla (palabras/min) | `148` |

### ¿Cómo obtengo el link de mi canción en Spotify?

1. Abre Spotify y busca tu canción
2. Clic derecho → **Compartir** → **Copiar enlace de canción**
3. Pega el link en `JARVIS_SPOTIFY_URL` dentro de tu `.env`

### Ajustar la sensibilidad del micrófono

| Entorno | `JARVIS_THRESHOLD` recomendado |
|---------|-------------------------------|
| Muy silencioso | `0.10` – `0.15` |
| Normal | `0.15` – `0.25` |
| Ruidoso | `0.25` – `0.40` |

---

## Solución de problemas

**No detecta los aplausos**
→ Baja el valor de `JARVIS_THRESHOLD` en tu `.env`.

**Detecta aplausos cuando no los hay**
→ Sube el valor de `JARVIS_THRESHOLD`.

**No se escucha la voz en macOS**
→ Prueba en la terminal: `say -v Monica "Hola"`. Si falla, ejecuta `say -v '?'` para ver las voces disponibles y actualiza `JARVIS_VOICE_MAC`.

**Spotify no se abre**
→ Asegúrate de que Spotify esté instalado. El link debe tener el formato `spotify:track:ID`.

**Error: No module named sounddevice**
→ Ejecuta `pip install sounddevice numpy` con el entorno virtual activo.

---

## Licencia

MIT — úsalo, modifícalo y compártelo libremente.
