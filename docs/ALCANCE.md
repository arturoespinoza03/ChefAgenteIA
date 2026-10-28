# Alcance acordado

Actualizado el 28 de octubre de 2026 por decisión del usuario.

## Objetivo

Ayudar a buscar y elegir recetas, consultar sus instrucciones y preparar una propuesta de menú según preferencias declaradas. El catálogo de 719 recetas permite búsqueda por nombre y consulta de pasos. La selección por ingredientes se limita a la fuente estructurada TheMealDB y a futuras extracciones revisadas; no se atribuye esta capacidad al catálogo completo de Kaggle.

Eliminamos la gestión de precios del producto: datos de Open Prices, consultas de productos, relaciones ingrediente-precio y cálculo económico. Se conservan recetas, imágenes, procedencia y la extracción inicial de ingredientes. No se garantiza un menú dentro de presupuesto, un ahorro ni el coste por ración.

## Precios opcionales bajo petición

Si el usuario solicita precios o una comparación, el flujo previsto recurrirá a fuentes disponibles en internet de supermercados como Mercadona o Carrefour. Esta capacidad está especificada, pero todavía no implementada ni comprobada para ninguna cadena. No se presupone que exista una base de datos pública, API accesible o conector disponible.

Flujo previsto:

1. Identificar productos e ingredientes solicitados, localidad o código postal y supermercado cuando afecten al resultado.
2. Consultar páginas oficiales o una API autorizada disponible en ese momento.
3. Mostrar nombre exacto, formato, precio, unidad de comparación, URL, fecha de consulta y condiciones visibles de promoción o localización.
4. Señalar productos no encontrados, datos ambiguos o fuentes inaccesibles. No completar precios con invenciones ni presentar un total como completo cuando faltan productos.

No se efectuarán compras. Las listas serán orientativas mientras falten cantidades y raciones verificadas. Una consulta de precios no demuestra disponibilidad ni una cesta comprable en una tienda concreta.

## Business Intelligence y demostración

El enfoque analítico pasa a ser cobertura y calidad del catálogo: número de recetas, pasos, disponibilidad de imágenes, ingredientes documentados y limitaciones de la selección. No se presentarán indicadores económicos sin datos.

La demo prevista será: petición de receta → consulta de base de datos mediante MCP → aplicación de una Skill de selección → respuesta con pasos y procedencia. Agente, MCP y Skill deben desarrollarse y probarse en la siguiente fase. Una búsqueda de precios solo se añadirá si es solicitada y existe una fuente accesible.
