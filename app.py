import streamlit as st
import json
from calculo import *

# --- CRÉDITOS E INICIALES EN BARRA LATERAL ---
with st.sidebar:
    st.divider()
    st.caption("Desarrollado por: **M.A.T.G.**") 
    st.caption("Ingenieria Civil") 
    st.caption("© 2026 - Universidad Nacional de Colombia, Sede Manizales")

# Importar tu módulo de presentación
from resultados import mostrar_resultados_estructurales

# IMPORTANTE: Descomenta la siguiente línea e importa la función principal de tu script de cálculo:
# from calculo import tu_funcion_de_calculo

st.set_page_config(page_title="Calculadora Cerchas Planas", page_icon="🏗️", layout="wide")

st.title("🏗️ Cerchas Planas")
st.caption("Interfaz en Streamlit para resolver cerchas por el Método Matricial")

# --- SECCIÓN 1: Datos Generales ---
st.header("Sección 1 — Datos Generales")
c1, c2, c3 = st.columns(3)
with c1:
    num_nodos = st.number_input("Número de Nodos:", min_value=1, value=4, step=1)
with c2:
    num_barras = st.number_input("Número de Barras:", min_value=1, value=5, step=1)
with c3:
    modulo_E = st.number_input("Módulo Elasticidad E (MPa):", min_value=0.0, value=2e11, format="%e")

# --- SECCIÓN 2: Coordenadas ---
st.header("Sección 2 — Coordenadas de Nodos")
coords_input = []
cols_nodos = st.columns(2)
for i in range(1, num_nodos + 1):
    with cols_nodos[0]:
        x = st.number_input(f"Nodo {i} - X (m):", value=0.0, key=f"x_{i}")
    with cols_nodos[1]:
        y = st.number_input(f"Nodo {i} - Y (m):", value=0.0, key=f"y_{i}")
    coords_input.extend([x, y])

# --- SECCIÓN 3: Barras ---
st.header("Sección 3 — Propiedades de Barras")
conectividad_input = []
areas_input = []
for b in range(1, num_barras + 1):
    cb1, cb2, cb3 = st.columns(3)
    with cb1:
        ni = st.number_input(f"Barra {b} - Nodo i:", min_value=1, max_value=num_nodos, value=1, key=f"ni_{b}")
    with cb2:
        nj = st.number_input(f"Barra {b} - Nodo j:", min_value=1, max_value=num_nodos, value=2 if num_nodos >= 2 else 1, key=f"nj_{b}")
    with cb3:
        area = st.number_input(f"Barra {b} - Área (mm²):", min_value=1e-6, value=0.002, format="%.6f", key=f"area_{b}")
    conectividad_input.extend([ni, nj])
    areas_input.append(area)

# --- SECCIÓN 4: Grados de Libertad ---
st.header("Sección 4 — Grados de Libertad (GDL)")
cg1, cg2 = st.columns(2)
with cg1:
    gdl_rest_str = st.text_input("GDL Restringidos (separados por coma):", value="1, 2, 7")
with cg2:
    gdl_libres_str = st.text_input("GDL Libres (separados por coma):", value="3, 4, 5, 6, 8")

def parse_gdl(cadena):
    try:
        return [int(x.strip()) for x in cadena.split(",") if x.strip() != ""]
    except ValueError:
        return []

gdl_restringidos = sorted(parse_gdl(gdl_rest_str))
gdl_libres = sorted(parse_gdl(gdl_libres_str))

# --- SECCIÓN 5: Cargas ---
st.header("Sección 5 — Cargas en GDL Libres")
cargas_input = []
if gdl_libres:
    cols_cargas = st.columns(min(len(gdl_libres), 4))
    for idx, gdl in enumerate(gdl_libres):
        with cols_cargas[idx % 4]:
            p = st.number_input(f"Carga en GDL {gdl} (N):", value=0.0, key=f"carga_{gdl}")
            cargas_input.append(p)

# --- BOTÓN DE EJECUCIÓN Y CÁLCULO ---
st.divider()
if st.button("🚀 Resolver Cercha Plana", type="primary"):
    
    # Validaciones básicas
    duplicados = set(gdl_restringidos).intersection(set(gdl_libres))
    if duplicados:
        st.error(f"⚠️ Error: Hay GDL repetidos en libres y restringidos: {list(duplicados)}")
    else:
        # 1. Empaquetar diccionario de entrada
        datos_cercha = {
            "num_nodos": int(num_nodos),
            "num_barras": int(num_barras),
            "coordenadas": coords_input,
            "areas": areas_input,
            "conectividad": conectividad_input,
            "gdl_restringidos": gdl_restringidos,
            "gdl_libres": gdl_libres,
            "E": float(modulo_E),
            "cargas": cargas_input
        }
        # Convertir la lista de coordenadas de metros (m) a milímetros (mm)
        coords_mm = [val * 1000.0 for val in coords_input]
        # 2. LLAMADA A TU CÓDIGO DE CÁLCULO (Sustituye esta sección con tu función real):
        # -----------------------------------------------------------------------------
        # Ejemplo conceptual de cómo conectas tu script:
        des,pa,lista_ke,kglobal,f_axial = calculos(num_nodos,num_barras,conectividad_input,coords_mm,areas_input,modulo_E,gdl_libres,gdl_restringidos,cargas_input)
        # -----------------------------------------------------------------------------

        st.success("¡Cálculo procesado exitosamente!")

        # 3. LLAMADA A LA INTERFAZ DE RESULTADOS:
        # Pasa las variables retornadas por tu código de cálculo a la función visual:
        mostrar_resultados_estructurales(
            gdl_libres=gdl_libres,
            gdl_restringidos=gdl_restringidos,
            desplazamientos=des,      # Reemplaza con tu variable de desplazamientos
            reacciones=pa,           # Reemplaza con tu variable de reacciones
            fuerzas_axiales=f_axial, # Reemplaza con tu variable de fuerzas axiales
            matrices_ke_global=lista_ke,# Reemplaza con tu lista de matrices ke
            K_global=kglobal         # Reemplaza con tu matriz K global
        )