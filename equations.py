import errors as e
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from kivy.uix.popup import Popup
from kivy.uix.label import Label

#Parametros fijos para testeo, modificar luego para que entren por default en la carga de parametros

intervalo = 0.5                           # Usar multiplos de 0.5, sino es posible que al calcular la correccin del xA se genere un error en la siguiente expresion: df.loc[correc_t+xA_t]["X"] = xA + (umax*xA) * correc_t
pp_CO2 = 0
H_CTE_30 = 893  # Constante de Henrry a 30° = 893 Atm*L/mol

# Deberian ser asignados segun el id del sustrato
kn = 0.02
ks = 0.02

def BalanceGama_b(p):
    # Balance de gama para calculo de b. Asume biomasa standar y NR = NH3, CO2, H2O
    # Se chequea la identidad de FCE y fn para calcular su gama segun el Nivel de referencia NR
    # Se aprovecha que esta funcion utiliza la identidad de la fn para calcular el a (consumo de fn/ consumo de FCE)
    
    # Se podria armar una funcion que calcule el gama en funcion de la formula molecular
    
    if p.id_fce=="glu":
        s=4
    else:
        raise e.error_sID
    if p.id_fn=="amonio":
        fn=0
        a = 0.2*p.yxs
    else:
        raise e.error_fnID
    if p.id_p =="etanol":
        prod = 6
    elif p.id_p =="":
        prod = 0
    else:
        raise e.error_pID
        
    x = 4.2 # Biomasa standard
    yxsv = 1/((1/p.yxs)-(p.ms/p.umax))    
        
    b = (s+a*fn-p.yxs*x-p.yps*prod)/4
    yxov = 1/ ((s/(yxsv*4))-x/4)
    mo = p.ms*s/4
    if b < 0:
        raise e.error_b
    else: 
        return a, b, yxov, mo


def BalanceGaseosoInverso(df, pp_O2, pp_CO2):
    # Aqui deberia ir el despeje para obtener los % de gases a partir del Ro2, hasta ahora no lo hice
    pass
    
def BarridoDe_D(p, rangoD):
    rows = []
    index=np.arange(rangoD[0], rangoD[1], rangoD[2])
    for i in index:
        p.d = i
        x, s, n, cl = GenerarContinuo(p, barrido=True)
        rows.append({"X":x, "S":s, "N":n, "Cl":cl})
    
    return pd.DataFrame(rows, index=index)
    
def GenerarContinuo(p, barrido=False):
    umax = p.umax
    yxs = p.yxs
    x0 = p.x0
    tf = p.tf
    fce = p.fce
    id_fce = p.id_fce
    fn = p.fn
    id_fn = p.id_fn
    kLa = p.kLa
    ms = p.ms
    tLag = p.tLag
    pp_O2 = p.pp_O2/100     # El valor entra en % lo divido para usarlo como fraccion molar
    d = p.d
    sr_c = p.sr_c
    nr_c = p.nr_c
    yps = p.yps
    id_p = p.id_p


    
# Calculo de algunos parametros iniciales

    a, b, yxov, mo = BalanceGama_b(p)
    yxsv = 1/((1/yxs)-(ms/umax))        #Calculo de rendimiento verdadero a partir de ecuacion de Pirt
    yxn = yxs/a
    C_maximo = pp_O2 / H_CTE_30                             # Solibulidad máxima de Oxigeno
    OTR_max = kLa * C_maximo + d*C_maximo                               # OTR maximo segun Kla
    rx_max = OTR_max*yxs/b

    if d>=umax:  # Esto seria un mal diseño y no se alcanzara el estado estacionario. Se simulara un lavado
        if nr_c/sr_c > a:       # Limitado en FCE
            s = 0               # Asumo que se consume todo, para definir un X inicial. Esto es arbitrario
            x = (yxsv*d*(sr_c-s)) / (d +ms*yxsv)
            
        else:                   # Limitado en Fn
            n = 0               # Asumo que se consume todo, para definir un X inicial. Esto es arbitrario
            x = nr_c*yxn       
        biomasa = []
   # Se chequea limitacion por oxigeno. Si se limita se ajusta el valor de x al mayor soportado por el kla
        if d*x > rx_max: x = rx_max/d
