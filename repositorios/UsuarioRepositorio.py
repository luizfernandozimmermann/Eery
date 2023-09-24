from save_and_load import carregar, salvar


class UsuarioRepositorio():
    def __init__(self):
        self.dados = carregar()
        
    def salvar_usuario(self, id : str, usuario : dict) -> None:
        self.dados[id] = usuario
        salvar(self.dados)
        
    def salvar_todos(self, dados : dict) -> None:
        self.dados = dados
        salvar(self.dados)
        
    def pegar_usuario(self, id : str) -> dict[str, str | int | None] | None:
        if id not in self.dados:
            return None
        return self.dados[id]
    
    def pegar_todos_usuarios(self) -> dict[str, dict[str, str | int | None]]:
        return self.dados
    
    def apagar_usuario(self, id : str):
        del self.dados[id]
        