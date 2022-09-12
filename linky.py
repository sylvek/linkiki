class Linky:
    def read(self, ser):
        """Lecture d'une trame sur le port serie specifie en entree.
        La trame debute par le caractere STX (002 h) et fini par ETX (003 h)"""
        # Lecture d'eventuel caractere avant le debut de trame
        # Jusqu'au caractere \x02 + \n (= \x0a)
        _trame = list()
        while _trame[-2:] != ['\x02', '\n']:
            _trame.append(ser.read(1))
        # Lecture de la trame jusqu'au caractere \x03
        _trame = list()
        while _trame[-1:] != ['\x03']:
            _trame.append(ser.read(1))
        # Suppression des caracteres de fin '\x03' et '\r' de la liste
        _trame.pop()
        _trame.pop()
        return self._decode("".join(_trame))

    def _decode(self, trame):
        """Decode une trame complete et renvoie un dictionnaire des elements"""
        lignes = trame.split('\r\n')
        result = {}
        for ligne in lignes:
            _tuple = self._valid(ligne)
            result[_tuple[0]] = _tuple[1]
        return result

    def _valid(self, ligne):
        """Retourne les elements d'une ligne sous forme de tuple si le checksum est ok"""
        chk = self._checksum(ligne)
        items = ligne.split(' ')
        if ligne[-1] == chk:
            return (items[0], items[1])
        else:
            raise IOError("Checksum error")

    def _checksum(self, ligne):
        """Verifie le checksum d'une ligne et retourne un tuple"""
        _sum = 0
        for ch in ligne[:-2]:
            _sum += ord(ch)
        _sum = (_sum & 63) + 32
        return chr(_sum)
