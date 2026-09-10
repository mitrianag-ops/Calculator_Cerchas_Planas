import numpy as np

def calculos(nodos,barras,nodos_barra,lista_nodos,areas,elasticida,gdlibres,gdlrest,pb):
    pb= np.array(pb).reshape(-1, 1)
# DEFINIR MATRIX DE RIGIDEZ GLOBAL
    t=nodos*2
    kglobal=np.zeros((t,t))
    lista_ke=[]
    # FUNCION QUE CALCULA LAS MATRICES DE RIGIDEZ DE CADA BARRA 
    def matriz_ke(numbarra):
        global k,l,m,n
        ke=np.zeros((4,4))
        i=2*numbarra-2
        j=i+1
        num_nodoi=nodos_barra[i]
        num_nodoj=nodos_barra[j]
        k=2*num_nodoi-2 # gdl-1 en el nodo i
        l=k+1
        m=2*num_nodoj-2
        n=m+1
        coorXi=lista_nodos[k] #COORDENADAS DEL NODO i
        coorYi=lista_nodos[l] 
        coorXj=lista_nodos[m] #COORDENADAS DEL NODO j
        coorYj=lista_nodos[n]
        le=np.sqrt((coorXi-coorXj)**2+(coorYi-coorYj)**2)
        ncos=(coorXj-coorXi)/le
        usen=(coorYj-coorYi)/le
        eal=elasticida*areas[(numbarra-1)]/le
        kelocal=eal*np.array([-ncos,-usen,ncos,usen])
        ke[0][0]=ncos**2*eal; ke[0][1]=usen*ncos*eal; ke[0][2]=-ncos**2*eal; ke[0][3]=-usen*ncos*eal #crear fila 1
        ke[1][0]=usen*ncos*eal; ke[1][1]=usen**2*eal; ke[1][2]=-usen*ncos*eal; ke[1][3]=-usen**2*eal #crear fila 2
        ke[2][0]=-ncos**2*eal; ke[2][1]=-usen*ncos*eal; ke[2][2]=ncos**2*eal; ke[2][3]=usen*ncos*eal #crear fila 3
        ke[3][0]=-usen*ncos*eal; ke[3][1]=-usen**2*eal; ke[3][2]=usen*ncos*eal; ke[3][3]=usen**2*eal #crear fila 4              
        lista_ke.append(ke)
        # SUMANDO-ENSAMBLAJE DE LA KE EN LA K GLOBAL
        kglobal[k][k]=kglobal[k][k]+ke[0][0]; kglobal[k][l]=kglobal[k][l]+ke[0][1]; kglobal[k][m]=kglobal[k][m]+ke[0][2]; kglobal[k][n]= kglobal[k][n]+ke[0][3] #sumar fila 1
        kglobal[l][k]=kglobal[l][k]+ke[1][0]; kglobal[l][l]=kglobal[l][l]+ke[1][1]; kglobal[l][m]=kglobal[l][m]+ke[1][2]; kglobal[l][n]= kglobal[l][n]+ke[1][3] #sumar fila 2
        kglobal[m][k]=kglobal[m][k]+ke[2][0]; kglobal[m][l]=kglobal[m][l]+ke[2][1]; kglobal[m][m]=kglobal[m][m]+ke[2][2]; kglobal[m][n]= kglobal[m][n]+ke[2][3] #sumar fila 3
        kglobal[n][k]=kglobal[n][k]+ke[3][0]; kglobal[n][l]=kglobal[n][l]+ke[3][1]; kglobal[n][m]=kglobal[n][m]+ke[3][2]; kglobal[n][n]= kglobal[n][n]+ke[3][3] #sumar fila 4 
        return kelocal

    #  FUNCION QUE CALCULA CADA KE PARA SUMAR EN LA KGLOBAL
    def calcular_kglobal(barras):
        # recorre cada barra  para calcular su matriz de rigidez y sumarla a la k global
        for i in range(1,barras+1,1):
            matriz_ke(i)
    calcular_kglobal(barras)

    # SACAR MATRICES AA,AB,BB
    def matrix_kaa(): # sacar matrix kaa
        kaa=np.zeros((len(gdlrest),len(gdlrest)))
        g=0
        for i in gdlrest:
            h=0
            for j in gdlrest:
                kaa[g][h]=kglobal[i-1,j-1]
                h=h+1
            g=g+1
        return kaa
    kaa=matrix_kaa()

    # OBTENER MATRIX KBB
    def matrix_kbb():
        kbb=np.zeros((len(gdlibres),len(gdlibres)))
        g=0
        for i in gdlibres:
            h=0
            for j in gdlibres:
                kbb[g][h]=kglobal[i-1,j-1]
                h=h+1
            g=g+1
        return kbb
    kbb=matrix_kbb()

    # OBTENER MATRIX KAB
    def matrix_kab():
        kab=np.zeros((len(gdlrest),len(gdlibres)))
        g=0
        for i in gdlrest:
            h=0
            for j in gdlibres:
                kab[g][h]=kglobal[i-1,j-1]
                h=h+1
            g=g+1
        return kab
    kab=matrix_kab()

    # CALCULAR DEZPLAZAMIENTOS DE LOS GDL LIBRES
    db=np.linalg.inv(kbb)@pb

    # CALCULAR REACCIONES
    pa=kab@db

    # CALCULAR FUERZAS AXIALES-INTERNAS DE CADA BARRA
    des=np.zeros((t,1)) # VECTOR QUE ALMACENARA TODOS LOS DESPLAZAMIENTOS
    def desplaz():  # FUNCION QUE VA LLENANDO LOS DESPLA EN EL VECTOR DES
        h=0
        for i in gdlibres:
            des[i-1][0]=db[h,0]
            h=h+1
        for j in gdlrest:
            des[j-1][0]=0
    desplaz()

    f_axial=[] # LISTA QUE ALMACENA LAS FUERZAS AXIALES DE TODAS LAS BARRAS
    def fuerza_axial(barras): 
        for i in range(1,barras+1,1):
            kelocal_nj=matriz_ke(i)
            deske=np.array([[des[k,0]],[des[l,0]],[des[m,0]],[des[n,0]]])
            fuerza_nj=kelocal_nj@deske
            f_axial.append(fuerza_nj[0])
    fuerza_axial(barras)

    return des,pa,lista_ke,kglobal,f_axial



# seguir probardo con varios ejercicios
# elaborar repositorio githud para subir la app a la nube y poder usar solo con el link sin tenr q correr vsc