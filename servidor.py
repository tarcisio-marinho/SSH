#!/bin/bash/env python
# coding=UTF-8
# by Tarcisio marinho
# github.com/tarcisio-marinho

# programas padrao
# ls
# mkdir
# upload
# copiar arquivos
# copiar pasta

import os
import datetime
import time
import socket
import sha
import subprocess
import sys


#
# AES para criptografar a senha privada
def conexao(meuIP):
    # servidor
    try:
        senha=open('senha.txt','r')
        hash_senha=senha.readline() # nova senha -> senha ja escolhida -> SHA1
    except:
        senha=open('senha.txt','w')
        nova_senha=raw_input('Digite sua senha: ') # criou nova senha para o servidor
        hash_senha=sha.new(nova_senha).hexdigest() # SHA1 da senha
        senha.write(hash_senha)
        os.system("clear")

    while True:
        porta=6064

        socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_obj.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # se der ctrl + c, ele para de escutar na porta
        socket_obj.bind((meuIP, porta))
        socket_obj.listen(1) # escuta apenas 1 cliente
        os.system('clear')
        print('Servidor rodando')


        b=0 # se o cara acertar a senha -> b=1
    	conexao,endereco=socket_obj.accept()
        hora=datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S') # hora de conexão -> unix timestamp
    	print('servidor conectado por', endereco[0],hora)
        print('gerando as chaves... ')
        while True: # TESTE PARA GERAR CHAVES CORRETAS
            try:
                palavra_teste='oi'
                gerador()
                arquivo1=open('chave_publica.txt','r')
                n=arquivo1.readline()
                n=int(n)
                e=arquivo1.readline()
                e=int(e)
                criptografado=cipher(palavra_teste,n,e)
                descriptografado=descifra(criptografado,n)
                novo=str(descriptografado)
                novo=novo.replace(']','').replace('[','').replace("'","").replace(',','').replace(' ','')
                if(novo==palavra_teste): # achou as chaves corretas -> para e vai para a conexão
                    break
                else:
                    continua_while=0
            except ValueError as e:
                print('Erro '+str(e) +'tentando proxima chave')
        # FIM DO TESTE -> achou as chaves corretas

        arquivo1=open('chave_publica.txt','r')
        n=arquivo1.readline()
        n=int(n)
        e=arquivo1.readline()
        e=int(e)
        conexao.send(b'' + str(n) +','+ str(e)) # envia pro cliente a chave publica
        # RECEBE A SENHA PARA SE CONECTAR AO SERVDIRO

        recebido=conexao.recv(1024)
        recebido=recebido.split(',')
        print(recebido)

        # DESCRIPTOGRAFA
        try:
            senha_descriptografada=[]
            novo_recebido=[]
            for caracter in recebido: # remove o L, que tem no fim dos caracteres
                caracter=caracter.replace('L','')
                novo_recebido.append(caracter) # adiciona na nova lista
            descriptografado=descifra(novo_recebido,n)
            descriptografado=str(descriptografado).replace(']','').replace('[','').replace("'","").replace(',','')
            descriptografado=descriptografado.split('  ')
            for palavra in descriptografado:
                palavra=palavra.replace(' ','')
                senha_descriptografada.append(palavra)
        except ValueError:
            #cliente saiu
            conexao.close()
            print('cliente desconectado antes de entrar')
            continue
        # FIM DESCRIPTOGRAFA

        print(senha_descriptografada)
        senha_descriptografada=str(senha_descriptografada).replace('[','').replace(']','').replace("'","")
        print(senha_descriptografada)
        hash_senha_descriptografada=sha.new(senha_descriptografada).hexdigest()

        if(hash_senha_descriptografada==hash_senha):
            conexao.send('1') # acertou a senha, pode entrar
            b=1

        else:
            print('senhas diferentes, nao pode entrar')
            conexao.send('-1') # errou a senha
            conexao.close()


        # ACERTOU A SENHA -> ENTRA NO SERVIDOR
        if(b==1):
            print('IP '+str(endereco[0])+' conectou ao servidor')
            try: # tenta abrir e escrever os clientes que foram conectados
                arq=open('logs/conectados.txt','a')
            except:
                os.mkdir('logs')
                arq=open('logs/conectados.txt','w') # cria arquivo
            arq.write(str(endereco[0])+' - '+str(hora)+'\n') # escreve no arquivo dos hosts conectados



            ###### CODIGO DE RECEBER AS CHAVES PUBLICAS DO CLIENTE
            chave_publica_cliente=conexao.recv(1024)
            chave_publica_cliente=chave_publica_cliente.split(',')


            #envia o nome de usuario que a pessoa esta logada
            logado = subprocess.check_output('whoami', shell=True)
            logado=logado.replace('\n','')
            criptografado=cipher(logado,int(chave_publica_cliente[0]),int(chave_publica_cliente[1]))
            string=str(criptografado)
            string=string.replace('[',' ').replace(']',' ').replace(' ','')
            conexao.send(string)

            # recebe dados enviados pelo cliente
            while True:
                # CRIA AS LISTAS QUE VÃO GUARDAR
                novo_descriptografado=[] # O PEDIDO DO CLIENTE DESCRIPTOGRAFADO -> COM STRING CORRETA
                novo_recebido=[] # O PEDIDO DO CLIENTE ORIGINAL
                historico=[] # HISTORICO DOS PEDIDOS DO CLIENTE

                try:
                    recebido = conexao.recv(1024) # recebe o que o cliente mandou
                except socket.error as erro:
                    print('erro '+ str(e)+', Usuario saiu\n Erro causado por PS AUX\n')
                    break
                    continue
                recebido=recebido.split(',') # separa em uma lista

                # DESCRIPTOGRAFA
                try:
                    for caracter in recebido: # remove o L, que tem no fim dos caracteres
                        caracter=caracter.replace('L','')
                        novo_recebido.append(caracter) # adiciona na nova lista
                    descriptografado=descifra(novo_recebido,n)
                    descriptografado=str(descriptografado).replace(']','').replace('[','').replace("'","").replace(',','')
                    descriptografado=descriptografado.split('  ')
                    for palavra in descriptografado:
                        palavra=palavra.replace(' ','')
                        novo_descriptografado.append(palavra)
                except ValueError:
                    #cliente saiu
                    conexao.close()
                    break
                    print('cliente escolheu sair\n')
                    continue
                # FIM DESCRIPTOGRAFA

                # tenta abrir e escrever os clientes que foram conectados
                hora=datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S')
                historico.append(str(descriptografado).replace(']','').replace('[','').replace("'","").replace(',',''))# HISTORICO DO QUE FOI ENVIADO PELO CLIENTE
                try:
                    arq=open('logs/historico.txt','a')
                except:
                    os.mkdir('logs')
                    arq=open('logs/historico.txt','w') # cria arquivo
                arq.write(str(historico)+' - ' + str(hora)+'\n')

                # pega a pergunta e executa no servidor
                tam=len(novo_descriptografado)
                print(novo_descriptografado)
                # se o usuario digitar exit
                if(str(novo_descriptografado).replace(']','').replace('[','').replace("'","").replace(',','')=='exit'):
                    conexao.send('exit')
                    conexao.close()
                    print('\nusuario escolheu sair\n')
                    break
                    continue



                comando = ' '.join([str(novo) for novo in novo_descriptografado])

                try:
                    a = subprocess.check_output(comando, shell=True)
                    conexao.send(a)
                except subprocess.CalledProcessError as e:
                    print(e)
                    conexao.send(str(e))


        conexao.close()

meuIP='127.0.0.1' # USUARIO QUE TEM QUE CONFIGURAR O IP -> PRIMEIRA VEZ RODANDO -> IFCONFIG -> INSERIR IP MANUALMENTE
conexao(meuIP)