# Chequear q pasa con barridos de paso 0.01. Hace algo raro        
        if barrido:         # Agrego este condicional, para q cuando esta funcion se utilice para un barrido devuelva solo un valor, el cual seria el resultado de un lavado
            x = 0
            s = sr_c
            n = nr_c
            cl = C_maximo
        else:
            if d==umax: d=umax + 0.01        # Si D=umax, segun la ecuacion de crecmiento la biomasa no cambia nunca y entra en un loop infinito. modifico D para que umax-d = 0.01, generando una velocidad de lavado muy suave
            count=0
            while x > 0.01:     # pongo un limite finito "0.01" porque la funcion se acerca a 0 pero nunca se hace negativa
                biomasa.append(x)
                x = x*np.exp(umax-d)
                # Agrego un contador para cortar el ciclo luego de 1000 rondas. Esto evita loops excesivamente largos que podrian ocurrir si d es ligeramente superior a umax, generando un (umax-d) muy chico, y una velocidad de decrecimiento de la biomasa muy lenta
                count += 1
                if count > 1000:
                    break
            
            df = pd.DataFrame(biomasa, columns=["X"])
            df["S"] = sr_c - d*df["X"]/yxsv + ms*df["X"]
            df["N"] = nr_c - df["X"]/yxn
            df["Cl"] = C_maximo - ((d*df["X"]*b)/(yxs*(d+kLa)))
    
    else:   # Esto seria un estado estacionario correcto
    # Se chequea el sustrato limitante
    
        if nr_c/sr_c > a:       # Limitado en FCE
            s = (ks*d) / (umax-d) 
            if s > sr_c: s= sr_c        # Esto ocurre cuando el Sr y el D son ambos muy bajos, genera un S estacionario mayor que Sr. Lo cual no es posible y genera biomasa negativa
            x = (yxsv*d*(sr_c-s)) / (d +ms*yxsv)
            if x > rx_max/d:    # chequeo limitacion por oxigeno, si hay limitacion se corrige la biomasa y el S
                x = rx_max/d
                s= sr_c -d*x/yxsv + ms*x   
                
    # Calculo del sustrato no limitante. Se hacen todos los pasos para simplificar su interpretación
            rn = d*x/yxn
            # Despejo n estacionario de la ecuacion rn= D*(nr-n)
            n = nr_c-rn/d if d !=0 else nr_c-rn/0.001           # Este condicional se agrega para salvar el problema de un D=0, el cual genera error en la ecuacion, y conceptualmente no tiene sentido porq no seria un cultivo continuo. Sin embargo decidí simular un D muy chiquito antes que crear un error en el programa
        
        else:                   # Limitado en Fn
            n =(kn*d) / (umax-d)
            if n > nr_c: n= nr_c      # Esto ocurre cuando el Nr y el D son ambos muy bajos, genera un N estacionario mayor que Nr. Lo cual no es posible y genera biomasa negativa

            x = (nr_c-n) * yxn 
            if x > rx_max/d:    # chequeo limitacion por oxigeno, si hay limitacion se corrige la biomasa y el N
                x = rx_max/d
                n = nr_c - x/yxn
    # Calculo del sustrato no limitante. Se hacen todos los pasos para simplificar su interpretación
            rs = d*x/yxs
            s = sr_c - rs/d if d !=0 else sr_c - rs/0.001       # Este condicional se agrega para salvar el problema de un D=0, el cual genera error en la ecuacion, y conceptualmente no tiene sentido porq no seria un cultivo continuo. Sin embargo es decidí simular un D muy chiquito que crear un error en el programa
        
        
        cl = C_maximo - ((d*x*b)/(yxs*(d+kLa)))
        df = pd.DataFrame(index=range(10))
        df["X"] = x
        df["S"] = s
        df["N"] = n
        df["Cl"] = cl
    
    if barrido:
        return x, s, n, cl
    else:
        return df
        
    
    
def GenerarAlimentado(p):
    umax = p.umax
    yxs = p.yxs
    x0 = p.x0
    tf = p.tf
    fce = p.fce
    id_fce = p.id_fce
    fn = p.fn
    id_fn = p.id_fn
    kLa = p.kLa
    yps = p.yps
    id_p = p.id_p
    ms = p.ms
    tLag = p.tLag
    pp_O2 = p.pp_O2/100     # El valor entra en % lo divido para usarlo como fraccion molar
    beta = p.beta
    f = p.f
    uc = p.uc
    t = p.t
    sr_a = p.sr_a
    nr_a = p.nr_a
    v = p.v
    v0 = v  #Esto lo hago para guardar el valor de V0, sin que sufra modifiaciones a lo largo de la alimentación. Lo uso para llevar todos los valor de batch a cantidades, multiplicandolos por V0
