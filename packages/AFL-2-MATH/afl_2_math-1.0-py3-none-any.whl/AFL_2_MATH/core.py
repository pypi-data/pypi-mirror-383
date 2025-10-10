class Himpunan:
    def __init__(self, *elemen):
        """Menyimpan elemen unik sebagai set"""
        self.items = set(elemen)

    def __repr__(self):
        """Menampilkan isi himpunan dengan format {a, b, c}"""
        return '{' + ', '.join(map(str, sorted(self.items))) + '}'

    # ---------------- MAGIC METHODS ----------------
    def __len__(self):
        """Mengembalikan jumlah elemen"""
        return len(self.items)

    def __contains__(self, item):
        """Cek apakah elemen ada dalam himpunan"""
        return item in self.items

    def __eq__(self, other):
        """Cek apakah dua himpunan sama"""
        return self.items == other.items

    def __le__(self, other):
        """Cek subset"""
        return self.items.issubset(other.items)

    def __lt__(self, other):
        """Cek proper subset"""
        return self.items < other.items

    def __ge__(self, other):
        """Cek superset"""
        return self.items.issuperset(other.items)

    def __floordiv__(self, other):
        """Cek ekuivalen"""
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
