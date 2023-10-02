def obter_level(xp : int):
    level = 0
    xp_requerido = 5 * (level ** 2) + (50 * level) + 100

    while xp >= xp_requerido:
        xp -= xp_requerido
        level += 1
        xp_requerido = 5 * (level ** 2) + (50 * level) + 100
    
    return (level, xp, xp_requerido)

def obter_xp(level : int):
    xp = 0
    xp_requerido = 100

    while level > 0:
        xp += xp_requerido
        level -= 1
        xp_requerido = 5 * (level ** 2) + (50 * level) + 100
    
    return xp