# Calculos iniciales 
    a, b, yxov, mo = BalanceGama_b(p)
    yxsv = 1/((1/yxs)-(ms/umax))        #Calculo de rendimiento verdadero a partir de ecuacion de Pirt
    yxn = yxs/a
    C_maximo = pp_O2 / H_CTE_30                             # Solibulidad máxima de Oxigeno
    OTR_max = kLa * C_maximo                                # OTR maximo segun Kla
    
# Genero el batch previo a la alimentación
    df = GenerarCineticaBatch(p)
    xv0 = df["X"].iloc[-1]*v
    s0 = df["S"].iloc[-1]*v
    n0 = df["N"].iloc[-1]*v
    
    Talimentacion = np.arange(tf+intervalo, tf+t, intervalo)
    
    dfa = pd.DataFrame(index=Talimentacion)
    xv = xv0
    s = s0
    n = n0
    
    
    
    
     
    if uc > 0:  # alimentacion con flujo variable
        yxs_alimentado= 1/ ((1/yxsv)+(ms/uc))               # Calculo el Yxs de en la alimentacion exp
        for i in Talimentacion:  #Se cicla tiempo a tiempo en funcion del tiempo de alimentación. 
            v_alimentado = f * (((np.exp(uc*intervalo))/uc) - ((np.exp(uc*0))/uc))   # Esta expresion es la variación de volumen en funcion del tiempo, proveniente de integrar la formula del flujo entre 0 y intervalo
            DeltaN = v_alimentado * nr_a
            DeltaS = v_alimentado * sr_a
            
            
           # X_Fexp = xv*np.exp(uc*intervalo)                # Se calcula el crecimiento exponencial segun la uc.
           # Elimino este, solo dejo el que va por consumo de sustrato
            X_umax = xv*np.exp(umax*intervalo)              # Se calcula el crecimiento irrestricto, suponiendo que se calculo mal el flujo y ambos nutrientes estan en exceso
            X_Fn = xv + yxn * (DeltaN + n)                  # Se calcula el crecimiento segun limitacion por N, Se suma el N remanente de tiempo anterior
            X_FCE = xv + (DeltaS + s)*yxs_alimentado            # Se calcula el crecimiento exponencial segun el deltaS alimentado y el Yxs correspondiente a la fase de alimentación (uc).
            X_O2 = xv + (v*OTR_max - mo*xv)*yxov*intervalo  # Se calcula el crecimiento segun lo soportado por OTR. XV + Vrx * DeltaT. El Vrx se despeja de la ecuacion de pirt de oxigeno, reemplazando ro2 por OTR_MAX. rx = (ro2 - mo*x)*yxov 

            f = f*np.exp(uc*intervalo)  # Se actualiza el nuevo flujo tiempo a tiempo segun su expresion dependiente de uc
            xv = min(X_umax, X_Fn, X_FCE, X_O2)   # Luego de calcular los posibles XV, tomo el menor
            
            # Estos X estan para fase de testeo, no cumplen ninguna funcion
            dfa.at[i, "X_umax"] = X_umax
            dfa.at[i, "X_Fn"] = X_Fn
            dfa.at[i, "X_FCE"] = X_FCE
            dfa.at[i, "X_O2"] = X_O2
            dfa.at[i, "X"] = xv
            
            #Calculo del yxs segun lo que crecio
            
            # En el primer punto, el deltaX se toma distinto, utilizando el XV0, en el resto se calcula usando el punto anterior del DF.
            # Este condicional funciona para reconocer el primer punto, luego sigue siempre igual
            Xi = xv0 if i ==tf+intervalo else dfa["X"].loc[i-intervalo]
            Xf = dfa["X"].loc[i]
            deltaX = Xf- Xi 
            
            u_intervalo = np.log(Xf/Xi)/intervalo           # Calculo la u del intervalo segun el deltaX
            yxs_intervalo = 1/ ((1/yxsv)+(ms/u_intervalo))  # Calculo el yxs del intervalo segun la u por pirt

            n = n+DeltaN - deltaX/yxn
            s = s+DeltaS - deltaX/yxs_intervalo
        
            dfa.at[i, "S"] = s 
            dfa.at[i, "N"] = n
        
        
    else:   # Alimentacion con flujo constante
        for i in Talimentacion:  #Se cicla tiempo a tiempo en funcion del tiempo de alimentación. En todas las formulas el 1 simboliza el DeltaT, No lo saque para no olvidar que todas las ecuaciones van en funcion del tiempo
            X_umax = xv*np.exp(umax*intervalo)          # Se calcula el crecimiento irrestricto, suponiendo que se calculo mal el flujo y ambos nutrientes estan en exceso
            X_Fn = xv + yxn * (f*nr_a*intervalo + n)    # Se calcula el crecimiento segun limitacion por N, Se suma el N remanente de tiempo anterior
            X_FCE = ((f*sr_a)/ms) + (xv-((f*sr_a)/ms))*np.exp(-yxsv*ms*intervalo) # Se calcula el crecimiento segun limitacion por FCE
            if s > 10*ks: X_FCE += s*yxs       # Si el S remanente es muy grande se consume a umax segun el yxs
            if X_FCE < xv: X_FCE = xv   # Si lo que alimento es menos que el gasto de mantenimiento, esta ecuacion devuelve un XV negativo. Corrigo para que no ocurra
            X_O2 = xv + (v*OTR_max - mo*xv)*yxov*intervalo       # Se calcula el crecimiento segun lo soportado por OTR. XV + Vrx * DeltaT. El Vrx se despeja de la ecuacion de pirt de oxigeno, reemplazando ro2 por OTR_MAX. rx = (ro2 - mo*x)*yxov 
    
           
            xv = min(X_umax, X_Fn, X_FCE, X_O2)   # Luego de calcular los posibles XV, tomo el menor
            
            # Estos X estan para fase de testeo, no cumplen ninguna funcion
            dfa.at[i, "X_umax"] = X_umax
            dfa.at[i, "X_Fn"] = X_Fn
            dfa.at[i, "X_FCE"] = X_FCE
            dfa.at[i, "X_O2"] = X_O2
            dfa.at[i, "X"] = xv

            # En el primer punto, el deltaX se toma distinto, utilizando el XV0, en el resto se calcula usando el punto anterior del DF.
            # Este condicional funciona para reconocer el primer punto, luego sigue siempre igual
            Xi = xv0 if i ==tf+intervalo else dfa["X"].loc[i-intervalo]
            Xf = dfa["X"].loc[i]
            deltaX = Xf- Xi 
            
            n = n+f*nr_a*intervalo - deltaX/yxn
            s = s+f*sr_a*intervalo - (1/yxsv)*deltaX - ms*Xi*intervalo-ms*(deltaX)*(intervalo**2)/2 
        
            if s < 0: s=0
            if n < 0: n=0
            dfa.at[i, "S"] = s 
            dfa.at[i, "N"] = n
        
        # Se corrige el volumen. Hasta ahora solo se usa para el oxigeno. V*OTR_max
            v += f*intervalo

    return pd.concat([df*v0, dfa], ignore_index=False)

