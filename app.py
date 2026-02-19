# --- CÁLCULOS CORREGIDOS (Estilo Excel) ---
    
    # Tasa fija horaria (Energía + Amortización + Renta + Internet + MO Inactiva)
    # Según tus datos: 1.05 + 5.60 + 5.00 + 1.40 + 3.93 = 16.98 aprox.
    tasa_fija_hr = COSTO_ENERGIA_HR + AMORTIZACION_HR + RENTA_HR + INTERNET_HR + MO_INACTIVA_HR
    
    subtotales_por_color = []
    
    if modo_impresion == "Un solo color":
        costo_material = detalles_material[0]['costo_g'] * detalles_material[0]['gramos']
        costo_fijo_pieza = tasa_fija_hr * total_horas_impresion
        # En tu excel el total por pieza incluye sus costos fijos y material
        subtotal_pieza = costo_material + costo_fijo_pieza
        subtotales_por_color.append(subtotal_pieza)
    else:
        # Para MULTICOLOR: Cada color en el Excel tiene su propio tiempo y costo fijo
        for item in detalles_material:
            c_material = item['costo_g'] * item['gramos']
            # Usamos el tiempo individual de cada color (que debes capturar en el input)
            c_fijo = tasa_fija_hr * item['horas_color'] 
            subtotales_por_color.append(c_material + c_fijo)

    # Suma de todos los costos de materiales y costos fijos de cada fase
    costo_base_acumulado = sum(subtotales_por_color)
    
    # 3. Mano de Obra Activa (Se suma al final de todo el proceso)
    costo_mo_activa_total = tiempo_mo_activa * MO_ACTIVA_HR
    
    # COSTO TOTAL DE PRODUCCIÓN
    costo_total_produccion = costo_base_acumulado + costo_mo_activa_total
    
    # PRECIO FINAL CON UTILIDAD (Aplicada al total como en tu Excel)
    precio_final = costo_total_produccion * (1 + utilidad_factor)
