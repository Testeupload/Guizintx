import json
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
import random
import string

# Caminho para os arquivos de dados
USER_DATA_FILE = 'user_data.json'
CODE_DATA_FILE = 'codes.json'
AMAZON_LOGIN_FILE = 'amazon_logins.txt'
GMAIL_LOGIN_FILE = 'gmail_logins.txt'
OUTLOOK_LOGIN_FILE = 'outlook_logins.txt'
VISA_CARD_FILE = 'visa_live.txt'
AMEX_CARD_FILE = 'amex_live.txt'
MASTER_CARD_FILE = 'master_live.txt'
ELO_CARD_FILE = 'elo_live.txt'
AMEXUS_CARD_FILE = 'amexus_live.txt' # Arquivo para cartões Visa
ADMIN_IDS = [6764678305]  # IDs dos administradores autorizados

# IDs do grupo e canal
GROUP_ID = -1002208253806  # Substitua pelo ID real do grupo
CHANNEL_ID = '@medusah777'  # Substitua pelo username real do canal
dados = 'auxiliares.txt'



# Função para carregar os dados dos usuários do arquivo JSON
def load_user_data():
    try:
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Função para salvar os dados dos usuários no arquivo JSON
def save_user_data(user_data):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(user_data, file, indent=4)

# Função para carregar os códigos do arquivo JSON
def load_code_data():
    try:
        with open(CODE_DATA_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Função para salvar os códigos no arquivo JSON
def save_code_data(code_data):
    with open(CODE_DATA_FILE, 'w') as file:
        json.dump(code_data, file, indent=4)

# Função para gerar um código aleatório de 8 caracteres
def generate_code():
    letters = string.digits
    return ''.join(random.choice(letters) for i in range(8))

# Função para verificar se o usuário é administrador
def is_admin(user_id):
    return user_id in map(str, ADMIN_IDS)

# Função para gerar saldo e armazenar no usuário
async def gerar(update, context):
    user_id = str(update.message.from_user.id)
    
    if is_admin(user_id):
        try:
            valor = float(context.args[0])  # O valor é passado como argumento
            if valor <= 0:
                await update.message.reply_text("O valor deve ser maior que zero.")
                return
            
            code = generate_code()
            code_data = load_code_data()

            # Adiciona o código e valor ao dicionário
            code_data[code] = valor
            save_code_data(code_data)

            await update.message.reply_text(f"🏷 GIFT CARD GERADO\n📮 GIFT CARD: /resgatar {code}\n💸 VALOR: R$ {valor:.2f}\n📥 RESGATE: @DOLEST_BOT")
        except (IndexError, ValueError):
            await update.message.reply_text("Uso correto: /gerar <valor>")
    else:
        await update.message.reply_text("Você não tem permissão para usar este comando.")
# Função para resgatar saldo
async def resgatar(update, context):
    user_id = str(update.message.from_user.id)
    user_data = load_user_data()
    code_data = load_code_data()

    # Inicializa os dados do usuário se ele não estiver no dicionário
    if user_id not in user_data:
        user_data[user_id] = {'saldo': 0, 'resgatou': []}  # Inicializa ciom saldo e lista de códigos resgatados

    # Verifica se 'resgatou' está no dicionário e inicializa, se necessário
    if 'resgatou' not in user_data[user_id]:
        user_data[user_id]['resgatou'] = []

    # Verifica se o código foi fornecidoj
    try:
        code = context.args[0]
    except IndexError:
        await update.message.reply_text("Uso correto: /resgatar <código>")
        return

    # Verifica se o código é válido
    if code not in code_data:
        await update.message.reply_text("Código inválido ou já resgatado.")
        return

    # Verifica se o usuário já resgatou este código
    if code in user_data[user_id]['resgatou']:
        await update.message.reply_text("Você já resgatou este código.")
        return

    # Adiciona o saldo ao usuário e marca o código como resgatado
    valor_resgatado = code_data[code]
    user_data[user_id]['saldo'] += valor_resgatado
    user_data[user_id]['resgatou'].append(code)

    # Salva os dados do usuário
    save_user_data(user_data)

    # Remove o código do dicionário de códigos e salva
    del code_data[code]
    save_code_data(code_data)

    # Envia a mensagem de sucesso
    await update.message.reply_text(f"📮 | GIFT RESGATADO\n💸 | VALOR: R$ {valor_resgatado:.2f}.\n💰 | SALDO ATUAL: R$ {user_data[user_id]['saldo']:.2f}")

# Função para carregar logins do arquivo TXT
def load_logins(file_path):
    try:
        with open(file_path, 'r') as file:
            logins = file.readlines()
            return [tuple(line.strip().split(':')) for line in logins]
    except FileNotFoundError:
        return []

# Função para salvar logins no arquivo TXT
def save_logins(file_path, logins):
    with open(file_path, 'w') as file:
        for email, senha in logins:
            file.write(f"{email}:{senha}\n")

# Função para obter e remover o primeiro login da lista
def get_and_remove_login(file_path):
    logins = load_logins(file_path)
    if not logins:
        return None, False
    login = logins.pop(0)
    save_logins(file_path, logins)
    return login, True

# Função para carregar cartões do arquivo
def load_cards(file_path):
    try:
        with open(file_path, 'r') as file:
            cards = file.readlines()
            return [tuple(line.strip().split('|')) for line in cards]
    except FileNotFoundError:
        return []

# Função para salvar cartões no arquivo
def save_cards(file_path, cards):
    with open(file_path, 'w') as file:
        for number, month, year, cvv in cards:
            file.write(f"{number}|{month}|{year}|{cvv}\n")

# Função para obter e remover o primeiro cartão da lista
def get_and_remove_card(file_path):
    cards = load_cards(file_path)
    if not cards:
        return None, False
    card = cards.pop(0)
    save_cards(file_path, cards)
    return card, True




# Função para carregar auxiliares do arquivo
def load_auxiliares(auxiliares):
    try:
        with open(auxiliares, 'r') as file:
            lista_auxiliares = file.readlines()
            return [tuple(line.strip().split('|')) for line in lista_auxiliares]
    except FileNotFoundError:
        return []

# Função para salvar auxiliares no arquivo
def save_auxiliares(auxiliares, lista_aux):
    try:
        with open(auxiliares, 'w') as file:
            for nome, cpf in lista_aux:
                file.write(f"{nome}|{cpf}\n")
    except IOError as e:
        print(f"Erro ao salvar auxiliares: {e}")

# Função para obter e remover o primeiro auxiliar da lista
def get_and_remove_auxiliar(auxiliares):
    lista_auxiliares = load_auxiliares(auxiliares)
    if not lista_auxiliares:
        return None, False
    auxiliar = lista_auxiliares.pop(0)
    save_auxiliares(auxiliares, lista_auxiliares)
    return auxiliar, True




# Função que será executada quando o comando /start for chamado
async def start(update, context):
    chat_id = update.message.chat_id
    user_data = load_user_data()
    if str(chat_id) not in user_data:
        user_data[str(chat_id)] = {'saldo': 0}
        save_user_data(user_data)
        await context.bot.send_message(chat_id=chat_id, text="Você foi registrado para receber mensagens futuras e seu saldo inicial é 0!")
    
    image_url = 'https://imgur.com/a/MP51Jfj'
    await context.bot.send_photo(chat_id=chat_id, photo=image_url)

    keyboard = [
        [InlineKeyboardButton("🛒 COMPRAR GG", callback_data='disponivel'),
         InlineKeyboardButton("🛒 LOGIN's", callback_data='logins')],
        [InlineKeyboardButton("💸 RECARREGAR", callback_data='pagamento'),
         InlineKeyboardButton("👤 INFOR", callback_data='infor')],
        [InlineKeyboardButton("⚠️ AJUDA", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
 
    await context.bot.send_message(
        chat_id=chat_id,
        text='\n\n⚠️ | PARA ACESSAR CONTAS FREE, É NECESSÁRIO ESTÁ NO GRUPO E NO CANAL\n\n✅ | GARANTIA DE LIVE\n\n❌ | NÃO GARANTO APROVAÇÃO\n\n💳 | MATERIAL DE QUALIDADE, COM MENOR PREÇO\n\n💠 | ADICIONE O PIX MANUAL EM RECARREGAR',reply_markup=reply_markup)

# Função para lidar com os botões flutuantes
async def button(update, context):
    query = update.callback_query
    await query.answer()

    user_data = load_user_data()

    if query.data == 'disponivel':
        keyboard = [
    [
        InlineKeyboardButton("374769 | R$ 5", callback_data='amex'),
        InlineKeyboardButton("498406| R$ 5", callback_data='visa')
    ],
    [
        InlineKeyboardButton("546479 | R$ 5", callback_data='master'),
        InlineKeyboardButton("379364 | R$ 5", callback_data='amexus')
    ],
    [
        InlineKeyboardButton("SOLICITAR GG", callback_data='comprar')
    ],
    [
        InlineKeyboardButton("« Retornar ao Menu", callback_data='back_to_menu')
    ]
]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="GGS DISPONÍVEL",reply_markup=reply_markup)

    elif query.data == 'logins':
        keyboard = [
            [InlineKeyboardButton("AMAZON", callback_data='amazon'),
            
InlineKeyboardButton("OUTLOOK", callback_data='outlook'),
              InlineKeyboardButton("GMAIL", callback_data='gmail')],
            [InlineKeyboardButton("«", callback_data='back_to_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="LOGIN's DISPONÍVEIS:", reply_markup=reply_markup)

    elif query.data == 'outlook':
        user_id = str(query.from_user.id)

        if user_id in user_data and user_data[user_id]['saldo'] >= 1:
            login, success = get_and_remove_login(OUTLOOK_LOGIN_FILE)

            if success:
                email, senha = login

                user_data[user_id]['saldo'] -= 1
                save_user_data(user_data)

                keyboard = [
                    [InlineKeyboardButton("«", callback_data='back_to_menu')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(text=f"✅ | Compra Realizada Com Sucesso!\n\nEmail: {email}\nSenha: {senha:}\n\n💰 | SALDO ATUAL: R$ {user_data[user_id]['saldo']:.2f}.", reply_markup=reply_markup)
            else:
                keyboard = [
                    [InlineKeyboardButton("«", callback_data='back_to_menu')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(text="Não há logins disponíveis no momento.", reply_markup=reply_markup)
        else:
            keyboard = [
                [InlineKeyboardButton("«", callback_data='back_to_menu')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text="Saldo insuficiente, recarregue seu saldo para efetuar sua comprar.", reply_markup=reply_markup)
            
    elif query.data == 'amazon':
        user_id = str(query.from_user.id)

        if user_id in user_data and user_data[user_id]['saldo'] >= 1:
            login, success = get_and_remove_login(AMAZON_LOGIN_FILE)

            if success:
                email, senha = login

                user_data[user_id]['saldo'] -= 1
                save_user_data(user_data)

                keyboard = [
                    [InlineKeyboardButton("«", callback_data='back_to_menu')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(text=f"✅ | Compra Realizada Com Sucesso!\n\nEmail: {email}\nSenha: {senha:}\n\n💰 | SALDO ATUAL: R$ {user_data[user_id]['saldo']:.2f}", reply_markup=reply_markup)
            else:
                keyboard = [
                    [InlineKeyboardButton("VOLTAR", callback_data='back_to_menu')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(text="Não há logins disponíveis no momento.", reply_markup=reply_markup)
        else:
            keyboard = [
                [InlineKeyboardButton("«", callback_data='back_to_menu')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text="Saldo insuficiente, recarregue seu saldo para efetuar sua comprar.", reply_markup=reply_markup)

    elif query.data == 'gmail':
        user_id = str(query.from_user.id)

        if user_id in user_data and user_data[user_id]['saldo'] >= 1:
            login, success = get_and_remove_login(GMAIL_LOGIN_FILE)

            if success:
                email, senha = login

                user_data[user_id]['saldo'] -= 1
                save_user_data(user_data)

                keyboard = [
                    [InlineKeyboardButton("«", callback_data='back_to_menu')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(text=f"✅ | Compra Realizada Com Sucesso!\n\nEmail: {email}\nSenha: {senha:}\n\n💰 | SALDO ATUAL: R$ {user_data[user_id]['saldo']:.2f}.", reply_markup=reply_markup)
            else:
                keyboard = [
                    [InlineKeyboardButton("«", callback_data='back_to_menu')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(text="Não há logins disponíveis no momento.", reply_markup=reply_markup)
  

    elif query.data == 'pagamento':
        keyboard = [
            [InlineKeyboardButton("«", callback_data='back_to_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="🤖 Pix Manual: Para Adicionar Saldo Manualmente, Copie a Chave PIX Abaixo e Faça o Pagamento. Após Feito, Mande o Comprovante Para o Dono Do BOT, Assim Você Poderá Comprar Sua GG LIVE.\n\n🏦 DADOS DA CONTA 🏦\n\nNome: MONIQUE SANTOS \nChave Pix: 57cb56df-30a2-462e-84da-82a2abb25892\n\nVocê Já Fez o Pagamento, Envie o Comprovante Para Um Desses Perfis Abaixo:@DOLESTSUPREM7\n\n⚠️ Não Envie Um Valor MENOR Que R$ 5, Pois Se Você Enviar, Perderá Seu Dinheiro.",
            reply_markup=reply_markup
        )

    elif query.data == 'infor':
        user = query.from_user
        user_id = user.id

        if str(user_id) in user_data:
            saldo = user_data[str(user_id)]['saldo']
        else:
            saldo = 0

        name = user.full_name
        now = datetime.now().strftime("%d/%m/%Y\n%H:%M:%S")
        user_info_text = f"⚙️ Suas Informações:\n\n👤 Nome: {name}\n🆔 ID do Usuário: {user_id}\n📅 Data: {now.split()[0]}\n🕒 Hora: {now.split()[1]}\n\n💰 Seu Saldo Atual é: {saldo}"

        keyboard = [
            [InlineKeyboardButton("«", callback_data='back_to_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=user_info_text, reply_markup=reply_markup)

    elif query.data == 'help':
        keyboard = [
            [InlineKeyboardButton("«", callback_data='back_to_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text='Qualquer Dúvida Ou Problema Contate o Desenvolvedor:\n\n@DOLESTSUPREM7', reply_markup=reply_markup)
        
    elif query.data == 'alugar':
        keyboard = [
            [InlineKeyboardButton("«", callback_data='back_to_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text='      ALUGUEL DO CHECKER\n\nGATE: ALLBINS  | ADYEN | VBV\n\nVALORES:\n30$ Ganha 40 Creditos\n40$ Ganha 50 Creditos\n50$ Ganha 60 Creditos\n\nREVENDEDOR AUTORIZADO:\n@DOLESTSUPREM7 ', reply_markup=reply_markup)
        
    elif query.data == 'grupo':
        keyboard = [
            [InlineKeyboardButton("«", callback_data='back_to_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text='LINK DO GRUPO: https://t.me/medusahcenter777\nLINK DO CANAL: https://t.me/medusahcenter666', reply_markup=reply_markup)
        
    elif query.data == 'comprar':
        keyboard = [
            [InlineKeyboardButton("«", callback_data='back_to_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text='DISPONIVEL EM BREVE', reply_markup=reply_markup)
        
    #MASTER    
    elif query.data == 'master':
        user_id = str(query.from_user.id)

        if user_id in user_data and user_data[user_id]['saldo'] >= 5:
            card, success = get_and_remove_card(MASTER_CARD_FILE)
            auxiliar, aux_success = get_and_remove_auxiliar(dados)  # Substitua AUXILIARES_FILE pelo nome correto do seu arquivo

            if aux_success:
                nome, cpf = auxiliar
                
            if success:
                number, month, year, cvv = card

                user_data[user_id]['saldo'] -= 5
                save_user_data(user_data)

                keyboard = [
                    [InlineKeyboardButton("«", callback_data='back_to_menu')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(text=f"✅ | Compra Realizada Com Sucesso!\n\n💳 | CARTÃO: {number}\n🗓 | DATA: {month} | {year}\n🔐 | CVV: {cvv}\n\n👤 | DADOS AUXILIARES \n👤 | NOME: {nome}\n👤 | CPF: {cpf}\n\n💰 | SALDO ATUAL: R$ {user_data[user_id]['saldo']:.2f}.", reply_markup=reply_markup)
            else:
                keyboard = [
                    [InlineKeyboardButton("«", callback_data='back_to_menu')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(text="Não há cartões disponíveis no momento.", reply_markup=reply_markup)
                
     #AMEX           
    elif query.data == 'amex':
        user_id = str(query.from_user.id)

        if user_id in user_data and user_data[user_id]['saldo'] >= 5:
            card, success = get_and_remove_card(AMEX_CARD_FILE)
            auxiliar, aux_success = get_and_remove_auxiliar(dados)  # Substitua AUXILIARES_FILE pelo nome correto do seu arquivo

            if aux_success:
                nome, cpf = auxiliar
                
            if success:
                number, month, year, cvv = card

                user_data[user_id]['saldo'] -= 5
                save_user_data(user_data)

                keyboard = [
                    [InlineKeyboardButton("«", callback_data='back_to_menu')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(text=f"✅ | Compra Realizada Com Sucesso!\n\n💳 | CARTÃO: {number}\n🗓 | DATA: {month} | {year}\n🔐 | CVV: {cvv}\n\n👤 | DADOS AUXILIARES \n👤 | NOME: {nome}\n👤 | CPF: {cpf}\n\n💰 | SALDO ATUAL: R$ {user_data[user_id]['saldo']:.2f}.", reply_markup=reply_markup)
            else:
                keyboard = [
                    [InlineKeyboardButton("«", callback_data='back_to_menu')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(text="Não há cartões disponíveis no momento.", reply_markup=reply_markup)  
                
       #ELO
    elif query.data == 'elo':
        user_id = str(query.from_user.id)

        if user_id in user_data and user_data[user_id]['saldo'] >= 3:
            card, success = get_and_remove_card(ELO_CARD_FILE)
            auxiliar, aux_success = get_and_remove_auxiliar(dados)  # Substitua AUXILIARES_FILE pelo nome correto do seu arquivo

            if aux_success:
                nome, cpf = auxiliar
                
            if success:
                number, month, year, cvv = card

                user_data[user_id]['saldo'] -= 3
                save_user_data(user_data)

                keyboard = [
                    [InlineKeyboardButton("«", callback_data='back_to_menu')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(text=f"✅ | Compra Realizada Com Sucesso!\n\n💳 | CARTÃO: {number}\n🗓 | DATA: {month} | {year}\n🔐 | CVV: {cvv}\n\n👤 | DADOS AUXILIARES \n👤 | NOME: {nome}\n👤 | CPF: {cpf}\n\n💰 | SALDO ATUAL: R$ {user_data[user_id]['saldo']:.2f}.", reply_markup=reply_markup)
            else:
                keyboard = [
                    [InlineKeyboardButton("«", callback_data='back_to_menu')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(text="Não há cartões disponíveis no momento.", reply_markup=reply_markup)
        else:
            keyboard = [
                [InlineKeyboardButton("«", callback_data='back_to_menu')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text="Saldo insuficiente, recarregue seu saldo para efetuar sua comprar.", reply_markup=reply_markup)
            
#VISA
    elif query.data == 'visa':
        user_id = str(query.from_user.id)

        if user_id in user_data and user_data[user_id]['saldo'] >= 5:
            card, success = get_and_remove_card(VISA_CARD_FILE)
            auxiliar, aux_success = get_and_remove_auxiliar(dados)  # Substitua AUXILIARES_FILE pelo nome correto do seu arquivo

            if aux_success:
                nome, cpf = auxiliar
                
            if success:
                number, month, year, cvv = card

                user_data[user_id]['saldo'] -= 5
                save_user_data(user_data)

                keyboard = [
                    [InlineKeyboardButton("«", callback_data='back_to_menu')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(text=f"✅ | Compra Realizada Com Sucesso!\n\n💳 | CARTÃO: {number}\n🗓 | DATA: {month} | {year}\n🔐 | CVV: {cvv}\n\n👤 | DADOS AUXILIARES \n👤 | NOME: {nome}\n👤 | CPF: {cpf}\n\n💰 | SALDO ATUAL: R$ {user_data[user_id]['saldo']:.2f}.", reply_markup=reply_markup)
            else:
                keyboard = [
                    [InlineKeyboardButton("«", callback_data='back_to_menu')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(text="Não há cartões disponíveis no momento.", reply_markup=reply_markup)
        else:
            keyboard = [
                [InlineKeyboardButton("«", callback_data='back_to_menu')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text="Saldo insuficiente, recarregue seu saldo para efetuar sua comprar.", reply_markup=reply_markup)

    elif query.data == 'back_to_menu':
        keyboard = [
            [InlineKeyboardButton("🛒 COMPRAR GG", callback_data='disponivel'),
             InlineKeyboardButton("🛒 LOGIN's", callback_data='logins')],
            [InlineKeyboardButton("💸 RECARREGAR", callback_data='pagamento'),
             InlineKeyboardButton("👤 INFOR", callback_data='infor')],
                        [InlineKeyboardButton("⚠️ AJUDA", callback_data='help')]
                        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text='\n\n⚠️ | PARA ACESSAR CONTAS FREE, É NECESSÁRIO ESTÁ NO GRUPO E NO CANAL\n\n✅ | GARANTIA DE LIVE\n\n❌ | NÃO GARANTO APROVAÇÃO\n\n💳 | MATERIAL DE QUALIDADE, COM MENOR PREÇO\n\n💠 | ADICIONE O PIX MANUAL EM RECARREGAR',
            reply_markup=reply_markup )

# Função para adicionar saldo
async def add_saldo(update, context):
    user_id = update.message.from_user.id

    if user_id in ADMIN_IDS:
        try:
            user_id_to_update = context.args[0]
            amount = float(context.args[1])

            user_data = load_user_data()
            if user_id_to_update in user_data:
                user_data[user_id_to_update]['saldo'] += amount
                save_user_data(user_data)
                await update.message.reply_text(f"Saldo de {amount} adicionado para o usuário {user_id_to_update}.")
            else:
                await update.message.reply_text(f"Usuário {user_id_to_update} não encontrado.")
        except (IndexError, ValueError):
            await update.message.reply_text("Uso correto: /addsaldo <user_id> <quantia>")
    else:
        await update.message.reply_text("Você não tem permissão para usar este comando.")

# Função para enviar mensagem para todos os usuários
async def broadcast(update, context):
    user_id = update.message.from_user.id

    if user_id in ADMIN_IDS:
        try:
            message = " ".join(context.args)
            user_data = load_user_data()

            for user_id in user_data:
                try:
                    await context.bot.send_message(chat_id=user_id, text=message)
                except Exception as e:
                    print(f"Erro ao enviar mensagem para {user_id}: {e}")

            await update.message.reply_text("Mensagem enviada para todos os usuários.")
        except Exception as e:
            await update.message.reply_text(f"Erro ao enviar mensagem: {e}")
    else:
        await update.message.reply_text("Você não tem permissão para usar este comando.")

# Função principal para iniciar o bot
def main():
    application = Application.builder().token("7680040307:AAGJ1t9mBVbrXjZ2Jir9xlneA00mkb_NOHk").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("addsaldo", add_saldo))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("resgatar", resgatar))
    application.add_handler(CommandHandler("gerar", gerar))
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling()

if __name__ == '__main__':
    main()