def GenerarCineticaBatch(p):
    umax = p.umax
    yxs = p.yxs
    x0 = p.x0
    tf = p.tf
    fce = p.fce
    id_fce = p.id_fce
    fn = p.fn
    id_fn = p.id_fn
    kLa = p.kLa
    yps = p.yps
    id_p = p.id_p
    ms = p.ms
    tLag = p.tLag
    pp_O2 = p.pp_O2/100     # El valor entra en % lo divido para usarlo como fraccion molar
    beta = p.beta

    
    
#### Se calculan parametros iniciales a partir de los datos proporcionados ####
    Tarray = np.arange(0, tf+intervalo, intervalo)
    df = pd.DataFrame({"T":Tarray})
    df.index = df["T"]
    a, b, yxov, mo = BalanceGama_b(p)                              #Calculo el b a partir del rendimiento por balance de gama, ademas se calcula el a, segun la identidad de la fn
   
#### Este bloque define el crecimiento de x, teniendo en cuenta una posible limitacion de O2 ####
    
    xF = x0*np.exp(umax*(tf-tLag))                          # Calculo del x final si fuese exp hasta el final
    C_maximo = pp_O2 / H_CTE_30                             # Solibulidad máxima de Oxigeno
    OTR_max = kLa * C_maximo                                # OTR maximo segun Kla
    xA = (OTR_max * yxs)/(umax * b)                   # x maxima soportada creciendo exp segun OTR
    xA_t = (np.log(xA) - np.log(x0))/umax
    
    # Calculo de crecmiento exponencial real, se agrega al df. Si hay limitacion se completa con 0
    df["X"] = np.where( df.index<xA_t, x0*np.exp(umax*df.index), x0 )

