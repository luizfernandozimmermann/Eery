from disnake import Member


class Usuario(Member):
    def __init__(self, disnake_user : Member):
        ret = {slot: getattr(disnake_user, slot) for slot in disnake_user.__slots__}
        for cls in type(disnake_user).mro():
            spr = super(cls, disnake_user)
            if not hasattr(spr, '__slots__'):
                break
            for slot in spr.__slots__:
                ret[slot] = getattr(disnake_user, slot)
                
        for nome, valor in ret.items():
            setattr(self, nome, valor)
        
        self.nome : str | None = None
        self.aniversario : str | None = None
        self.estado : str | None = None
        self.twitter : str | None = None
        self.twitch : str | None = None
        self.lista_animes : str | None = None
        self.steam : str | None = None
        self.instagram : str | None = None
        self.osu : str | None = None
        self.genshin_uid : str | None = None
        self.bruno_points : int = 0
        self.xp : int = 0
        self.time : str | None = None
        self.honkai_uid : str | None = None
        