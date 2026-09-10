import streamlit as st
import numpy as np
import pandas as pd

def mostrar_resultados_estructurales(
    gdl_libres, 
    gdl_restringidos, 
    desplazamientos, 
    reacciones, 
    fuerzas_axiales, 
    matrices_ke_global, 
    K_global
):
    """
    Módulo de visualización para Streamlit.
    Presenta los resultados manteniendo las unidades de entrada (mm, N, N/mm2)
    sin aplicar ninguna conversión numérica. Formatea todos los flotantes
    a máximo 4 decimales en notación decimal estándar (sin 'e').
    """
    st.divider()
    st.header("📊 Sección 7 — Resultados del Análisis Estructural")

    # Aplanar arreglos para asegurar dimensiones unidimensionales (1D)
    u_flat = np.array(desplazamientos).flatten()
    r_flat = np.array(reacciones).flatten()
    f_flat = np.array(fuerzas_axiales).flatten()

    # --- SECCIÓN 1: Desplazamientos ---
    st.subheader("1. Desplazamientos ($D_b$)")
    
    # Manejo defensivo: Verificación de longitud entre GDL libres y vector
    if len(u_flat) == len(gdl_libres):
        u_mostrar = u_flat
    else:
        indices_libres = [int(gdl) - 1 for gdl in gdl_libres]
        u_mostrar = u_flat[indices_libres]

    df_u = pd.DataFrame({
        "GDL Libre": [f"GDL {gdl}" for gdl in gdl_libres],
        "Desplazamiento (mm)": u_mostrar  # Muestra el valor puro sin convertir
    })
    
    col_u1, col_u2 = st.columns([1, 2])
    with col_u1:
        # Format '{:.4f}' garantiza formato decimal estándar con máx 4 decimales
        st.dataframe(df_u.style.format({"Desplazamiento (mm)": "{:.4f}"}), use_container_width=True)
    with col_u2:
        st.info("💡 **Unidades:** Desplazamientos en milímetros (mm).")

    # --- SECCIÓN 2: Reacciones ---
    st.subheader("2. Reacciones en Apoyos ($P_a$)")
    
    if len(r_flat) == len(gdl_restringidos):
        r_mostrar = r_flat
    else:
        indices_rest = [int(gdl) - 1 for gdl in gdl_restringidos]
        r_mostrar = r_flat[indices_rest]

    df_r = pd.DataFrame({
        "GDL Restringido": [f"GDL {gdl}" for gdl in gdl_restringidos],
        "Fuerza de Reacción (N)": r_mostrar
    })
    
    col_r1, col_r2 = st.columns([1, 2])
    with col_r1:
        st.dataframe(df_r.style.format({"Fuerza de Reacción (N)": "{:.4f}"}), use_container_width=True)
    with col_r2:
        st.info("💡 **Unidades:** Fuerzas de reacción en Newtons (N).")

    # --- SECCIÓN 3: Fuerzas Internas Axiales ---
    st.subheader("3. Fuerzas Internas Axiales por Barra")
    
    estados = []
    for f in f_flat:
        if abs(f) < 1e-4:
            estados.append("⚪ Nula (0)")
        elif f > 0:
            estados.append("🔴 Tracción (+)")
        else:
            estados.append("🔵 Compresión (-)")

    df_barras = pd.DataFrame({
        "Barra": [f"Barra {i+1}" for i in range(len(f_flat))],
        "Fuerza Axial N (N)": f_flat,
        "Estado": estados
    })

    st.dataframe(
        df_barras.style.format({"Fuerza Axial N (N)": "{:.4f}"}),
        use_container_width=True
    )

    # --- SECCIÓN 4: Matriz K Global ---
    with st.expander("🌐 Ver Matriz de Rigidez Global ($K_{global}$)"):
        num_total_gdl = K_global.shape[0]
        columnas_gdl = [f"GDL {i+1}" for i in range(num_total_gdl)]
        df_kglobal = pd.DataFrame(K_global, index=columnas_gdl, columns=columnas_gdl)
        st.dataframe(df_kglobal.style.format("{:.4f}"), use_container_width=True)

    # --- SECCIÓN 5: Matrices Ke por Barra ---
    with st.expander("🧩 Ver Matrices de Rigidez por Barra ($K_e$ Global)"):
        # Mostramos exactamente tantas matrices como barras existan
        num_barras_reales = len(f_flat)
        matrices_a_mostrar = matrices_ke_global[:num_barras_reales]

        for idx, ke in enumerate(matrices_a_mostrar):
            st.markdown(f"**Matriz $K_e$ - Barra {idx+1}:**")
            df_ke = pd.DataFrame(
                ke, 
                index=["u_i", "v_i", "u_j", "v_j"], 
                columns=["u_i", "v_i", "u_j", "v_j"]
            )
            st.dataframe(df_ke.style.format("{:.4f}"), use_container_width=True)

#streamlit run app.py