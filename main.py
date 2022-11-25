import pymongo
from pymongo.server_api import ServerApi

import json
import redis


client = pymongo.MongoClient("mongodb+srv://Sakuragui:mmmpt2022@cluster0.xksehma.mongodb.net/mercadolivre")
db = client.test

dbRedis = redis.Redis(host='redis-11404.c244.us-east-1-2.ec2.cloud.redislabs.com',port=11404,password='P1xJBh1DwFCM8YEZdh7j8lJNkwwHwfPE')

global mydb
mydb = client.mercadolivre

print(dbRedis.get('user:name'))

def findSort():
    #Sort
    global mydb
    mycol = mydb.usuario
    print("\n####SORT####") 
    mydoc = mycol.find().sort("nome")
    for x in mydoc:
        print(x)
    
def insertVendedor(nome,email,cnpj):
    #Insert Vendedor
    global mydb
    mycol = mydb.vendedor
    print("\n####INSERT VENDEDOR####")
    mydict = { "nome": nome,"email":email,"cnpj":cnpj}
    x = mycol.insert_one(mydict)
    print(x.inserted_id)

def updateVendedor(id,nome,email,cnpj):
    #Update Vendedor
    global mydb
    mycol = mydb.vendedor
    mycol.update_one({"_id": id},{"$set":{ "nome": nome,"email":email,"cnpj":cnpj}})
    print("\n####UPDATE VENDEDOR####")

def deleteVendedor(vendedor):
    #Delete Vendedor
    global mydb
    mycol = mydb.vendedor
    mycol.delete_one(vendedor)

def insertFavorito(usuarioEmail,produto):
    json_produto = json.dumps(produto)
    
    print(json_produto)
    dbRedis.rpush(usuarioEmail+':'+'favorito',json_produto)
       
    print(dbRedis.lrange(usuarioEmail+':'+'favorito',0 ,-1))

def updateFavoritos(id,favoritos):
    mycol = mydb.usuario
    mycol.update_one({"_id": id}, {"$set":{"favoritos": favoritos}})


def sincronizarFavoritos():
    chaves = dbRedis.keys()
    for chave in chaves:
        chave = chave.decode()
        if(chave.split(":")[1] == 'favorito'):
            usuario = findUsuario(None,chave.split(":")[0])
            print(usuario)
            if usuario != None:
                print(usuario)
                updateFavoritos(usuario.get("_id"),dbRedis.lrange(chave,0,-1))
            

def insertUsuario(nome,cpf,email,senha,endereco):
    #Insert Usuario
    global mydb
    mycol = mydb.usuario
    print("\n####INSERT USUARIO####")
    mydict = { "nome": nome, "cpf":cpf,"email":email,"senha":senha,"endereco":endereco,"favoritos": []}
    x = mycol.insert_one(mydict)
    print(x.inserted_id)

def updateUsuario(id,nome,cpf,email,senha,endereco):
    #Update Usuario
    global mydb
    mycol = mydb.usuario
    mycol.update_one({"_id": id},{"$set":{"nome": nome, "cpf":cpf,"email":email,"senha":senha,"endereco":endereco }})
    print("\n####UPDATE USUARIO####")

def deleteUsuario(usuario):
    #Delete Usuario
    global mydb
    mycol = mydb.usuario
    mycol.delete_one(usuario)

def insertPromocao(tempo,produto):
    json_produto = json.dumps(produto)
    print(json_produto)
    dbRedis.set(produto.get("nome")+":promocao",json_produto,int(tempo))
    dbRedis.get(produto.get("nome")+":promocao")

def insertProduto(vendedor,nome,preco,descricao):
    #Insert Produto
    global mydb
    mycol = mydb.produto
    print("\n####INSERT PRODUTO####")
    mydict = { "vendedor_id": vendedor, "nome": nome, "preco":preco,"descricao":descricao}
    x = mycol.insert_one(mydict)
    print(x.inserted_id)

def updateProduto(id,nome,preco,descricao):
    #Update Produto
    global mydb
    mycol = mydb.produto
    mycol.update_one({"_id": id},{"$set":{ "nome": nome, "preco":preco,"descricao":descricao}})
    print("\n####UPDATE PRODUTO####")

