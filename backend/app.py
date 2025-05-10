 # Impor fungsi konversi dari modul utils
 try:
     from utils.kalender_saka import konversi_masehi_ke_saka
 except ImportError:
     print("[ERROR app.py] Gagal mengimpor 'konversi_masehi_ke_saka' dari 'utils.kalender_saka'. Pastikan file dan path sudah benar, dan ada file '__init__.py' di folder 'utils'.")
     # Fungsi dummy jika impor gagal, agar aplikasi tetap bisa jalan untuk demo
     def konversi_masehi_ke_saka(tanggal_masehi_str):
         print("[WARNING app.py] Menggunakan fungsi konversi_masehi_ke_saka DUMMY karena impor gagal.")
         return {"tahun_saka": "N/A", "wulan_saka": "N/A", "tanggal_saka": "N/A", "pasaran_saka": "N/A", "wuku_saka": "N/A"}

 # --- Konfigurasi Aplikasi Flask ---
 # BASE_DIR adalah path absolut ke folder tempat app.py berada (yaitu 'backend')
 BASE_DIR = os.path.abspath(os.path.dirname(__file__))
 # TEMPLATE_DIR adalah path ke folder 'templates' (satu level di atas 'backend')
 TEMPLATE_DIR = os.path.join(os.path.dirname(BASE_DIR), 'templates')
 # STATIC_DIR adalah path ke folder 'static' (satu level di atas 'backend')
 STATIC_DIR = os.path.join(os.path.dirname(BASE_DIR), 'static')

 app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
 # Kunci rahasia dibutuhkan untuk fitur 'flash messages' (pesan notifikasi)
 app.secret_key = 'ganti_dengan_kunci_rahasia_acak_milik_anda' # Ganti dengan string acak Anda sendiri

 # --- Konfigurasi Penyimpanan Data ---
 DATA_DIR = os.path.join(BASE_DIR, 'data') # Path ke folder 'data' di dalam 'backend'
 DATA_FILE = os.path.join(DATA_DIR, 'pengamatan.json') # Path ke file 'pengamatan.json'

 # --- Fungsi Bantuan untuk Mengelola Data ---
 def pastikan_folder_data_ada():
     """Memastikan folder 'data' ada, jika tidak maka dibuat."""
     if not os.path.exists(DATA_DIR):
         try:
             os.makedirs(DATA_DIR)
             print(f"[INFO app.py] Folder data berhasil dibuat di: {DATA_DIR}")
         except OSError as e:
             print(f"[ERROR app.py] Gagal membuat folder data '{DATA_DIR}': {e}")
             return False
     return True

 def muat_data_pengamatan():
     """Memuat data pengamatan dari file JSON."""
     if not pastikan_folder_data_ada(): 
         return [] 
     
     if not os.path.exists(DATA_FILE):
         print(f"[INFO app.py] File data {DATA_FILE} tidak ditemukan. Membuat file baru dengan list kosong.")
         try:
             with open(DATA_FILE, 'w', encoding='utf-8') as f:
                 json.dump([], f)
             return []
         except Exception as e:
             print(f"[ERROR app.py] Gagal membuat file data awal {DATA_FILE}: {e}")
             return []
     try:
         with open(DATA_FILE, 'r', encoding='utf-8') as f:
             if os.path.getsize(DATA_FILE) == 0:
                 print(f"[INFO app.py] File data {DATA_FILE} kosong, mengembalikan list kosong.")
                 return []
             data = json.load(f)
             print(f"[INFO app.py] Berhasil memuat {len(data)} data pengamatan dari {DATA_FILE}.")
             return data
     except json.JSONDecodeError:
         print(f"[ERROR app.py] Gagal decode JSON dari {DATA_FILE}. File mungkin korup atau tidak valid. Mengembalikan list kosong.")
         return []
     except Exception as e:
         print(f"[ERROR app.py] Kesalahan tidak terduga saat memuat data dari {DATA_FILE}: {e}")
         return []

 def simpan_semua_data_pengamatan(daftar_pengamatan_lengkap):
     """Menyimpan seluruh list data pengamatan ke file JSON."""
     if not pastikan_folder_data_ada():
         print("[ERROR app.py] Tidak bisa menyimpan data karena folder data tidak bisa diakses/dibuat.")
         return False
     try:
         with open(DATA_FILE, 'w', encoding='utf-8') as f:
             json.dump(daftar_pengamatan_lengkap, f, indent=4, ensure_ascii=False)
         print(f"[INFO app.py] Data pengamatan ({len(daftar_pengamatan_lengkap)} item) berhasil disimpan ke {DATA_FILE}.")
         return True
     except Exception as e:
         print(f"[ERROR app.py] Gagal menyimpan data ke {DATA_FILE}: {e}")
         return False

 # --- Rute (Alamat URL) Aplikasi Web ---
 @app.route('/', methods=['GET', 'POST'])
 def index():
     if request.method == 'POST':
         print("[INFO app.py] Menerima request POST ke /")
         tanggal_masehi_str = request.form.get('tanggal_masehi')
         lokasi_deskripsi = request.form.get('lokasi_deskripsi')
         kategori_pengamatan = request.form.get('kategori_pengamatan')
         deskripsi_detail = request.form.get('deskripsi_detail')

         if not all([tanggal_masehi_str, lokasi_deskripsi, kategori_pengamatan, deskripsi_detail]):
             flash('Semua field wajib diisi!', 'error') 
             print("[WARNING app.py] Validasi form gagal: ada field yang kosong.")
             return redirect(url_for('index')) 

         print(f"[INFO app.py] Memanggil konversi_masehi_ke_saka untuk tanggal: {tanggal_masehi_str}")
         data_saka = konversi_masehi_ke_saka(tanggal_masehi_str)
         if not data_saka:
             flash('Gagal melakukan konversi tanggal ke Saka. Periksa format tanggal atau fungsi konversi.', 'error')
             print("[ERROR app.py] Fungsi konversi_masehi_ke_saka mengembalikan None.")
             return redirect(url_for('index'))

         pengamatan_baru = {
             "id_pengamatan": datetime.now().strftime("%Y%m%d%H%M%S%f"), 
             "tanggal_masehi_pengamatan": tanggal_masehi_str,
             "tahun_saka": data_saka.get("tahun_saka", "N/A"), 
             "wulan_saka": data_saka.get("wulan_saka", "N/A"),
             "tanggal_saka": data_saka.get("tanggal_saka", "N/A"),
             "pasaran_saka": data_saka.get("pasaran_saka", "N/A"),
             "wuku_saka": data_saka.get("wuku_saka", "N/A"),
             "lokasi_deskripsi": lokasi_deskripsi,
             "kategori_pengamatan": kategori_pengamatan,
             "deskripsi_detail": deskripsi_detail,
             "timestamp_input_data": datetime.now().isoformat() 
         }
         print(f"[INFO app.py] Data pengamatan baru yang akan disimpan: {pengamatan_baru}")

         semua_pengamatan = muat_data_pengamatan()
         semua_pengamatan.append(pengamatan_baru)
         
         if simpan_semua_data_pengamatan(semua_pengamatan):
             flash('Pengamatan berhasil disimpan!', 'success') 
         else:
             flash('Gagal menyimpan pengamatan ke file. Cek log server.', 'error') 
         
         return redirect(url_for('index')) 

     print("[INFO app.py] Menerima request GET ke /")
     daftar_pengamatan = muat_data_pengamatan()
     daftar_pengamatan_sorted = sorted(daftar_pengamatan, key=lambda x: x.get('timestamp_input_data', ''), reverse=True)
     
     tanggal_hari_ini = datetime.now().strftime("%Y-%m-%d") 
     current_year = datetime.now().year 

     return render_template('index.html', 
                            daftar_pengamatan=daftar_pengamatan_sorted, 
                            tanggal_hari_ini=tanggal_hari_ini,
                            current_year=current_year)

 # --- Bagian untuk Menjalankan Aplikasi Web ---
 if __name__ == '__main__':
     print("[INFO app.py] Memulai aplikasi Flask...")
     if not pastikan_folder_data_ada():
         print("[FATAL app.py] Tidak bisa melanjutkan karena folder data tidak bisa dibuat/diakses. Harap periksa izin folder atau path.")
     else:
         if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0 :
             simpan_semua_data_pengamatan([]) 
             print(f"[INFO app.py] File data {DATA_FILE} diinisialisasi (atau memang kosong).")
         
         app.run(debug=True, host='0.0.0.0', port=5000)
 ```