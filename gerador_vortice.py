import pandas as pd
import qrcode
import os
import gspread
import git
from oauth2client.service_account import ServiceAccountCredentials

# CONFIGURAÇÃO VORTICE
BASE_URL = "https://vortice-hub.github.io/p/" 

def enviar_ao_github():
    try:
        repo = git.Repo(os.getcwd(), search_parent_directories=True)
        print("📤 Enviando para o GitHub automaticamente...")
        repo.git.add(all=True)
        
        if repo.is_dirty(untracked_files=True):
            repo.index.commit("Vortice Engine: Atualização automática Premium")
            origin = repo.remote(name='origin')
            origin.push()
            print("🚀 GitHub atualizado com sucesso!")
        else:
            print("✨ Nada novo para enviar, tudo atualizado!")
            
    except Exception as e:
        print(f"⚠️ Erro ao sincronizar: {e}")

def fabricar_vortice():
    # 1. Conexão com Google Sheets
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
    try:
        print("🔑 Acessando nuvem de dados...")
        creds = ServiceAccountCredentials.from_json_keyfile_name('credenciais.json', scope)
        client = gspread.authorize(creds)
        planilha = client.open("Respostas_Vortice").sheet1
        dados = planilha.get_all_records()
        df = pd.DataFrame(dados)
        df.columns = [str(c).strip().lower() for c in df.columns]
    except Exception as e:
        print(f"❌ Erro na planilha: {e}")
        return

    # 2. Carregar Template
    if not os.path.exists('index.html'):
        print("❌ Erro: index.html não encontrado.")
        return
        
    with open('index.html', 'r', encoding='utf-8') as f:
        template = f.read()

    # 3. Gerar Arquivos
    for index, cliente in df.iterrows():
        nome = str(cliente.get('nome', 'Cliente')).strip()
        slug = nome.lower().replace(" ", "_")
        
        # Criando pasta para cada cliente
        caminho_cliente = f"p/{slug}" 
        if not os.path.exists(caminho_cliente): os.makedirs(caminho_cliente)

        # 3.1 vCard (Arquivo de contatos)
        vcf_nome = f"{slug}.vcf"
        vcard = f"BEGIN:VCARD\nVERSION:3.0\nFN:{nome}\nTEL:{cliente.get('telefone','')}\nEMAIL:{cliente.get('email','')}\nEND:VCARD"
        with open(f"{caminho_cliente}/{vcf_nome}", 'w', encoding='utf-8') as f:
            f.write(vcard)

        # 3.2 QR Code
        qr_nome = f"{slug}_qr.png"
        qrcode.make(BASE_URL + slug + "/").save(f"{caminho_cliente}/{qr_nome}")

        # 3.3 HTML Final (Substituindo as tags do design premium)
        html_final = template.replace("{{NOME}}", nome)\
                             .replace("{{CARGO}}", str(cliente.get('cargo', '')))\
                             .replace("{{TELEFONE}}", str(cliente.get('telefone', '')))\
                             .replace("{{INSTAGRAM}}", str(cliente.get('instagram', '')))\
                             .replace("{{LINKEDIN}}", str(cliente.get('linkedin', '')))\
                             .replace("{{EMAIL}}", str(cliente.get('email', '')))\
                             .replace("{{VCF_ARQUIVO}}", vcf_nome)\
                             .replace("{{QR_CODE}}", qr_nome)\
                             .replace("{{FOTO}}", "https://i.pravatar.cc/150")

        with open(f"{caminho_cliente}/index.html", 'w', encoding='utf-8') as f:
            f.write(html_final)
        
        print(f"✅ Vórtice Premium Gerado: {nome}")

    # 4. Sincronizar com GitHub
    enviar_ao_github()

if __name__ == "__main__":
    fabricar_vortice()