"""
=============================================================
  SISTEM ANTRIAN RUMAH SAKIT
  Final Project UAS - Struktur Data
  Struktur Data: Queue + Stack
  Database     : data_pasien.csv
=============================================================
"""

import csv
import os
import datetime

# ─────────────────────────────────────────────
# STRUKTUR DATA 1: QUEUE (Antrian Pasien - FIFO)
# ─────────────────────────────────────────────

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class Queue:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def enqueue(self, data):
        node = Node(data)
        if self.tail is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self.size += 1

    def dequeue(self):
        if self.is_empty():
            return None
        data = self.head.data
        self.head = self.head.next
        if self.head is None:
            self.tail = None
        self.size -= 1
        return data

    def peek(self):
        return self.head.data if self.head else None

    def is_empty(self):
        return self.size == 0

    def to_list(self):
        result, cur = [], self.head
        while cur:
            result.append(cur.data)
            cur = cur.next
        return result


# ─────────────────────────────────────────────
# STRUKTUR DATA 2: STACK (Riwayat Aksi - LIFO)
# ─────────────────────────────────────────────

class Stack:
    def __init__(self):
        self.top = None
        self.size = 0

    def push(self, data):
        node = Node(data)
        node.next = self.top
        self.top = node
        self.size += 1

    def pop(self):
        if self.is_empty():
            return None
        data = self.top.data
        self.top = self.top.next
        self.size -= 1
        return data

    def is_empty(self):
        return self.size == 0

    def to_list(self):
        result, cur = [], self.top
        while cur:
            result.append(cur.data)
            cur = cur.next
        return result


# ─────────────────────────────────────────────
# DATABASE: data_pasien.csv
# Kolom: no_antrian, nama, keluhan, poli, status, waktu_daftar
# ─────────────────────────────────────────────

CSV_FILE = "data_pasien.csv"
HEADER   = ["no_antrian", "nama", "keluhan", "poli", "status", "waktu_daftar"]

POLI = {"1": "Umum", "2": "Gigi", "3": "Anak", "4": "Jantung", "5": "Mata"}

def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            csv.writer(f).writerow(HEADER)

def baca_csv():
    with open(CSV_FILE, "r") as f:
        return list(csv.DictReader(f))

def tulis_csv(data):
    with open(CSV_FILE, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADER)
        w.writeheader()
        w.writerows(data)

def nomor_antrian_baru(semua):
    """Generate nomor antrian dari data yang ada di CSV."""
    angka = [int(p["no_antrian"][1:]) for p in semua if p["no_antrian"].startswith("A")]
    return f"A{(max(angka) + 1 if angka else 1):03d}"


# ─────────────────────────────────────────────
# STATE APLIKASI
# ─────────────────────────────────────────────

antrian = Queue()
riwayat = Stack()

def muat_antrian():
    """Load pasien berstatus 'menunggu' dari CSV ke Queue."""
    for p in baca_csv():
        if p["status"] == "menunggu":
            antrian.enqueue(p)


# ─────────────────────────────────────────────
# OPERASI CRUD
# ─────────────────────────────────────────────

