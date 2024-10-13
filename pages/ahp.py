import streamlit as st
import pandas as pd

# Fungsi untuk menghitung bobot prioritas AHP tanpa menggunakan vektor
def ahp_priority(matrix):
    n = len(matrix)
    # Menghitung total setiap kolom
    column_sum = [sum(row[j] for row in matrix) for j in range(n)]
    
    # Menghitung bobot dengan membagi setiap elemen dengan total kolom
    priorities = [sum(matrix[i][j] / column_sum[j] for j in range(n)) / n for i in range(n)]
    
    # Menghitung lambda_max
    weighted_sum_vector = [sum(matrix[i][j] * priorities[j] for j in range(n)) for i in range(n)]
    lambda_max = sum(weighted_sum_vector[i] / priorities[i] for i in range(n)) / n
    
    return priorities, lambda_max

# Fungsi untuk menghitung rasio konsistensi
def consistency_ratio(matrix, priorities):
    n = len(matrix)
    weighted_sum_vector = [sum(matrix[i][j] * priorities[j] for j in range(n)) for i in range(n)]
    lambda_max = sum(weighted_sum_vector[i] / priorities[i] for i in range(n)) / n
    ci = (lambda_max - n) / (n - 1)  # Menghitung Consistency Index
    random_index = {1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
    cr = ci / random_index[n]  # Menghitung Consistency Ratio
    return cr, lambda_max  # Mengembalikan CR dan lambda_max

st.title("Metode AHP dengan Input Manual")

# Input kriteria
st.header("Masukkan Kriteria")
num_criteria = st.number_input("Jumlah Kriteria", min_value=1, max_value=10, value=5)

criteria = []
for i in range(num_criteria):
    criteria.append(st.text_input(f"Nama Kriteria {i+1}", value=f"C0{i+1}"))

# Matriks Perbandingan Berpasangan
st.header("Masukkan Matriks Perbandingan Berpasangan Kriteria")
matrix = [[1 if i == j else 0 for j in range(num_criteria)] for i in range(num_criteria)]

# Memastikan semua pasangan terinput
for i in range(num_criteria):
    for j in range(i + 1, num_criteria):
        value = st.number_input(f"Perbandingan {criteria[i]} vs {criteria[j]}", min_value=0.1, max_value=9.0, value=1.0)
        matrix[i][j] = value
        matrix[j][i] = 1 / value

st.write("Matriks Perbandingan Kriteria:")
st.write(pd.DataFrame(matrix, index=criteria, columns=criteria))

# Menghitung Bobot Prioritas dan Rasio Konsistensi
if st.button("Hitung Bobot Kriteria"):
    # Langkah 2: Menghitung Nilai Eigen dan Bobot Prioritas
    priorities, lambda_max = ahp_priority(matrix)
    
    # Langkah 5: Menghitung Rasio Konsistensi
    cr, lambda_max = consistency_ratio(matrix, priorities)

    st.subheader("Hasil Bobot Prioritas Kriteria:")
    bobot_prioritas_df = pd.DataFrame(priorities, index=criteria, columns=["Bobot Prioritas"])
    st.write(bobot_prioritas_df)

    st.subheader("Rasio Konsistensi (CR):")
    st.write(f"CR: {cr:.4f}")
    if cr > 0.1:
        st.warning("Rasio konsistensi terlalu tinggi, perbandingan mungkin tidak konsisten.")
    else:
        st.success("Perbandingan konsisten.")

# Input alternatif
st.header("Masukkan Alternatif")
num_alternatives = st.number_input("Jumlah Alternatif", min_value=1, max_value=10, value=3)

alternatives = []
for i in range(num_alternatives):
    alternatives.append(st.text_input(f"Nama Alternatif {i+1}", value=f"Alternatif {i+1}"))

# Matriks Perbandingan Berpasangan Alternatif untuk Setiap Kriteria
st.header("Matriks Perbandingan Antar Alternatif Berdasarkan Kriteria")
all_alt_weights = []
for k in criteria:
    st.subheader(f"Perbandingan Alternatif Berdasarkan {k}")
    alt_matrix = [[1 if i == j else 0 for j in range(num_alternatives)] for i in range(num_alternatives)]
    
    for i in range(num_alternatives):
        for j in range(i + 1, num_alternatives):
            value = st.number_input(f"Perbandingan {alternatives[i]} vs {alternatives[j]} untuk {k}", min_value=0.1, max_value=9.0, value=1.0)
            alt_matrix[i][j] = value
            alt_matrix[j][i] = 1 / value

    st.write(f"Matriks perbandingan untuk {k}:")
    st.write(pd.DataFrame(alt_matrix, index=alternatives, columns=alternatives))
    
    # Menghitung bobot prioritas untuk alternatif berdasarkan kriteria
    alt_priorities, _ = ahp_priority(alt_matrix)
    all_alt_weights.append(alt_priorities)
    
    st.write("Bobot Prioritas Alternatif Berdasarkan Kriteria:")
    st.write(pd.DataFrame(alt_priorities, index=alternatives, columns=[f"Bobot {k}"]))

# Jika sudah ada prioritas kriteria, lakukan perhitungan akhir untuk setiap alternatif
if st.button("Hitung Alternatif Terbaik"):
    final_scores = [0] * num_alternatives  # Inisialisasi dengan nol

    # Pastikan kita mengalikan dengan bobot kriteria yang sesuai
    for i in range(num_criteria):
        for j in range(num_alternatives):
            final_scores[j] += all_alt_weights[i][j] * priorities[i]  # Mengalikan bobot prioritas alternatif dengan bobot kriteria

    st.subheader("Skor Akhir untuk Setiap Alternatif:")
    final_df = pd.DataFrame(final_scores, index=alternatives, columns=["Skor Akhir"])
    st.write(final_df)

    st.write(f"Alternatif terbaik adalah: {alternatives[final_scores.index(max(final_scores))]}")
