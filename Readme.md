# Descargador

> “Hijo, **_bájamelo en música este video que esas páginas raras me llenan de virus_**”
> 
> —Mi madre, pagando YouTube Premium sin utilizarlo nunca

Pequeño script (en serio, cabe en un tupper) que:

1. Pregunta el link de YouTube.
2. Deja elegir **mp3** (solo audio para cantar en el bus)  
   o **mp4** (video completo para ver recetas de queque seco).
3. Usa `yt-dlp` + `FFmpeg` para hacer la magia.
4. Funciona en **Python 3.12** porque nos gusta lo último, porque las librerias estan sumamente actualizadas.

## ¿Cómo se corre?

```bash
make install   # instala dependencias sin dramas
make run       # lanza el interrogatorio interactivo