def deleteProduto(produto):
    #Delete Produto
    global mydb
    mycol = mydb.produto
    mycol.delete_one(produto)

def findAllVendedores():
    #Query Vendedores
    global mydb
    mycol = mydb.vendedor
    print("\n####QUERY VENDEDORES####")
    vendedores = mycol.find({})
    lista = []
    for vendedor in vendedores:
        lista.append(vendedor)
    return lista

def findPromocoes():
    chaves = dbRedis.keys()
    for chave in chaves:
        chave = chave.decode()   
        if chave.split(":")[1] == "promocao":
            produto = dbRedis.get(chave)
            print("---------------------PROMOÇÃO---------------------------")
            print("Nome: " + produto.get("nome"))
            print("Preço: " + produto.get("preco"))
            print("------------------------------------------------")

def findVendedor(id,email):
    #Query Vendedor
    global mydb
    mycol = mydb.vendedor
    print("\n####QUERY VENDEDOR####")
    if id:
        myquery = { "_id": id }
    else: 
        myquery = { "email": email }
    return mycol.find_one(myquery)

def findAllUsuarios():
    #Query Vendedores
    global mydb
    mycol = mydb.usuario
    print("\n####QUERY USUARIOS####")
    usuarios = mycol.find({})
    lista = []
    for usuario in usuarios:
        lista.append(usuario)
    return lista

def findUsuario(id,email):
    #Query Usuario
    global mydb
    mycol = mydb.usuario
    print("\n####QUERY USUARIO####")
    if id:
        myquery = { "_id": id }
    else: 
        myquery = { "email": email }
    return mycol.find_one(myquery)

def findAllProdutos():
    #Query Produtos
    global mydb
    mycol = mydb.produto
    print("\n####QUERY PRODUTOS####")
    produtos = mycol.find({})
    lista = []
    for produto in produtos:
        lista.append(produto)
    return lista

def findProduto(nome,vendedor):
    #Query Produto
    global mydb
    mycol = mydb.produto
    vendedorId = findVendedor(None,vendedor).get("_id")
    print("\n####QUERY PRODUTO####")
    myquery = { "vendedor_id": vendedorId, "nome": nome }
    return mycol.find_one(myquery)

def findCompra(emailUsuario,emailVendedor):
    #Query Compra
    global mydb
    mycol = mydb.compra
    print("\n####QUERY COMPRA####")
    if emailUsuario:
        myquery = { "usuario.email":  emailUsuario }
    else: 
        myquery = { "vendedor": {"$elemMatch": {"email": emailVendedor}} }
    compras = mycol.find(myquery)
    lista = []
    for compra in compras:
        lista.append(compra)
    return lista

def insertCompra(usuario,vendedor,produto):
    #Insert Compra
    global mydb
    mycol = mydb.compra
    total = []
    for prod in produto:
        total.append(float(prod.get("preco")))

    print("\n####INSERT COMPRA####")
    mydict = { 
    "vendedor": vendedor ,
    "usuario": {"id": usuario.get("_id"), "nome": usuario.get("nome"),"email": usuario.get("email")},
    "produtos":produto,
    "total": sum(total)}
    x = mycol.insert_one(mydict)
    print(x.inserted_id)

############# main

