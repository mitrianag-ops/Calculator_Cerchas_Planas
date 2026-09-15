import numpy as np

def calculos(nodos, barras, nodos_barra, lista_nodos, areas, elasticida, gdlibres, gdlrest, pb):
    pb = np.array(pb).reshape(-1, 1)
    
    # DEFINIR MATRIZ DE RIGIDEZ GLOBAL
    t = nodos * 2
    kglobal = np.zeros((t, t))
    lista_ke = []
    lista_keaxial = []
    
    # Estructura para almacenar los grados de libertad (i, l, m, n) de cada barra
    gdls_por_barra = []

    # FUNCION QUE CALCULA LAS MATRICES DE RIGIDEZ DE CADA BARRA 
    def matriz_ke(numbarra):
        ke = np.zeros((4, 4))
        
        # Identificación de nodos
        idx_i = 2 * numbarra - 2
        idx_j = idx_i + 1
        num_nodoi = nodos_barra[idx_i]
        num_nodoj = nodos_barra[idx_j]
        
        # Grados de libertad locales (0-indexed para Python)
        k = 2 * num_nodoi - 2
        l = k + 1
        m = 2 * num_nodoj - 2
        n = m + 1
        
        # Guardamos los GDL de esta barra específica
        gdls_por_barra.append((k, l, m, n))

        # Coordenadas
        coorXi = lista_nodos[k]
        coorYi = lista_nodos[l] 
        coorXj = lista_nodos[m]
        coorYj = lista_nodos[n]
        
        # Geometría y propiedades
        le = np.sqrt((coorXj - coorXi)**2 + (coorYj - coorYi)**2)
        ncos = (coorXj - coorXi) / le
        usen = (coorYj - coorYi) / le
        eal = elasticida * areas[numbarra - 1] / le

        # Matriz de rigidez del elemento en coordenadas globales
        # T^T * k_local * T
        ke[0][0] = ncos**2 * eal;      ke[0][1] = usen*ncos * eal;  ke[0][2] = -ncos**2 * eal;     ke[0][3] = -usen*ncos * eal
        ke[1][0] = usen*ncos * eal;   ke[1][1] = usen**2 * eal;    ke[1][2] = -usen*ncos * eal;   ke[1][3] = -usen**2 * eal
        ke[2][0] = -ncos**2 * eal;    ke[2][1] = -usen*ncos * eal; ke[2][2] = ncos**2 * eal;      ke[2][3] = usen*ncos * eal
        ke[3][0] = -usen*ncos * eal;  ke[3][1] = -usen**2 * eal;   ke[3][2] = usen*ncos * eal;    ke[3][3] = usen**2 * eal              
        
        lista_ke.append(ke)

        # Vector de transformación para fuerza axial (1x4)
        kelocal = eal * np.array([[-ncos, -usen, ncos, usen]])
        lista_keaxial.append(kelocal)

        # Ensamblaje en la Matriz Global
        gdl = [k, l, m, n]
        for row in range(4):
            for col in range(4):
                kglobal[gdl[row]][gdl[col]] += ke[row][col]

    # Calcular Matrices Elementales y Global
    for i in range(1, barras + 1):
        matriz_ke(i)

    # EXTRACCIÓN DE SUBMATRICES Kaa, Kbb, Kab
    # Se ajustan índices (1-based de entrada a 0-based de Python)
    g_rest = [x - 1 for x in gdlrest]
    g_lib  = [x - 1 for x in gdlibres]

    kaa = kglobal[np.ix_(g_rest, g_rest)]
    kbb = kglobal[np.ix_(g_lib, g_lib)]
    kab = kglobal[np.ix_(g_rest, g_lib)]
    kba = kab.T

    # DESPLAZAMIENTOS EN GDL LIBRES
    db = np.linalg.inv(kbb) @ pb

    # REACCIONES EN GDL RESTRINGIDOS
    pa = kab @ db

    # VECTOR GLOBAL DE DESPLAZAMIENTOS (des)
    des = np.zeros((t, 1))
    for idx, gdl in enumerate(g_lib):
        des[gdl, 0] = db[idx, 0]

    # CALCULO DE FUERZAS AXIALES
    f_axial = []
    for i in range(barras):
        kelocal_nj = lista_keaxial[i]  # Matriz (1, 4)
        k, l, m, n = gdls_por_barra[i] # GDL correspondientes a ESTA barra
        
        # Desplazamientos de los nodos i y j de esta barra
        deske = np.array([
            [des[k, 0]],
            [des[l, 0]],
            [des[m, 0]],
            [des[n, 0]]
        ])
        
        # Fuerza axial: F = k_axial * d_e
        fuerza_nj = kelocal_nj @ deske
        f_axial.append(fuerza_nj[0, 0])

    return des, pa, lista_ke, kglobal, f_axial, kaa, kbb, kab, kba
# seguir probardo con varios ejercicios