def create_pasien():
    print("\n── DAFTAR PASIEN BARU ──")
    nama = input("Nama    : ").strip()
    if not nama:
        print("[!] Nama tidak boleh kosong.")
        return
    keluhan = input("Keluhan : ").strip()
    if not keluhan:
        print("[!] Keluhan tidak boleh kosong.")
        return
    print("Poli: " + "  ".join(f"{k}.{v}" for k, v in POLI.items()))
    poli = input("Pilih  : ").strip()
    if poli not in POLI:
        print("[!] Pilihan poli tidak valid.")
        return

    semua = baca_csv()
    pasien = {
        "no_antrian"  : nomor_antrian_baru(semua),
        "nama"        : nama,
        "keluhan"     : keluhan,
        "poli"        : POLI[poli],
        "status"      : "menunggu",
        "waktu_daftar": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    semua.append(pasien)
    tulis_csv(semua)
    antrian.enqueue(pasien)
    riwayat.push(f"DAFTAR  | {pasien['no_antrian']} - {pasien['nama']}")
    print(f"\n✅ Terdaftar! Nomor antrian: {pasien['no_antrian']}  (posisi ke-{antrian.size})")

def read_antrian():
    print("\n── DAFTAR ANTRIAN ──")
    daftar = antrian.to_list()
    if not daftar:
        print("[i] Antrian kosong.")
        return
    print(f"{'No':<4} {'Antrian':<10} {'Nama':<20} {'Keluhan':<20} {'Poli':<10} Waktu Daftar")
    print("─" * 80)
    for i, p in enumerate(daftar, 1):
        print(f"{i:<4} {p['no_antrian']:<10} {p['nama']:<20} {p['keluhan']:<20} {p['poli']:<10} {p['waktu_daftar']}")
    print(f"\nTotal: {antrian.size} pasien menunggu")

def read_cari():
    print("\n── CARI PASIEN ──")
    kata = input("Nama / nomor antrian : ").strip().lower()
    hasil = [p for p in baca_csv() if kata in p["nama"].lower() or kata in p["no_antrian"].lower()]
    if not hasil:
        print("[i] Tidak ditemukan.")
        return
    print(f"\n{'Antrian':<10} {'Nama':<20} {'Keluhan':<20} {'Poli':<10} {'Status':<12} Waktu")
    print("─" * 85)
    for p in hasil:
        print(f"{p['no_antrian']:<10} {p['nama']:<20} {p['keluhan']:<20} {p['poli']:<10} {p['status']:<12} {p['waktu_daftar']}")

def update_pasien():
    print("\n── UPDATE DATA PASIEN ──")
    no = input("Nomor antrian (cth: A001) : ").strip().upper()
    semua = baca_csv()
    target = next((p for p in semua if p["no_antrian"] == no and p["status"] == "menunggu"), None)
    if not target:
        print("[!] Pasien tidak ditemukan atau sudah selesai.")
        return

    print(f"  Nama: {target['nama']}  |  Keluhan: {target['keluhan']}  |  Poli: {target['poli']}")
    nama_baru    = input("Nama baru    (Enter=skip) : ").strip()
    keluhan_baru = input("Keluhan baru (Enter=skip) : ").strip()
    print("Poli baru  (Enter=skip): " + "  ".join(f"{k}.{v}" for k, v in POLI.items()))
    poli_baru = input("Pilih                     : ").strip()

    lama = dict(target)
    if nama_baru:    target["nama"]    = nama_baru
    if keluhan_baru: target["keluhan"] = keluhan_baru
    if poli_baru in POLI: target["poli"] = POLI[poli_baru]

    tulis_csv(semua)

    # Sinkronisasi node di Queue
    cur = antrian.head
    while cur:
        if cur.data["no_antrian"] == no:
            cur.data.update(target)
            break
        cur = cur.next

    riwayat.push(f"UPDATE  | {no} - {lama['nama']} → {target['nama']}")
    print("✅ Data diperbarui.")

def delete_pasien():
    print("\n── HAPUS PASIEN ──")
    no = input("Nomor antrian (cth: A001) : ").strip().upper()
    semua = baca_csv()
    target = next((p for p in semua if p["no_antrian"] == no and p["status"] == "menunggu"), None)
    if not target:
        print("[!] Pasien tidak ditemukan atau sudah selesai.")
        return

    if input(f"Hapus {target['nama']} ({no})? (y/n) : ").strip().lower() != "y":
        print("[i] Dibatalkan.")
        return

    tulis_csv([p for p in semua if p["no_antrian"] != no])

    # Rebuild queue tanpa pasien yang dihapus
    sisa = [p for p in antrian.to_list() if p["no_antrian"] != no]
    antrian.head = antrian.tail = None
    antrian.size = 0
    for p in sisa:
        antrian.enqueue(p)

    riwayat.push(f"HAPUS   | {no} - {target['nama']}")
    print(f"✅ {target['nama']} ({no}) dihapus dari antrian.")

def panggil_pasien():
    print("\n── PANGGIL PASIEN BERIKUTNYA ──")
    if antrian.is_empty():
        print("[i] Antrian kosong.")
        return
    pasien = antrian.dequeue()

    # Update status di CSV
    semua = baca_csv()
    for p in semua:
        if p["no_antrian"] == pasien["no_antrian"]:
            p["status"] = "selesai"
            break
    tulis_csv(semua)

    riwayat.push(f"PANGGIL | {pasien['no_antrian']} - {pasien['nama']}")
    print(f"\n🔔 Memanggil: {pasien['nama']}  ({pasien['no_antrian']})")
    print(f"   Keluhan  : {pasien['keluhan']}")
    print(f"   Poli     : {pasien['poli']}")
    print(f"   Sisa antrian: {antrian.size} pasien")

def lihat_riwayat():
    print("\n── RIWAYAT AKSI (STACK) ──")
    daftar = riwayat.to_list()
    if not daftar:
        print("[i] Belum ada aksi.")
        return
    for i, aksi in enumerate(daftar, 1):
        print(f"  {i}. {aksi}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def menu():
    print("\n┌────────────────────────────────┐")
    print("│    SISTEM ANTRIAN RUMAH SAKIT  │")
    print("├────────────────────────────────┤")
    print("│  1. Daftar Pasien Baru         │")
    print("│  2. Panggil Pasien Berikutnya  │")
    print("│  3. Lihat Antrian              │")
    print("│  4. Cari Pasien                │")
    print("│  5. Update Data Pasien         │")
    print("│  6. Hapus Pasien               │")
    print("│  7. Riwayat Aksi               │")
    print("│  0. Keluar                     │")
    print("└────────────────────────────────┘")

def main():
    init_csv()
    muat_antrian()
    print(f"\n✅ Sistem siap. {antrian.size} pasien dalam antrian.")

    aksi = {
        "1": create_pasien,
        "2": panggil_pasien,
        "3": read_antrian,
        "4": read_cari,
        "5": update_pasien,
        "6": delete_pasien,
        "7": lihat_riwayat,
    }

    while True:
        menu()
        pilihan = input("Pilih [0-7] : ").strip()
        if pilihan == "0":
            print("\n👋 Sistem ditutup.\n")
            break
        elif pilihan in aksi:
            aksi[pilihan]()
        else:
            print("[!] Pilihan tidak valid.")

if __name__ == "__main__":
    main()

