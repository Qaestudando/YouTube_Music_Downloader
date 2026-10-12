import threading
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from album_lookup import procurar_album
from search import pesquisar, pesquisar_primeiro_resultado
from downloader import Downloader

ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('blue')
root = ctk.CTk()
root.title('YouTube Music Downloader — MP3')
root.geometry('1100x760')
status = tk.StringVar(value='Pronto — formato MP3')
videos = []
downloader = Downloader()
cancel_event = threading.Event()
trabalhando = False


def ui(func, *args):
    root.after(0, lambda: func(*args))


def log(msg):
    def escrever():
        log_area.configure(state='normal')
        log_area.insert('end', msg + '\n')
        log_area.see('end')
        log_area.configure(state='disabled')
    ui(escrever)


def finalizar(mensagem):
    global trabalhando
    trabalhando = False
    status.set(mensagem)
    btn_buscar.configure(state='normal')
    btn_baixar.configure(state='normal')
    btn_album.configure(state='normal')


def iniciar(mensagem):
    global trabalhando
    if trabalhando:
        messagebox.showinfo('Aguarde', 'Já existe uma operação em andamento.')
        return False
    trabalhando = True
    cancel_event.clear()
    status.set(mensagem)
    btn_buscar.configure(state='disabled')
    btn_baixar.configure(state='disabled')
    btn_album.configure(state='disabled')
    return True


def buscar():
    termo = entrada.get().strip()
    if not termo:
        messagebox.showwarning('Aviso', 'Digite um artista, música ou álbum.')
        return
    if not iniciar('Pesquisando...'):
        return
    videos.clear()
    for item in tree.get_children():
        tree.delete(item)

    def tarefa():
        try:
            resultados = pesquisar(termo)
            def mostrar():
                videos.extend(resultados)
                for i, video in enumerate(resultados):
                    tree.insert('', 'end', iid=str(i), values=(video['title'], video['channel']))
                finalizar(f'{len(resultados)} resultados encontrados')
            ui(mostrar)
            log(f'Busca concluída: {termo}')
        except Exception as erro:
            log(f'Erro na pesquisa: {erro}')
            ui(finalizar, 'Erro na pesquisa')
    threading.Thread(target=tarefa, daemon=True).start()


def baixar():
    selecionados = [videos[int(item)] for item in tree.selection()]
    if not selecionados:
        messagebox.showwarning('Aviso', 'Selecione pelo menos uma música.')
        return
    if not iniciar('Baixando MP3...'):
        return
    pasta = entrada.get().strip() or 'Diversos'
    barra.configure(maximum=len(selecionados), value=0)

    def tarefa():
        erros = 0
        for i, video in enumerate(selecionados, 1):
            if cancel_event.is_set():
                break
            try:
                if downloader.ja_baixado(video['id']):
                    log(f'Já baixado: {video["title"]}')
                else:
                    log(f'Baixando: {video["title"]}')
                    caminho = downloader.baixar_audio(video['id'], pasta)
                    log(f'MP3 salvo: {caminho}')
            except Exception as erro:
                erros += 1
                log(f'Erro em {video["title"]}: {erro}')
            ui(barra.configure, value=i)
        mensagem = 'Cancelado' if cancel_event.is_set() else f'Concluído — {erros} erro(s)'
        ui(finalizar, mensagem)
    threading.Thread(target=tarefa, daemon=True).start()


def baixar_album():
    selecao = tree.selection()
    if not selecao:
        messagebox.showwarning('Aviso', 'Selecione uma música para identificar o álbum.')
        return
    video = videos[int(selecao[0])]
    if not iniciar('Identificando álbum...'):
        return

    def tarefa():
        try:
            resultado = procurar_album(artista=video['channel'], musica=video['title'])
            if not resultado:
                log('Álbum não encontrado.')
                ui(finalizar, 'Álbum não encontrado')
                return
            def confirmar():
                texto = f"Artista: {resultado['artist']}\nÁlbum: {resultado['album']}\nFaixas: {len(resultado['tracks'])}\n\nBaixar em MP3?"
                if not messagebox.askyesno('Álbum encontrado', texto):
                    finalizar('Pronto')
                    return
                status.set('Baixando álbum em MP3...')
                threading.Thread(target=executar_album, args=(resultado,), daemon=True).start()
            ui(confirmar)
        except Exception as erro:
            log(f'Erro ao identificar álbum: {erro}')
            ui(finalizar, 'Erro ao identificar álbum')
    threading.Thread(target=tarefa, daemon=True).start()


def executar_album(resultado):
    try:
        downloader.baixar_album(resultado['artist'], resultado['album'], resultado['tracks'], pesquisar_primeiro_resultado, callback=log, cancelado=cancel_event.is_set)
        ui(finalizar, 'Álbum cancelado' if cancel_event.is_set() else 'Álbum concluído')
    except Exception as erro:
        log(f'Erro no álbum: {erro}')
        ui(finalizar, 'Erro no álbum')


def cancelar():
    cancel_event.set()
    status.set('Cancelando após o arquivo atual...')


topo = ctk.CTkFrame(root)
topo.pack(fill='x', padx=12, pady=12)
entrada = ctk.CTkEntry(topo, placeholder_text='Pesquisar artista, música ou álbum...')
entrada.pack(side='left', fill='x', expand=True, padx=8, pady=8)
btn_buscar = ctk.CTkButton(topo, text='Buscar', command=buscar)
btn_buscar.pack(side='left', padx=8)
entrada.bind('<Return>', lambda event: buscar())

ctk.CTkLabel(root, text='Formato de download: MP3 | Qualidade máxima configurada: 320 kbps', anchor='w').pack(fill='x', padx=18)
tree = ttk.Treeview(root, columns=('titulo', 'canal'), show='headings', selectmode='extended')
tree.heading('titulo', text='Título')
tree.heading('canal', text='Canal')
tree.column('titulo', width=740)
tree.column('canal', width=280)
tree.pack(fill='both', expand=True, padx=12, pady=10)

botoes = ctk.CTkFrame(root)
botoes.pack(fill='x', padx=12)
btn_baixar = ctk.CTkButton(botoes, text='Baixar selecionados (MP3)', command=baixar)
btn_baixar.pack(side='left', padx=6, pady=8)
btn_album = ctk.CTkButton(botoes, text='Baixar álbum completo', command=baixar_album)
btn_album.pack(side='left', padx=6)
ctk.CTkButton(botoes, text='Baixar playlist', command=lambda: messagebox.showinfo('Em desenvolvimento', 'Download de playlists ainda não implementado.')).pack(side='left', padx=6)
ctk.CTkButton(botoes, text='Cancelar', command=cancelar, fg_color='#a33232').pack(side='left', padx=6)
barra = ttk.Progressbar(root, mode='determinate')
barra.pack(fill='x', padx=12, pady=10)
ctk.CTkLabel(root, textvariable=status).pack()
log_area = tk.Text(root, height=10, state='disabled')
log_area.pack(fill='both', padx=12, pady=10)
root.mainloop()
