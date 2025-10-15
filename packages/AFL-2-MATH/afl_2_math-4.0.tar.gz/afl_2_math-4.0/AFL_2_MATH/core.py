def __hash__(self):
        return hash(tuple(sorted(map(str, self.items))))
class Himpunan:
    def __init__(self, *elemen):
        """Menyimpan elemen unik sebagai set, menerima tipe apapun (list diubah ke tuple, Himpunan disimpan langsung)"""
        processed = set()
        for el in elemen:
            if isinstance(el, list):
                processed.add(tuple(el))
            else:
                processed.add(el)
        self.items = processed

    def __hash__(self):
        return hash(tuple(sorted(map(str, self.items))))

    def __repr__(self):
        """Menampilkan isi himpunan dengan format {a, b, c}"""
        if not self.items:
            return '{}'
        tampil = ', '.join(sorted(map(str, self.items)))
        return '{' + tampil + '}'

    # ---------------- MAGIC METHODS ----------------
    def __len__(self):
        return len(self.items)

    def __contains__(self, item):
        return item in self.items

    def __eq__(self, other):
        return self.items == other.items

    def __le__(self, other):
        return self.items.issubset(other.items)

    def __lt__(self, other):
        return self.items < other.items

    def __ge__(self, other):
        return self.items.issuperset(other.items)

    def __floordiv__(self, other):
        """Ekuivalen"""
        return self.items == other.items

    def __add__(self, other):
        """Gabungan"""
        return Himpunan(*(self.items.union(other.items)))

    def __sub__(self, other):
        """Selisih"""
        return Himpunan(*(self.items.difference(other.items)))

    def __truediv__(self, other):
        """Irisan"""
        return Himpunan(*(self.items.intersection(other.items)))

    def __mul__(self, other):
        """Selisih Simetris"""
        return Himpunan(*(self.items.symmetric_difference(other.items)))

    def __pow__(self, other):
        """Cartesian Product"""
        hasil = set()
        for a in self.items:
            for b in other.items:
                hasil.add((a, b))
        return Himpunan(*hasil)

    def __abs__(self):
        """Jumlah himpunan kuasa"""
        return 2 ** len(self.items)

    def __iadd__(self, item):
        """Tambah elemen (operator +=)"""
        self.items.add(item)
        return self

    def __isub__(self, item):
        """Kurangi elemen (operator -=)"""
        self.items.discard(item)
        return self

    # ---------------- METODE TAMBAHAN ----------------
    def Komplemen(self, semesta):
        """Komplemen terhadap himpunan semesta"""
        return Himpunan(*(semesta.items - self.items))

    def ListKuasa(self):
        """Menampilkan semua subset dari himpunan"""
        elemen = list(self.items)
        n = len(elemen)
        semua_subset = []
        for i in range(2 ** n):
            subset = set()
            for j in range(n):
                if (i >> j) & 1:
                    subset.add(elemen[j])
            semua_subset.append(subset)
        return semua_subset



