import threading
import tkinter as tk
from tkinter import ttk, messagebox
from album_lookup import procurar_album
import customtkinter as ctk

from search import pesquisar, pesquisar_primeiro_resultado
from album_lookup import procurar_album
from search import pesquisar
from downloader import Downloader

# =========================
# Configuração da interface
# =========================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("YouTube Music Downloader")
root.geometry("1200x800")

videos = []
cancelar_download = False

downloader = Downloader()

status = tk.StringVar(value="Pronto")


# =========================
# Utilidades
# =========================

def adicionar_log(texto):
    log.configure(state="normal")
    log.insert("end", texto + "\n")
    log.see("end")
    log.configure(state="disabled")


# =========================
# Busca
# =========================

def buscar():

    termo = entrada_busca.get().strip()

    if not termo:
        messagebox.showwarning(
            "Aviso",
            "Digite um artista, música ou álbum."
        )
        return

    status.set("Pesquisando...")

    videos.clear()

    for item in tree.get_children():
        tree.delete(item)

    try:

        resultados = pesquisar(termo)

        videos.extend(resultados)

        for video in resultados:

            tree.insert(
                "",
                "end",
                values=(
                    video["title"],
                    video["channel"]
                )
            )

        status.set(f"{len(resultados)} resultados encontrados")
        adicionar_log(f"Busca concluída: {termo}")

    except Exception as erro:

        messagebox.showerror(
            "Erro",
            str(erro)
        )

        status.set("Erro na pesquisa")


# =========================
# Download selecionados
# =========================

def baixar():

    global cancelar_download

    cancelar_download = False

    selecionados = tree.selection()

    if not selecionados:
        messagebox.showwarning(
            "Aviso",
            "Selecione pelo menos uma música."
        )
        return

    termo = entrada_busca.get().strip()

    barra.configure(maximum=len(selecionados))
    barra["value"] = 0

    def tarefa():

        concluido = 0

        for item in selecionados:

            if cancelar_download:
                adicionar_log("Download cancelado.")
                status.set("Cancelado")
                return

            indice = tree.index(item)
            video = videos[indice]

            try:

                adicionar_log(
                    f"Baixando: {video['title']}"
                )

                if downloader.ja_baixado(video["id"]):
                    adicionar_log(f"Já baixado: {video['title']}")
                else:
                    downloader.baixar_audio(
                                video["id"],
                                termo
                        )
                downloader.marcar_baixado(
                    video["id"]
                )

                downloader.marcar_baixado(
                    video["id"]
                )

                adicionar_log(
                    f"Concluído: {video['title']}"
                )

            except Exception as erro:

                adicionar_log(
                    f"Erro: {erro}"
                )

            concluido += 1
            barra["value"] = concluido

        status.set("Downloads concluídos")

    threading.Thread(
        target=tarefa,
        daemon=True
    ).start()


# =========================
# Baixar álbum
# =========================

def baixar_album():

    selecionados = tree.selection()

    if not selecionados:
        messagebox.showwarning(
            "Aviso",
            "Selecione uma música."
        )
        return

    indice = tree.index(selecionados[0])
    video = videos[indice]

    titulo = video["title"]
    artista = video["channel"]

    status.set("Procurando álbum...")

    resultado = procurar_album(
        artista=artista,
        musica=titulo
    )

    if resultado is None:

        messagebox.showinfo(
            "Álbum não encontrado",
            "Não foi possível identificar o álbum."
        )

        status.set("Pronto")

        return

    confirmar = messagebox.askyesno(
        "Álbum encontrado",
        (
            f"Artista: {resultado['artist']}\n"
            f"Álbum: {resultado['album']}\n"
            f"Ano: {resultado['year']}\n\n"
            f"Faixas: {len(resultado['tracks'])}\n\n"
            "Deseja baixar o álbum completo?"
        )
    )

    if not confirmar:
        status.set("Pronto")
        return

    status.set("Baixando álbum...")

    def tarefa():

        downloader.baixar_album(
            artista=resultado["artist"],
            album=resultado["album"],
            faixas=resultado["tracks"],
            pesquisar_funcao=pesquisar_primeiro_resultado
        )

        status.set("Álbum concluído")

        adicionar_log(
            f"Álbum baixado: {resultado['album']}"
        )

    threading.Thread(
        target=tarefa,
        daemon=True
    ).start()

# =========================
# Baixar playlist
# =========================

def baixar_playlist():

    messagebox.showinfo(
        "Em desenvolvimento",
        "Esta função será implementada na próxima etapa."
    )


# =========================
# Cancelar
# =========================

def cancelar():

    global cancelar_download

    cancelar_download = True

    status.set("Cancelando...")


# =========================
# Interface
# =========================

topo = ctk.CTkFrame(root)
topo.pack(fill="x", padx=10, pady=10)

entrada_busca = ctk.CTkEntry(
    topo,
    placeholder_text="Digite artista, música ou álbum..."
)

entrada_busca.pack(
    side="left",
    fill="x",
    expand=True,
    padx=5
)

btn_buscar = ctk.CTkButton(
    topo,
    text="Buscar",
    command=buscar
)

btn_buscar.pack(side="left")

tree = ttk.Treeview(
    root,
    columns=("titulo", "canal"),
    show="headings",
    selectmode="extended"
)

tree.heading("titulo", text="Título")
tree.heading("canal", text="Canal")

tree.column("titulo", width=750)
tree.column("canal", width=300)

tree.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)

frame_botoes = ctk.CTkFrame(root)
frame_botoes.pack(fill="x", padx=10)

ctk.CTkButton(
    frame_botoes,
    text="Baixar Selecionados",
    command=baixar
).pack(side="left", padx=5, pady=5)

ctk.CTkButton(
    frame_botoes,
    text="Baixar Álbum Completo",
    command=baixar_album
).pack(side="left", padx=5, pady=5)

ctk.CTkButton(
    frame_botoes,
    text="Baixar Playlist",
    command=baixar_playlist
).pack(side="left", padx=5, pady=5)

ctk.CTkButton(
    frame_botoes,
    text="Cancelar",
    command=cancelar
).pack(side="left", padx=5, pady=5)

barra = ttk.Progressbar(
    root,
    mode="determinate"
)

barra.pack(fill="x", padx=10, pady=10)

ttk.Label(
    root,
    textvariable=status
).pack()

log = tk.Text(
    root,
    height=10,
    state="disabled"
)

log.pack(
    fill="both",
    expand=False,
    padx=10,
    pady=10
)

root.mainloop()