#### Calculo del crecimiento entre tiempos menores al intervalo de tiempo en el df.    Esta correccion es necesaria porque el crecimiento exp puede detenerse entre puntos de medicion ####

    if xF>xA:
        if xA_t%1 < intervalo:                                        # ej: el t exponencial finaliza en .20
            correc_t = intervalo - xA_t%1                             # el t a corregir con un crecimiento lineal seria 0.30, es decir hasta llegar a .50 . Tomando en cuenta intervalos de 0.5
        else:                                                         # Ej: el t exponencial finaliza en 0.55
            correc_t = intervalo - (xA_t%1 - intervalo)               # el t a corregir con un crecimiento lineal seria 0.45, es decir hasta llegar a .00 . Tomando en cuenta intervalos de 0.5
        if xA_t > 0 :                                                 # este if protege de una situacion de kLa muy chico, donde la limitacion por oxigeno se da al inicio del cultivo. El problema es que si xA < x0, este tiempo da negativo
            df.at[correc_t+xA_t, "X"] = xA + (umax*xA) * correc_t        # Se corrige la biomasa generada desde el instante xA_t, hasta un valor del index tomando en cuenta crecimiento lineal  

#### Crecimiento lineal ####
        # Cuando el tiempo es mayor al tiempo de xA, se completa la columna ["X"] segun la ecuacion xF = xA + (rx * delta T )
            
            df["X"] = np.where( df.index > correc_t+xA_t, df.loc[correc_t+xA_t]["X"] + (umax*xA * (df.index-(correc_t+xA_t))) , df["X"] )
        # Esta situacion modela un crecimiento que inicia limitado en oxigeno
        else:
            df["X"] = np.where( df.index >= intervalo,  x0 + (OTR_max*yxs/b)*df.index, x0)
        

#### Calculo del consumo de FCE y fn ####

    df["dX"] = df["X"].diff(1)      # Genero una columna con los deltaX, para calcular asi los deltaS utilizando el yxs
    index = df.index.to_list()      # Genero una lista iterable, que corresponde al index
    index.pop()                     # Le quito el ultimo valor, ya que sino generara un error out of index
    df.at[0,"S"]= fce               # Defino el S0 a partir del valor ingresado
    df.at[0,"N"]= fn               # Defino el fn inicial a partir del valor ingresado
    df.at[0, "P"] = 0               # Siempre se comienza sin producto, por definicion nuestra
    
    Xf_lim_FCE = x0 + yxs* fce
    Xf_lim_fn = x0 + (yxs/a)*fn                    # yxs/a = Yx/n
    
    # Se itera sobre el index, calculando el DeltaS y Deltafn, restandolo fila a fila
    for i in index:
        
        deltaS = df.at[i+intervalo,"dX"] / yxs
        deltaN = df.at[i+intervalo,"dX"] / (yxs/a)       # yxs/a = Yx/n
        
        Nuevo_S = df.at[i, "S"] - deltaS
        Nuevo_N = df.at[i, "N"] - deltaN
        Nuevo_P = df.at[i, "P"] + deltaS*yps
        