def menu():
  
    
    loop = True
    while loop:
        print("""
            1 - Novo Usuario \n
            2 - Novo Vendedor \n 
            3 - Novo Produto \n
            4 - Realizar Compra \n
            5 - Encontrar Usuario \n
            6 - Encontrar Vendedor \n
            7 - Encontrar Produto \n
            8 - Encontrar Compra \n
            9 - Atualizar Usuario \n
            10 - Atualizar Vendedor \n
            11 - Atualizar Produto \n
            12 - Deletar Usuario \n
            13 - Deletar Vendedor \n
            14 - Deletar Produto \n
            15 - Inserir Favorito \n
            16 - Inserir Promoção \n
            17 - Encontrar Todas as Promoções \n
            20 - Sincronizar Favoritos \n
            0 - Sair \n
        """)
        escolha = input("Digite a Operação desejada: ")
        match escolha:
            case '1':
                nome = input("Insira o NOME do usuário : ")
                cpf = input("Insira o CPF do usuário: ")
                email = input("Insira o EMAIL do usuário: ")
                senha = input("Insira a SENHA do usuário: ")
                print("-----ENDEREÇO-----")
                cep = input("Insira o CEP do usuário: ")
                estado = input("Insira o ESTADO do usuário: ")
                cidade = input("Insira a CIDADE do usuário: ")
                rua = input("Insira a RUA do usuário: ")
                numero = input("Insira o NÚMERO do usuário: ")
                insertUsuario(nome,cpf,email,senha,{"cep":cep, "estado": estado, "cidade": cidade, "rua": rua, "numero": numero})
            case '2':
                nome = input("Insira o NOME do vendedor: ")
                email = input("Insira o EMAIL do vendedor: ")
                cnpj = input("Insira o CNPJ do vendedor: ")
                insertVendedor(nome,email,cnpj)
            case '3':
                index = 0
                vendedores = findAllVendedores()      

                for vendedor in vendedores:
                    print(str(index) + ' - ' + vendedor.get("nome"))
                    index = index + 1
                index =  int(input("Digite o index do vendedor desejado: "))
                vendedor = vendedores[index].get("_id")

                nomeProduto = input("Digite o nome do seu produto: ")
                precoProduto = input("Digite o preço do seu produto: ")
                descricaoProduto = input("Digite a descrição do seu produto: ")
                insertProduto(vendedor,nomeProduto, precoProduto, descricaoProduto)
            case '4':
                index = 0
                usuarios = findAllUsuarios()      

                for usuario in usuarios:
                    print(str(index) + ' - ' + usuario.get("nome"))
                    index = index + 1
                index = int(input("Digite o index do usuário desejado: "))
                usuario = usuarios[index].get("email")
                usuarioCompra = findUsuario(None,usuario)
                produtos = findAllProdutos()

                listaCompra = []
                listaProdutos = produtos
                comprando = True
                while comprando:      
                    index = 0
                    print("X - Cancelar")
                    print("P - Prosseguir ")
                    for produto in produtos:
                        print(str(index) + ' - ' + produto.get("nome"))
                        index = index + 1
                    
                    index = input("Digite o index do produto desejado: ")
                    if index == 'X':
                        comprando = False
                        break
                    elif index == 'P':
                        if len(listaCompra) == 0 :
                            print("Adicione ao menos um item na sua compra !")
                        else:
                            usuarioDict = {"_id": usuarioCompra.get("_id"), "nome": usuarioCompra.get("nome"),  "email": usuarioCompra.get("email")}
                            compras = []
                            vendedoresCompra = []

                        for compra in listaCompra:
                            produtoDict = {"_id": compra.get("_id"), "nome": compra.get("nome"),  "preco": compra.get("preco")}
                            compras.append(produtoDict)
                            vendedorCompra = findVendedor(compra.get("vendedor_id"),None)
                            vendedorDict = {"_id": vendedorCompra.get("_id"), "nome": vendedorCompra.get("nome"), "email": vendedorCompra.get("email")}
                            vendedoresCompra.append(vendedorDict)
                        
                        insertCompra(usuarioDict,vendedoresCompra,compras) 

                        comprando = False
                        break

                    else:
                        index = int(index)
                        listaCompra.append(listaProdutos[index])
                        del listaProdutos[index]
            case '5':
               print(findUsuario(None, input("Digite o email do usuário: ")))   
            case '6':
                print(findVendedor(None, input("Digite o email do vendedor: ")))   
            case '7':
                print(findProduto(input("Digite o nome do Produto: "), input("Digite o email do vendedor: ")))
            case '8':
                decisao = input("Encontrar as compras por:\n 0 - Usuário \n 1 - Vendedor \n")
                if decisao == '0':
                    print(findCompra(input("Digite o email do usuário: "), None))
                else:
                    print(findCompra(None, input("Digite o email do Vendedor: ")))
            case '9':
                index = 0
                usuarios = findAllUsuarios()      

                for usuario in usuarios:
                    print(str(index) + ' - ' + usuario.get("nome"))
                    index = index + 1
                index = int(input("Digite o index do usuário desejado: "))
                
                nome = input("Insira o NOME do usuário : ")
                cpf = input("Insira o CPF do usuário: ")
                email = input("Insira o EMAIL do usuário: ")
                senha = input("Insira a SENHA do usuário: ")
                print("-----ENDEREÇO-----")
                cep = input("Insira o CEP do usuário: ")
                estado = input("Insira o ESTADO do usuário: ")
                cidade = input("Insira a CIDADE do usuário: ")
                rua = input("Insira a RUA do usuário: ")
                numero = input("Insira o NÚMERO do usuário: ")
                updateUsuario(usuarios[index].get("_id"),nome,cpf,email,senha,{"cep":cep, "estado": estado, "cidade": cidade, "rua": rua, "numero": numero})

            case '10':
                index = 0
                vendedores = findAllVendedores()      

                for vendedor in vendedores:
                    print(str(index) + ' - ' + vendedor.get("nome"))
                    index = index + 1

                index = int(input("Digite o index do vendedor desejado: "))
                nome = input("Insira o NOME do vendedor: ")
                email = input("Insira o EMAIL do vendedor: ")
                cnpj = input("Insira o CNPJ do vendedor: ")

                updateVendedor(vendedores[index].get("_id"),nome,email,cnpj)
            case '11':
                index = 0
                produtos = findAllProdutos()
                for produto in produtos:
                    print(str(index) + ' - ' + produto.get("nome"))
                    index = index + 1
                index = int(input("Digite o index do produto desejado: "))
                nomeProduto = input("Digite o nome do seu produto: ")
                precoProduto = input("Digite o preço do seu produto: ")
                descricaoProduto = input("Digite a descrição do seu produto: ")

                updateProduto(produtos[index].get("_id"),nomeProduto,precoProduto,descricaoProduto)
            case '12':
                index = 0
                usuarios = findAllUsuarios()      

                for usuario in usuarios:
                    print(str(index) + ' - ' + usuario.get("nome"))
                    index = index + 1
                index = int(input("Digite o index do usuário desejado: "))

                deleteUsuario(usuarios[index])
            case '13':
                index = 0
                vendedores = findAllVendedores()      

                for vendedor in vendedores:
                    print(str(index) + ' - ' + vendedor.get("nome"))
                    index = index + 1

                index = int(input("Digite o index do vendedor desejado: "))

                deleteVendedor(vendedores[index])
            case '14':
                index = 0
                produtos = findAllProdutos()

                for produto in produtos:
                    print(str(index) + ' - ' + produto.get("nome"))
                    index = index + 1
                index = int(input("Digite o index do produto desejado: "))
                deleteProduto(produtos[index])    
            case '15':
                indexUsuario = 0
                usuarios = findAllUsuarios()      

                for usuario in usuarios:
                    print(str(indexUsuario) + ' - ' + usuario.get("nome"))
                    indexUsuario = indexUsuario + 1
                indexUsuario = int(input("Digite o index do usuário desejado: "))

                indexProduto = 0
                produtos = findAllProdutos()

                for produto in produtos:
                    print(str(indexProduto) + ' - ' + produto.get("nome"))
                    indexProduto = indexProduto + 1
                indexProduto = int(input("Digite o index do produto desejado: "))

                print(produtos[indexProduto].get("_id"))
               
                insertFavorito(usuarios[indexUsuario].get("email"),{"nome": produtos[indexProduto].get("nome"), "preco": produtos[indexProduto].get("preco")})
            case '16':
                index = 0
                produtos = findAllProdutos()      

                for produto in produtos:
                    print(str(index) + ' - ' + produto.get("nome"))
                    index = index + 1
                index = int(input("Digite o index do produto desejado: "))
                print(produtos[index])
                tempo = input("Digite o tempo da duração da promoção: ")
                insertPromocao(tempo,{"nome": produtos[index].get("nome"), "preco": produtos[index].get("preco")})
            case '17':
                findPromocoes()
            case '20':
                sincronizarFavoritos()
            case '0':
                print("Até a Próxima!")
                loop = False
                break
            case _ :
                print("Operação não entendida")


menu()


