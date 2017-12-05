#--------------------------------------------------------------------------------
# Importando modulos
import os
import sys
from shutil import copy
import numpy as np
import funcoes
import matplotlib.pyplot as plt
import matplotlib.patches as patches
#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------
# Pegando nome da pasta Output
# Nome da estacao
estacao = 'RJK1'
pasta = 'Output_'+estacao
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
Anos = []
Meses = []
Dias = []
Radiantes = []
colors = ['b','g','r','c','m','y']
#--------------------------------------------------------------------------------
# Criando pasta anos
arquivos_output = os.listdir(pasta)  # Recolhendo nome de todos os arquivos da pasta Output 
for item in arquivos_output:
    #
    if '20' in item:  # Evitando pastas que nao sejam anos (presenca de 20xx)
        Anos.append(pasta+'/'+item)
#
# Entrando na pasta do ano
for ano in Anos:    
    print ('---------- Iniciando', ano)
    # Criando pasta Meses
    arquivos_ano = os.listdir(ano)  # Recolhendo nome de todos os arquivos da pasta referente ao ano   
    for item in arquivos_ano:
        #
        if '.' not in item:  # Evitando pastas que nao sejam referentes ao mes e outros arquivos (presenca de '.')
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
            string_data = dia[:4]+'/'+dia[4:6]+'/'+dia[6:]
            print (string_data)
            # Criando pasta radiantes  
            pasta_dia = pasta_mes+'/'+str(dia)
            arquivos_dia = os.listdir(pasta_dia)  # Recolhendo nome de todos os arquivos da pasta referente ao mes                                            
            for item in arquivos_dia:
                #            
                if 'RA' in item:  # Evitando pastas que nao sejam referentes ao radiante (presenca de RA)
                    Radiantes.append(item)
            #
            # Entrando na pasta de radiantes
            for radiante in Radiantes:
                pasta_radiante = pasta_dia+'/'+str(radiante)
                capturas = os.listdir(pasta_radiante)
                #
                # Getting ra and dec points of the radiant
                radiante_strings = radiante.split('_')
                ra_point = np.around(float(radiante_strings[0][2:]))
                dec_point = np.around(float(radiante_strings[1][3:]))
                # Setting axis limits
                xlim0 = ra_point - fov/2.
                xlim1 = ra_point + fov/2.
                ylim0 = dec_point - fov/2.
                ylim1 = dec_point + fov/2.
                if xlim0 < 0:
                    xlim = 0
                if xlim1 > 360:
                    xlim1 = 360
                if ylim0 < -90:
                    ylim0 = -90
                if ylim1 > 90:
                    ylim1 = 90
                # Setting title 1
                title_top = 'RA:' + str(ra_point) + ' - ' + 'DEC:' + str(dec_point) + '\n'
                # Plotting radiant circle
                # Correndo pelas capturas
                k = 0
                fig = plt.figure(figsize=(10,10), dpi=100)
                circle = plt.Circle((float(radiante_strings[0][2:]), float(radiante_strings[0][2:])), raio_radiante, color='k', fill=False)
                ax = fig.add_subplot(111,aspect='equal')
                ax.add_patch(patches.Circle((float(radiante_strings[0][2:]), float(radiante_strings[1][3:])),raio_radiante,fill=False))      # remove background
                ax.plot(float(radiante_strings[0][2:]), float(radiante_strings[1][3:]),'k+')
                for captura in capturas:
                    #            
                    if '.txt' in captura:    # Analisando arquivo .txt da captura gerado pelo analyzer
                        arquivo = open(pasta_radiante+'/'+captura)     # Abrindo arquivo
                        linhas_arquivo = arquivo.readlines()     # Lendo linhas do arquivo
                        # CHAMANDO MODULO meteor_reader dentro de funcoes.py
                        meteor_trail, meteor_id = funcoes.meteor_reader(linhas_arquivo, captura)  # Lendo trilha deixada pelo meteoro e id da captura
                        arquivo.close()    # Fechando arquivo
                        # CHAMANDO MODULO meteor_path dentro de funcoes.py
                        ra_extent, dec_extent = funcoes.meteor_path(meteor_trail, tam_trilha)  # Recolhendo trilha extendida (ate possivel radiante)
                        # Gerrint ra and dec points of meteor in the sky
                        meteor_trail=np.array(meteor_trail)
                        ra_meteor = meteor_trail[:,0]
                        dec_meteor = meteor_trail[:,1]
                        # Plotting meteor trail
                        ax.plot(ra_meteor, dec_meteor, colors[k]+'+', label=meteor_id)
                        # Plotting meteor trail extent
                        ax.plot(ra_extent, dec_extent, colors[k]+'--')
                        #
                        ax.legend(loc="upper right", shadow=True, title="Meteors", fancybox=True)
                        #plt.legend(loc="upper right")
                        k=k+1
                # Adding circle for radiant
                #ax.add_artist(circle)
                # Setting title 2
                title_bott = string_data + ': ' + str(k) + ' meteoros'
                # Setting axis limits
                plt.xlim(xlim0, xlim1)
                plt.ylim(ylim0, ylim1)
                # Plotting and saving figure
                plt.title(title_top + title_bott)
                fig.savefig(pasta_radiante+'/'+str(ra_point)+'_'+str(dec_point)+'.png',bbox_inches='tight')
                fig.savefig(pasta+'/'+str(ra_point)+'_'+str(dec_point)+'.png',bbox_inches='tight')
                fig.clear()
                plt.close()
            #--------------------------------------------------------------------------------
            Radiantes = []
        #
        Dias = []    # Resetando lista de dias para proximo mes
    #
    Meses = []     # Resetando lista de meses para proximo ano
#
Anos = []
# ------------------------------- FIM DO PROGRAMA -------------------------------
print ('Fim!')
