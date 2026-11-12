# Ejercicio: revisar la traducción de una ficha técnica en PDF

Practica la revisión de un PDF técnico comparando una ficha electrónica ficticia en inglés con una traducción al español generada por Scanfile y sin corregir. Los valores son inventados, no describen un componente real y no deben utilizarse para tomar decisiones de ingeniería. Los archivos no contienen datos de clientes. El original y las notas de revisión se comparten bajo [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## Descarga y comparación

Guarda estos archivos en una misma carpeta:

- [Ficha original en inglés (PDF)](https://scanfile.online/samples/pdf/datasheet-en-es/datasheet-review-test.en.pdf)
- [Traducción al español sin corregir (PDF)](https://scanfile.online/samples/pdf/datasheet-en-es/datasheet-review-test.es.pdf)
- [Notas de revisión en español](https://scanfile.online/samples/pdf/datasheet-en-es/review.es.txt)

Instala la herramienta siguiendo las [instrucciones de instalación](../README.md#setup) (en inglés). Desde la carpeta que contiene los PDF, ejecuta:

```sh
pdf-translation-review datasheet-review-test.en.pdf datasheet-review-test.es.pdf -o datasheet-review.pdf
```

Si el archivo de salida ya existe, elige otro nombre: el programa no lo sobrescribe. Abre el resultado en un lector PDF. El original aparece a la izquierda y la traducción a la derecha. La instalación de dependencias requiere conexión; una vez instalada, la comparación se ejecuta en tu equipo sin subir los documentos. La herramienta organiza páginas: **no detecta errores, no comprueba el significado y no certifica traducciones**. Si alguna página se ve demasiado pequeña o diferente, revisa los archivos originales por separado.

## Lista de revisión

1. **Identificadores físicos:** compara `IN` y `OUT` con `ENTRADA` y `SALIDA` en el resultado. Una etiqueta impresa en un dispositivo puede necesitar conservarse literalmente, aunque se traduzca su significado.
2. **Tabla y unidades:** coteja símbolos, filas, columnas, signos, valores, unidades y notas. En esta muestra se observaron `I_CC`, `V_IH` y `t_PD` y los valores numéricos mostrados en las filas correspondientes. Compruébalo en los archivos; no presupongas que otras traducciones los conservarán.
3. **Terminología y ortografía:** compara «Supply current» con «Suministrar corriente» y busca la errata `pruea` en las condiciones de ensayo. La redacción necesita revisión técnica y lingüística.
4. **Instrucciones y nombres:** comprueba negaciones, condiciones y encabezado. En el resultado, `SCANFILE` aparece como `ARCHIVO ESCANEADO`, que no es el nombre original.

La traducción española no ha sido revisada de forma independiente por una persona hispanohablante nativa. Es una sola página con texto seleccionable: no es una prueba de OCR ni una medición de calidad para otros documentos. Para trabajo técnico real, consulta el documento autorizado del fabricante y recurre a profesionales cualificados.

## Alternativa en el navegador

El [lector de revisión PDF de Scanfile](https://scanfile.online/tools/pdf-translator?sf_campaign=github_pdf_review#compare-pdf-translation) permite abrir dos archivos localmente para verlos lado a lado. Su interfaz está disponible en inglés y portugués de Brasil. El enlace incluye una etiqueta fija para estadísticas agregadas, sin nombres ni contenido de archivos; la analítica sigue las preferencias de privacidad del navegador. El servicio de traducción en línea de Scanfile es independiente, requiere subir el documento y aplica las condiciones de prueba y créditos indicadas en el sitio. El desarrollador de Scanfile mantiene este repositorio.

[English version](technical-datasheet.md)
