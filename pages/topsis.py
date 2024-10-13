import streamlit as st
import pandas as pd
import numpy as np

# Fungsi untuk normalisasi matriks keputusan
def normalize_matrix(matrix):
    return matrix / np.sqrt((matrix**2).sum(axis=0))

# Fungsi untuk menghitung jarak ke solusi ideal positif dan negatif
def calculate_distance(matrix, ideal_solution):
    return np.sqrt(((matrix - ideal_solution) ** 2).sum(axis=1))

# Fungsi utama untuk perhitungan TOPSIS
def topsis(vendor_data, weights, is_benefit_criteria):
    # 1. Normalisasi matriks keputusan
    normalized_matrix = normalize_matrix(vendor_data.iloc[:, 1:].astype(float))
    st.subheader('Matriks Normalisasi')
    st.write(normalized_matrix)

    # 2. Normalisasi bobot
    weighted_matrix = normalized_matrix * weights
    st.subheader('Matriks Bobot')
    st.write(weighted_matrix)

    # 3. Solusi ideal positif dan negatif
    ideal_positive = np.zeros(weighted_matrix.shape[1])
    ideal_negative = np.zeros(weighted_matrix.shape[1])

    for i in range(weighted_matrix.shape[1]):
        if is_benefit_criteria[i]:
            ideal_positive[i] = weighted_matrix.iloc[:, i].max()  # Benefit criteria
            ideal_negative[i] = weighted_matrix.iloc[:, i].min()  # Benefit criteria
        else:
            ideal_positive[i] = weighted_matrix.iloc[:, i].min()  # Cost criteria
            ideal_negative[i] = weighted_matrix.iloc[:, i].max()  # Cost criteria

    st.subheader('Solusi Ideal Positif dan Negatif')
    ideal_df = pd.DataFrame({
        'Kriteria': vendor_data.columns[1:],  # Mengambil nama kriteria dari vendor_data
        'Ideal Positif': ideal_positive,
        'Ideal Negatif': ideal_negative
    })
    st.write(ideal_df)

    # 4. Menghitung jarak ke solusi ideal positif dan negatif
    distance_to_positive = calculate_distance(weighted_matrix, ideal_positive)
    distance_to_negative = calculate_distance(weighted_matrix, ideal_negative)

    st.subheader('Jarak ke Solusi Ideal Positif dan Negatif')
    distance_df = pd.DataFrame({
        'Vendor': vendor_data['index'],
        'Jarak ke Solusi Ideal Positif': distance_to_positive,
        'Jarak ke Solusi Ideal Negatif': distance_to_negative
    })
    st.write(distance_df)

    # 5. Menghitung kedekatan relatif dengan solusi ideal positif
    relative_closeness = distance_to_negative / (distance_to_positive + distance_to_negative)

    # Menambahkan hasil ke dataframe
    vendor_data['Closeness Coefficient'] = relative_closeness
    vendor_data['Ranking'] = vendor_data['Closeness Coefficient'].rank(ascending=False, method='min').astype(int)

    # Kesimpulan berdasarkan ranking
    vendor_data['Kesimpulan'] = ''
    for index, row in vendor_data.iterrows():
        if row['Ranking'] == 1:
            vendor_data.at[index, 'Kesimpulan'] = 'Merupakan vendor terpilih'
        else:
            vendor_data.at[index, 'Kesimpulan'] = f'Tidak terpilih, ranking {row["Ranking"]}'

    return vendor_data

# Inisialisasi session_state
if 'vendor_data' not in st.session_state:
    st.session_state.vendor_data = pd.DataFrame()
if 'weights' not in st.session_state:
    st.session_state.weights = []
if 'is_benefit_criteria' not in st.session_state:
    st.session_state.is_benefit_criteria = []
if 'topsis_result' not in st.session_state:
    st.session_state.topsis_result = pd.DataFrame()

# Judul aplikasi
st.title('Implementasi TOPSIS Manual dengan Streamlit')

# Input di Sidebar
st.sidebar.header("Input Data TOPSIS")

# Input jumlah vendor dan kriteria
num_vendors = st.sidebar.number_input('Masukkan jumlah vendor', min_value=2, step=1)
num_criteria = st.sidebar.number_input('Masukkan jumlah kriteria', min_value=2, step=1)

# Input nama vendor
vendors = []
for i in range(num_vendors):
    vendor = st.sidebar.text_input(f'Nama Vendor {i+1}', f'Vendor {i+1}')
    vendors.append(vendor)

# Input nama kriteria
criteria = []
for j in range(num_criteria):
    criterion = st.sidebar.text_input(f'Nama Kriteria {j+1}', f'C{j+1}')
    criteria.append(criterion)

# Input bobot kriteria
weights = []
st.sidebar.subheader('Masukkan bobot untuk masing-masing kriteria')
for j in range(num_criteria):
    weight = st.sidebar.number_input(f'Bobot untuk {criteria[j]}', min_value=0.0, max_value=1.0, step=0.01)
    weights.append(weight)

# Tentukan apakah kriteria adalah benefit atau cost
is_benefit_criteria = []
st.sidebar.subheader('Tentukan apakah kriteria ini benefit atau cost')
for j in range(num_criteria):
    is_benefit = st.sidebar.radio(f'{criteria[j]} adalah:', ['Benefit', 'Cost'], index=0)
    is_benefit_criteria.append(is_benefit == 'Benefit')

# Input nilai tiap vendor pada setiap kriteria
vendor_data = pd.DataFrame(index=vendors, columns=criteria)
for i in range(num_vendors):
    for j in range(num_criteria):
        score = st.sidebar.number_input(f'Nilai {vendors[i]} untuk {criteria[j]}', min_value=0.0, step=0.1)
        vendor_data.loc[vendors[i], criteria[j]] = score

# Simpan data ke session_state
if st.sidebar.button('Simpan Data'):
    st.session_state.vendor_data = vendor_data.astype(float)
    st.session_state.weights = np.array(weights)
    st.session_state.is_benefit_criteria = is_benefit_criteria
    st.success("Data berhasil disimpan!")

# Menjalankan TOPSIS jika data sudah lengkap
if st.sidebar.button('Hitung TOPSIS') and not st.session_state.vendor_data.empty:
    result = topsis(st.session_state.vendor_data.reset_index(), st.session_state.weights, st.session_state.is_benefit_criteria)
    st.session_state.topsis_result = result  # Simpan hasil ke session_state
    
    # Menampilkan hasil perhitungan di halaman utama
    st.subheader('Hasil Ranking TOPSIS')
    st.write(result[['index', 'Closeness Coefficient', 'Ranking', 'Kesimpulan']].rename(columns={'index': 'Vendor'}))
elif st.session_state.topsis_result is not None and not st.session_state.topsis_result.empty:
    # Jika hasil sudah ada di session_state, tampilkan
    st.subheader('Hasil Ranking TOPSIS')
    st.write(st.session_state.topsis_result[['index', 'Closeness Coefficient', 'Ranking', 'Kesimpulan']].rename(columns={'index': 'Vendor'}))
else:
    st.info("Masukkan data dan simpan terlebih dahulu.")
