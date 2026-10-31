# 鯉 · El koi de mi perfil

Debajo de la tarjeta de racha nada un koi en pixel art. No es un dibujo fijo: se genera a partir de mi actividad pública en GitHub y se redibuja él solo.

## De dónde sale el pez

Lo dibuja [git-koi](https://github.com/yalongwastaken/git-koi) cada noche (00:20 UTC) con los datos públicos de la cuenta:

- **Color base:** el cuerpo elegido en el workflow (`white`). Existen también `black`, `asagi`, `tea`, `gold` y `platinum`.
- **Manchas = lenguajes.** Cada lenguaje de mis repos públicos (y de los repos públicos a los que contribuyo) se asigna, por el color que le da GitHub, al pigmento koi más cercano: rojo (*beni*), naranja, amarillo (*ki*) o azul (*ai*). Los lenguajes grises o sin color pasan a negro (*sumi*). El pigmento con más peso marca el patrón principal, el segundo añade manchas o costados y el tercero tiñe la base de las aletas.
- **Tamaño = contribuciones.** Con pocas contribuciones el koi es joven, pequeño y de colores pálidos. Al acumular más, crece y se ve con todos los colores.
- **Rachas.** La racha actual pinta de dorado los bordes de las aletas. La racha más larga hace los colores más vivos.

## Cómo nada

- Cada día recorre un camino aleatorio distinto: cambia de rumbo y de velocidad, evita los bordes y pasa por detrás de la tarjeta, que hace de cristal esmerilado.
- Va recto en línea recta y se curva hacia el lado al que gira.
- De vez en cuando frena y sube a respirar: asoma el hocico y deja ondas en el agua.

## Cómo está hecho

- [`.github/workflows/koi.yml`](../.github/workflows/koi.yml) dibuja `koi/koi.gif` con git-koi.
- [`.github/workflows/streak-koi.yml`](../.github/workflows/streak-koi.yml) descarga la tarjeta de [GitHub Readme Streak Stats](https://github.com/DenverCoder1/github-readme-streak-stats) cada 6 horas y ejecuta [`.github/scripts/streak_koi.py`](../.github/scripts/streak_koi.py). El script endereza los fotogramas del koi, genera el recorrido del día y lo junta todo en un solo SVG animado: [`koi/streak-koi.svg`](streak-koi.svg).
- Es un SVG y no un GIF para que se mueva siempre, sin botón de play.

[← Volver al perfil](https://github.com/S34mu5)
