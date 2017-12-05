#--------------------------------------------------------------------------------
# Importando modulos
import os
from shutil import copy
import numpy as np
#--------------------------------------------------------------------------------
def meteor_reader(linhas_arquivo, captura):
    meteor_trail = []
    p_init = 0  # Valor inicial para usar como verificador (caso nao seja alterado)
    p_final = 0  # Valor inicial para usar como verificador (caso nao seja alterado)
    if len(linhas_arquivo) >= 15:    # Perguntando se arquivo e ruido
        #
        for line in range(len(linhas_arquivo)):    # Correndo pelas linhas do arquivo .txt caso nao seja ruido
            #
            if "trail #0" in linhas_arquivo[line]:
                p_init = line + 2
            if "trail 1" in linhas_arquivo[line]:
                p_final = line - 1
                break
    #
    # Mesmo nao sendo ruido, arquivo pode ter poucos pontos RA e DEC no ceu
    # Perguntando se captura possui mais de 5 pontos no ceu
    # Aqui tambem verifica se p_init e p_final sao diferentes de zero (valores iniciais antes de verificar se e ruido)
    # E verifico (p_init >= 7) se a captura possui registros de estrelas o suficiente para um bom registro de de RA e DEC
    if p_final >= p_init + 5:# and p_init >= 7:  # talvez nao necessario
        for p in range(p_init,p_final+1):
            if '->'  in linhas_arquivo[p]:  # Making sure line contains information of RA and DEC, since it must have '->' character
                tmp = linhas_arquivo[p].split("->")
                tmp0 = tmp[0].split(" ")
                tmp1 = tmp[1].split(" ")
                tmp2 = tmp[2].split(" ")
                ra = tmp0[-1]
                dec = tmp1[-1]
                meteor_trail.append([float(ra), float(dec)])
        meteor_id = captura[0:16]
        #
        return meteor_trail, meteor_id  
    else:
        # Retornando lista vazia e string qualquer caso contrario
        return [], '0'
