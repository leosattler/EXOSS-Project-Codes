#--------------------------------------------------------------------------------
# Importando modulos
import os
import sys
from shutil import copy
import numpy as np
import funcoes
#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------
# Nome da estacao
estacao = 'RJK1'
# Escolhendo anos e meses a serem escaneados
Anos = ['2016','2017']
# Field of View da estacao
fov = 50.
# Escolhendo numero minimo de capturs a serem consideradas por noite
minimo_radiantes_noite = 2
# Escolhendo raio do radiante no ceu (em graus) 
raio_radiante = 2
# Escolhendo tamanho da trilha (ira multiplicar extensao linear do meteoro)
tam_trilha = 3 
#--------------------------------------------------------------------------------
# Definicoes para o codigo
Meses = []
Dias = []
capturas_da_noite = []
radiante_meteoros = []
radiante_posicoes = []
#
meteoros_counter = 0
radiantes_counter = 0
#
output = 'Output' + '_' + estacao 
if os.path.exists(output):
    if os.listdir(output):
        print ('Pasta Output nao esta vazia. Delete-a para continuar.')
        sys.exit()
    else:
        os.rmdir(output)
os.mkdir(output)
#--------------------------------------------------------------------------------
# Entrando na pasta do ano
for ano in Anos:    
    print ('---------- Iniciando', ano)
    # Criando pasta Meses
    arquivos_ano = os.listdir(ano)  # Recolhendo nome de todos os arquivos da pasta referente ao ano   
    for item in arquivos_ano:
        #
        if ano in item and '.' not in item:  # Evitando pastas que nao sejam referentes ao mes e outros arquivos (presenca de '.')
            Meses.append(item)
    #
    # Entrando na pasta do mes
    for mes in Meses:    
        print ('---------- Iniciando', mes[:4]+'/'+mes[4:])
        # Criando pasta dias
        pasta_mes = str(ano)+'/'+str(mes)  
        arquivos_mes = os.listdir(pasta_mes)  # Recolhendo nome de todos os arquivos da pasta referente ao mes                                            
        for item in arquivos_mes:
            #            
            if mes in item and '.' not in item:  # Evitando pastas que nao sejam referentes ao dia e tabelas de analise (presenca de '.') 
                Dias.append(item) 
        #
        # Entrando na pasta do dia
        for dia in Dias:    
            # String da data para display
            string_data = dia[:4]+'/'+dia[4:6]+'/'+dia[6:]
            # Perguntando se noite de captura possui arquivos suficientes
            if len(os.listdir(pasta_mes+'/'+dia)) >= minimo_radiantes_noite * 8: # x8 pois ha 8 arquivos p/ cada captura
                #--------------------------------------------------------------------------------
                # Iniciando busca caso noite contenha capturas suficientes
                for captura in os.listdir(pasta_mes+'/'+dia):    # Correndo por arquivos das capturas na pasta do dia
                    #            
                    if '.txt' in captura:    # Analisando arquivo .txt da captura gerado pelo analyzer
                        meteoros_counter = meteoros_counter + 1
                        arquivo = open(pasta_mes+'/'+dia+'/'+captura)     # Abrindo arquivo
                        linhas_arquivo = arquivo.readlines()     # Lendo linhas do arquivo
                        # CHAMANDO MODULO meteor_reader dentro de funcoes.py
                        meteor_trail, meteor_id = funcoes.meteor_reader(linhas_arquivo, captura)  # Lendo trilha deixada pelo meteoro e id da captura
                        arquivo.close()    # Fechando arquivo
                        # Perguntando se captura possui mais de 2 pontos no ceu (meteor_reader retorna lista vazia caso nao)
                        if len(meteor_trail) != 0: 
                            # CHAMANDO MODULO meteor_path dentro de funcoes.py
                            ra_extent, dec_extent = funcoes.meteor_path(meteor_trail, tam_trilha)  # Recolhendo trilha extendida (ate possivel radiante)
                            capturas_da_noite.append([meteor_id, ra_extent, dec_extent])
                # Evitando caso em que ainda nao ha arquivos de analise na pasta (caturas_da_noite se mante vazia)
                if len(capturas_da_noite) != 0:
                    # CHAMANDO MODULO radiant_seeker dentro de funcoes.py
                    print (string_data + ' - Buscando radiantes')
                    radiante_meteoros, radiante_posicoes = funcoes.radiant_seeker(capturas_da_noite, raio_radiante, minimo_radiantes_noite, string_data)    # Obtendo possiveis radiantes encontrados para a noite: conjunto de IDs e posicoes
                    radiantes_counter = radiantes_counter + len(radiante_posicoes) 
                    capturas_da_noite = []    # Resetando lista de capturas da noite para proximo dia
            # Pulando data caso noite nao tenha capturas suficientes
            else:
                print (string_data + ' - Sem capturas suficientes para a noite')
            print ('----------')
            #--------------------------------------------------------------------------------
            # Criando pastas dentro da pasta Output (seguindo mesmo padrao ano/mes/dia da pasta !Data)
            # Isso apenas se radiante_meteoros e radiante_posicoes nao estiverem vazios (ou seja, radiante foi encontrado para o dia em qestao)
            if len(radiante_meteoros)!=0:
                #sys.exit()
                # Criando Output/ano (caso nao exista)
                if os.path.exists(output+'/'+ano) == False: 
                    os.mkdir(output+'/'+ano)
                # Criando Output/ano/mes (caso nao exista)
                if os.path.exists(output+'/'+pasta_mes) == False: 
                    os.mkdir(output+'/'+pasta_mes)
                # Criando Output/ano/mes/dia (caso nao exista)
                if os.path.exists(output+'/'+pasta_mes+'/'+dia) == False: 
                    os.mkdir(output+'/'+pasta_mes+'/'+dia)
                # Operando sobre lista de posicoes de radiantes para o dia em questao
                for index in range(len(radiante_posicoes)):
                    ra_dec = radiante_posicoes[index]
                    pasta = 'RA'+str(ra_dec[0])+'_DEC'+str(ra_dec[1])
                    # Criando Output/ano/mes/dia/radiante_ra_dec
                    os.mkdir(output+'/'+pasta_mes+'/'+dia+'/'+pasta)
                    # Copiando arquivos .txt e .jpg (referente aos IDs) da pasta !Data/ano/mes/dia para Output/ano/mes/dia/radiante_ra_dec
                    for meteor_id in radiante_meteoros[index]:
                        for item in os.listdir(pasta_mes+'/'+dia):
                            if meteor_id in item and '.txt' in item:
                                copy(pasta_mes+'/'+dia+'/'+item, output+'/'+pasta_mes+'/'+dia+'/'+pasta)
                            if meteor_id in item and 'P.jpg' in item:
                                copy(pasta_mes+'/'+dia+'/'+item, output+'/'+pasta_mes+'/'+dia+'/'+pasta)
            # Resetando pasta de radiantes
            radiante_meteoros = []
            radiante_posicoes = []
        #
        Dias = []    # Resetando lista de dias para proximo mes
    #
    Meses = []     # Resetando lista de meses para proximo ano
# ------------------------------- FIM DO PROGRAMA -------------------------------
file = open(output+'/'+estacao+'.txt', 'a')
file.write('estacao = '+estacao+'\n')
file.write('Anos = '+str(Anos)+'\n')
file.write('fov = '+str(fov)+'\n')
file.write('minimo_radiantes_noite = '+str(minimo_radiantes_noite)+'\n')
file.write('raio_radiante = '+str(raio_radiante)+'\n')
file.write('tam_trilha = '+str(tam_trilha)+'\n')
file.write('N total de meteoros analisados = '+str(meteoros_counter)+'\n')
file.write('N total de radiantes = '+str(radiantes_counter)+'\n')
file.close()
print ('Fim!')