# Se chequea en que nutriente esta limitado, luego se corrige la Xf en funcion del nutriente limitante y su rendimiento
# Se aprovecha este loop para agregar el producto, si lo hubiese

        if Xf_lim_FCE > Xf_lim_fn:  # Cultivo limitado en fn
            if Nuevo_N > 0:
                df.at[i+intervalo, "N"] = Nuevo_N
                df.at[i+intervalo, "S"] = Nuevo_S       # Mientras tenga fn, la FCE se ira restando sin problema
                df.at[i+intervalo, "P"] = Nuevo_P 
                

            else:           # Se acaba la Fn, pero sobra FCE
                df.at[i+intervalo, "N"] = 0            # Cuando se acabe la fn, la FCE se ira restando segun el mantenimiento
                df.at[i+intervalo, "X"] = Xf_lim_fn     # Al no haber mas fn, se corrije el valor de X al mayor posible en funcion de la cantidad inicial de fn
                
                if df.at[i+intervalo, "X"]-df.at[i, "X"] >0:            # Chequea que este sea el ultimo punto de crecimiento
                    df.at[i+intervalo, "S"] = df.at[i, "S"] - (df.at[i+intervalo, "X"]-df.at[i, "X"]) / yxs        # Resta FCE segun rendimineto por ultima vez, segun la formula DeltaX/rend. De ahora en mas solo se restara segun ms
                    df.at[i+intervalo, "P"] = df.at[i, "P"] + ((df.at[i+intervalo, "X"]-df.at[i, "X"]) / yxs) * yps                # Tomo el delta S calculado en la linea de arriba, y multiplico por yps
                
                elif (Nuevo_S > 0):
    # Ecuacion de pirt cuando Rx=0  ==> Rs = ms*x + B*x.    Multiplico por tiempo para calcular DeltaS 
    # ms*X*tiempo + rp*tiempo / yps. Es decir DeltaS + DeltaP/yps. Lo que gasta en mantenimiento, mas lo q va a producto
                
                    Nuevo_S = df.at[i, "S"] - Xf_lim_fn*ms*intervalo -  (Xf_lim_fn*beta*intervalo / yps if yps>0 else 0 )   # Se agrega un termino condicional si hay un Yps para restar sustrato en fase estacionaria
                    df.at[i+intervalo, "S"] = Nuevo_S

    # Se agrega el termino de la fce destinada a generar producto, utilizando un valor de beta como si fuese de ludekin y piret
                    df.at[i+intervalo, "P"] = df.at[i, "P"] + Xf_lim_fn*beta*intervalo if yps>0 else 0
                else:
                    df.at[i+intervalo, "S"] = 0
                
                
                
        else:                       # Cultivo limitado en FCE
            if Nuevo_S > 0:
                df.at[i+intervalo, "S"] = Nuevo_S
                df.at[i+intervalo, "N"] = Nuevo_N      # Mientras tenga FCE, la fn se ira restando sin problema
                df.at[i+intervalo, "P"] = Nuevo_P       # Agrego la cantidad de producto calculando el DeltaS*yps 
                
            else:
                df.at[i+intervalo, "S"] = 0             # Cuando se acabe la FCE, la fn permanecera constante
                df.at[i+intervalo, "N"] = fn-fce*a  # Se fija el valor a Fn-DeltaFn, calculando DeltaFn como DeltaS*a
                df.at[i+intervalo, "X"] = Xf_lim_FCE    # Al no haber mas FCE, se corrije el valor de X al mayor posible en funcion de la cantidad inicial de FCE
                df.at[i+intervalo, "P"] = fce*yps #Se mantiene constante, por no hay fce. Tomo el valor anterior


    #### Agrego la fase lag al final ####
    df = df.shift(int(tLag/intervalo)).fillna(method='backfill')    # Genero un corrimiento de n intervalos, segun tLag/intervalo. Luego relleno con el valor mas proximo

    return df

if __name__ == "__main__":
    
    class objeto(object):   # Utilizo este objeto para almacenar los inputs de la interfase y pasarlo a las funciones necesarias
        pass
    p=objeto() 
    
    p.umax = 0.4
    p.yxs = 0.5
    p.tf = 10
    p.fce = 1
    p.id_fce = "glu"
    p.fn = 0.05
    p.id_fn = "amonio"
    p.x0 = 0.2
    p.yps = 0
    p.id_p = "etanol"
    p.kLa = 1000
 # Continuo   
    p.d = 0.5
    p.sr_c = 10
    p.nr_c = 1
# Alimentado
    p.f = 0.5
    p.uc = 0
    p.t = 10
    p.sr_a = 2
    p.nr_a = 2
    p.v = 10
# Inputs de la ventada avanzados
    p.ms = 0.04
    p.tLag = 2
    p.pp_O2 = 21
    p.beta = 0


    df= GenerarAlimentado(p)
#    df = GenerarCineticaBatch(p)
    df[["X", "S", "P", "N"]].plot()
#    df[["X_umax", "X_FCE", "S", "X_O2", "X", "N"]].plot()