#--------------------------------- FIM DO MODULO --------------------------------
#--------------------------------------------------------------------------------
def meteor_path(meteor_trail, tam_trilha):
    # Checking if meteor cross Vernal point (ra=0 -> ra=360, which is bad for least square)
    meteor_trail=np.array(meteor_trail)
    ra = meteor_trail[:,0]
    dec = meteor_trail[:,1]
    devider=[]
    # finding vernal point (right ascension change 0->360)
    for i in range(len(ra)-1):
        if abs(ra[i] - ra[i+1]) > 300:
            devider.append(i+1)
            break
    #--------------------------------------------------------------------------------
    # Deviding between trail before vernal point and after: ra_0 is before, ra_1 is after
    if len(devider) != 0:
        # Before vernal point
        ra_0=ra[0:devider[0]]
        dec_0=dec[0:devider[0]]
        # After vernal point
        ra_1=ra[devider[0]:]
        dec_1=dec[devider[0]:]
    #--------------------------------------------------------------------------------
    # Gettin ra and dec lenght in the sky
    # If meteor cross vernal point
    if len(devider) != 0:
        ra_len0 = ra_0
        dec_len0 = dec_0
        ra_len1 = ra_1
        dec_len1 = dec_1
        ra_size0 = abs(ra_len0[0] - ra_len0[-1])
        dec_size0 = abs(dec_len0[0] - dec_len0[-1])
        ra_size1 = abs(ra_len1[0] - ra_len1[-1])
        dec_size1 = abs(dec_len1[0] - dec_len1[-1])
        ra_size = ra_size0 + ra_size1
        dec_size = dec_size0 + dec_size1
    # If meteor does not cross vernal point
    else:
        ra_len = ra
        dec_len = dec
        ra_size = abs(ra_len[0] - ra_len[-1])
        dec_size = abs(dec_len[0] - dec_len[-1])
    # setting trail size
    meteor_length=np.sqrt(ra_size**2+dec_size**2)
    #--------------------------------------------------------------------------------
    # Applying least square (m = angular coeff., c = linear coeff.)
    # If meteor cross vernal point
    if len(devider) != 0:
        if len(ra_0) > len(ra_1):
            ra_lstsq = ra_0
            dec_lstsq = dec_0
        else:
            ra_lstsq = ra_1
            dec_lstsq = dec_1      
        A = np.vstack([ra_lstsq, np.ones(len(ra_lstsq))]).T
        m, c = np.linalg.lstsq(A, dec_lstsq)[0]
    # If meteor does not cross vernal point
    else:
        A = np.vstack([ra, np.ones(len(ra))]).T
        m, c = np.linalg.lstsq(A, dec)[0]
    #--------------------------------------------------------------------------------
    # Checking direction: left (<0) or right (>0). This information is useful for
    # calculation of meteor's path extention
    # If meteor cross vernal point
    if len(devider)!=0:
        if len(ra_0) > len(ra_1):
            ra_dir = ra_0
        else:
            ra_dir = ra_1
    # If meteor does not cross vernal point
    else:
        ra_dir = ra
    # Getting direction
    if ra_dir[0] - ra_dir[-1] > 0:
        direction = 'l'
    else:
        direction = 'r'
    #--------------------------------------------------------------------------------
    # Extending the trail of meteor back to its 'origin' in the sky: radiant
    if meteor_length <= 1:
        extent = tam_trilha
    else:
        extent = tam_trilha*meteor_length
    # Checking direction and settin increment
    # If meteor goes to the left
    if direction == 'l':
        increment = 0.001
    # If meteor goes to the right
    else:
        increment = -0.001
    # Calculating final RA and DEC to satisfy trail extention length
    d = 0
    x0 = ra[0]
    x1 = ra[0]
    y0 = dec[0]
    while d <= extent:
        x1 = x1 + increment
        if len(devider) != 0:
            # If least square applied to ra_0 part of devided trail
            if len(ra_0) > len(ra_1):
                y1 = m*x1 + c
            # If least square applied to ra_1
            else:
                # If meteor goes to the left
                if direction == 'l':
                    y1 = m*(x1+360) + c  # Correcting (shfting x axis further away)
                # If meteor goes to the right
                else:
                    y1 = m*(x1-360) + c  # Correcting (shfting x axis closer to 0,0)
        else:
            y1 = m*x1 + c
        X = x0 - x1
        Y = y0 - y1
        d = np.sqrt(X**2 + Y**2)
        #d = abs(d1 - d0)
    # Checking if final RA (x) value is less than 0 or grater than 360
    # Checker cross_limit remains =0 in case 0 < x < 360
    cross_limit = 0  
    if x1 < 0: 
        cross_limit = -1  # x < 0, cross_limit = -1
        #x = x + 360
    if x1 > 360:  
        cross_limit = +1  # x > 360, cross_limit = +1
        #x = x - 360
    ra_final = x1
    #--------------------------------------------------------------------------------
    # Creating extension arrays for RA and DEC
    # RA extent
    if cross_limit == 0:  # 0 < x1 (ra_final) < 360
        ra_extent = np.linspace(ra[0], ra_final, 20)
    else:
        if cross_limit == -1:  # x1 (ra_final) < 0
            ra_extent = np.linspace(ra[0], 0, 20)
            #ra_extent_1 = np.linspace(360, ra_final, 5)
            #ra_extent = np.concatenate([ra_extent_0,ra_extent_1])
        if cross_limit == 1:  # x1 (ra_final) > 360
            ra_extent = np.linspace(ra[0], 360, 20)
            #ra_extent_1 = np.linspace(0, ra_final, 5)
            #ra_extent = np.concatenate([ra_extent_0,ra_extent_1])
    # DEC extent
    dec_extent = np.array([])
    # Performing least square
    for x in ra_extent:
        dec_lstsq = m*x + c
        dec_extent = np.append(dec_extent, dec_lstsq)
    return ra_extent, dec_extent
#--------------------------------- FIM DO MODULO --------------------------------
#--------------------------------------------------------------------------------
# Criando funcao que pergunta se ponto (x_point,y_point) esta dentro de circulo de raior r e centro (x_center,y_center)
# Retorna True caso sim e False caso nao
def is_in(x_center,y_center,r,x_point,y_point):
    if np.sqrt((x_point-x_center)**2+(y_point-y_center)**2) <= r:
        return True
    else:
        return False
