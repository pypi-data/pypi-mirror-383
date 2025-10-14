"""
Este es el modulo que incluye la clase de reproductor de musica
"""

class Player:
    """
    Esta clase crea un reproductor de musica
    """
    def play(self, song):
        """
        Reproduce la canción 
        que recibio en el parametro
        
        Parameters:
        song (stre): este es un string con el path de la canción
        
        Returns:
        int: devuelve 1 si reproduce con exito, si no devuelve 0
        """
        print("reproduciendo cancion")