#--------------------------------------------------------------------------------   
# HERE STARTS THE CODE!
# Input: arquivos .txt de cada meteoro de uma noite e raio r do radiante.
# Funcionamento: corro por valores (x,y) do ceu e faco um circulo de raio r.
# Pergunto quantos meteoros estao dentro desse circulo.
# Se mais de tres, guardo o ponto (x,y).
# Eventualmente, um conjunto igual de meteoros pode satisfazer a condicao acima.
# E.g., os meteoros [m1,m2,m3] passam pelo circulo (2,6) e pelo circulo (3,6).
# Para escolher um, vejo qual circulo possui maiores seguimentos de reta definidos
# pela rota desses mesmos meteoros ao passar por dentro do circulo..
# Isso significa que o ponto (x,y) sera o "mais equidistante" se possuir retas maiores.
# Mas sera que isso e necessario? Talvez seja interessante guardar quaisquer possibilidades de
# (x,y) e analisar ao longo dos dias/meses/anos os mais recorrentes.
#--------------------------------------------------------------------------------
def radiant_seeker(capturas_da_noite, raio_radiante, minimo_radiantes_noite, string_data):
    # Captando valores minimo e maximo para ra e dec presentes nos rastros das capturas de uma noite
    # Isso reduz pontos a procurar o radiante (ao inves de correr pelo ceu inteiro)
    xmin = np.inf
    xmax = -np.inf
    ymin = np.inf
    ymax = -np.inf
    for item in capturas_da_noite:
        if min(item[1]) <= xmin:
            xmin = min(item[1])
        if max(item[1]) >= xmax:
            xmax = max(item[1])
        if min(item[2]) <= ymin:
            ymin = min(item[2])
        if max(item[2]) >= ymax:
            ymax = max(item[2])
    #--------------------------------------------------------------------------------
    # Definicoes para o codigo
    radiant_candidate = []
    # Correndo pelo valor minimo e maximo do ceu que possa conter radiantes (xmin,xmax,ymin,ymax) definidos anteriormente
    print (string_data + ' - Correndo pelo ceu...') 
    for x in np.arange(xmin,xmax,0.25):  # passo de 0.25
        for y in np.arange(ymin,ymax,0.25):  # passo de 0.25
            #print (string_data, x,y)
            # Definicoes para o codigo
            counter = []
            register = []
            # Correndo pelos meteoros da noite (dentro da pasta dia)
            for meteor in capturas_da_noite:
                # Buscando valores de ra e dec do rastro do meteoro
                for index in range(len(meteor[1])):
                    ra = meteor[1][index]
                    dec = meteor[2][index]
                    # Perguntando se ra e dec estao dentro do circulo (radiante) de centro (x,y) e raio r
                    if is_in(x,y,raio_radiante,ra,dec):
                        # Guardando valores ra,dec num contador para aquele meteoro
                        counter.append([ra,dec])
                # Perguntando se contador possui entrada de meteoros (se meteoro passa por radiante)
                if len(counter)!=0:
                    # Guardando id do meteoro e o respectivo tamanho de sua trilha
                    # que se localiza dentro do circulo radiante
                    register.append([meteor[0],len(counter)])
                    counter = []
            # Perguntando se mais de 3 meteoros passaram por aquele radiante de centro (x,y)
            if len(register)>=minimo_radiantes_noite:
                # Guardando centro do radiante (x,y) e lista dos meteoros e respectivos tamanhos de trilha
                # que estao dentro do circulo radiante
                radiant_candidate.append([[x,y],register])
    #--------------------------------------------------------------------------------
    print (string_data + ' - Analisando intersecoes...')
    # Trabalhando se ha possiveis radiantes para a noite:
    # A cada conjunto de IDs de meteoros, analisaremos todos os pares (x,y) de possiveis radiantes
    # para o conjunto mas escolheremos aquele que melhor representa o centro geometrico destes.
    if len(radiant_candidate)!=0:
        # Criando lista para conjunto de IDs dos meteoros pertencentes a um radiante (comecando com o primeiro conjunto na lista radiant_candidate)
        radiant_meteors = [list(np.array(radiant_candidate[0][1])[:,0])]
        # Criando lista para ra e dec (x,y) dos radiantes detectados para a noite analisada (comecando com o primeiro par na lista radiant_candidate)
        radiant_position = [radiant_candidate[0][0]]
        # Comparando elementos 1->2, 1->3, 1->4..., ...2->3, 2->4..., ...3->4, 3->5,..., i->j, para todo i<j.
        # O loop a seguir trabalha com todas as informacoes presentes na lista radiant_candidate
        for i in range(len(radiant_candidate)-1):
            for j in range(i+1, len(radiant_candidate)):
                # Pegando os valores relevantes dentro da lista de candidatos
                # Posicao (x,y) do radiante no ceu
                position_i=radiant_candidate[i][0]
                position_j=radiant_candidate[j][0]
                # Registro com listas de IDs de meteoros e seus tamanhos no radiante (segmentos de reta)
                # E.g.: register = [ [meteoro1, 4], [meteoro2, 7], [meteoro3, 4] ]
                register_i=radiant_candidate[i][1]
                register_j=radiant_candidate[j][1]
                # Captando IDs da lista anterior
                # E.g.: meteors = [meteoro1, meteoro2, meteoro3]
                meteors_i=np.array(register_i)[:,0]
                meteors_j=np.array(register_j)[:,0]
                # Captando tamanhos totais dos meteoros da lista anterior dentro do radiante
                # E.g.: size = 4 + 7 + 4 = 15
                size_i=np.sum(np.array(np.array(register_i)[:,1],dtype=float))
                size_j=np.sum(np.array(np.array(register_j)[:,1],dtype=float))
                # Se lista de id's do candidato_1 e identico ao do candidato_2:
                if len(meteors_i) == len(meteors_j) and False not in (meteors_i == meteors_j):
                    # Comparo tamanho de segmentos de reta referente a ambos os candidatos e escolho o maior
                    if size_i>size_j:
                        meteors=meteors_i
                        position=position_i
                    else:
                        meteors=meteors_j
                        position=position_j
                # Caso nao sejam iguais, candidato_j pode ser passivel de entrar na lista final
                else:
                    meteors=meteors_j
                    position=position_j
                # Porem pode ocorrer o caso desse mesmo conjunto de meteoros ja estar presente,
                # pois a comparacao e sempre um a um e portanto carece de informacoes globais a cada loop:
                # size_j pode ser menor que um size_i de um loop anteior, um i_old.
                # Caso esse nao seja o caso (conjunto de id's de meteoros e novo):
                if list(meteors) not in radiant_meteors:
                    radiant_meteors.append(list(meteors))
                    radiant_position.append(position)
                # Caso lista de meteoros ja exista na lista final, precisamos achar dados de i_old
                # para substitui-lo por j. Sendo assim:
                else:
                    # 0- discover a new identical meteor id's list to be compared to previous already stored
                    # on radiant_meteors. Done already. Next:
                    # 1- get its position inside radiant_meteors (that comprises meteor id's for each particular radiant).
                    # 2- with that, get its respective position (x,y) inside radiant_position.
                    # 3- use this (x,y) to find its position on the first column of the radiant_candidate array,
                    # that has the form radiant_candidate = [ [x,y], ['m1', 'm2', 'm3'] ].
                    # 4 - with this position I can use the values on the second column to compare this old size_i_old with
                    # the current size_j.
                    gen_list = []  # Creating generical list based on radiant_candidate to retrieve desired index
                    for elem in radiant_candidate:
                        gen_list.append(elem[0])
                    old_i = gen_list.index(radiant_position[radiant_meteors.index(list(meteors))])
                    position_old_i=radiant_candidate[old_i][0]
                    register_old_i=radiant_candidate[old_i][1]
                    meteors_old_i=np.array(register_old_i)[:,0]
                    size_old_i=np.sum(np.array(np.array(register_old_i)[:,1],dtype=float))
                    #
                    # Asking which radiant has more line-segment inside its circumference
                    if size_j>size_old_i:
                        # Removing previous entrance of radiant in case new radiant is bigger
                        radiant_position.remove(radiant_position[radiant_meteors.index(list(meteors))])
                        radiant_meteors.remove((list(meteors)))            
                        # Appending new lists
                        radiant_meteors.append(list(meteors))
                        radiant_position.append(position)
        # Retornando lista final com conjuntos de meteoros (IDs) e os respectivos radiantes a que cada conjunto pertence
        print (string_data, '-', len(radiant_position), 'radiante(s) encontrado(s)!')
        return radiant_meteors, radiant_position
    # Se lista radiant_candidate esta vazia, retorno duas listas tambem vazias
    else:
        print (string_data + ' - Sem radiantes para a noite')
        return [], []               
#-------------------------------- FIM DO MODULO --------------------------------
