import streamlit as st
import pandas as pd
from apyori import apriori


# Fungsi untuk memproses dataset dan mencari aturan-asosiasi
def find_association_rules(transactions, min_support, min_confidence):
    transactions_list = []
    for _, transaction in transactions.iterrows():
        transaction_cleaned = transaction.dropna().astype(str).tolist()  # Menghapus NaN dan konversi ke list of strings
        if transaction_cleaned:
            transactions_list.append(transaction_cleaned)

    # Menjalankan Algoritma Apriori jika ada transaksi yang tidak kosong
    if transactions_list:
        results = list(apriori(transactions_list, min_support=min_support, min_confidence=min_confidence))

        # Mengumpulkan hasil aturan-asosiasi
        rules = []
        for result in results:
            support = result.support
            for ordered_stat in result.ordered_statistics:
                lhs = ", ".join(list(ordered_stat.items_base))
                rhs = ", ".join(list(ordered_stat.items_add))
                confidence = round(ordered_stat.confidence * 100)  # Confidence dibulatkan
                total_percent = round((support * ordered_stat.confidence) * 100,
                                      2)  # Total dibulatkan dan 2 digit desimal
                rules.append((lhs, rhs, support, f"{confidence}%", f"{total_percent}%"))

        return rules
    else:
        return []


# Main program dengan menggunakan Streamlit
def main():
    st.title('Aplikasi Evaluasi Aturan-Asosiasi')

    # Pilihan antara upload file atau input manual
    option = st.selectbox('Pilih cara memasukkan data transaksi:',
                          ('Upload File CSV', 'Input Manual'))

    transactions = pd.DataFrame()

    if option == 'Upload File CSV':
        uploaded_file = st.file_uploader("Upload dataset transaksi (CSV file)", type=['csv'])
        if uploaded_file is not None:
            transactions = pd.read_csv(uploaded_file, header=None)

    elif option == 'Input Manual':
        st.write('### Masukkan Data Transaksi Manual')
        st.write('Masukkan transaksi satu per satu, pisahkan item dengan koma (misal: Roti, Susu, Telur)')
        transaction_input = st.text_input('Transaksi baru:', '')
        if 'transactions' not in st.session_state:
            st.session_state['transactions'] = []

        if st.button('Tambah Transaksi'):
            if transaction_input:
                st.session_state['transactions'].append([item.strip() for item in transaction_input.split(',')])

        # Memastikan bahwa transaksi yang sudah ada ditampilkan dengan benar
        transactions = pd.DataFrame(st.session_state['transactions'])

    if not transactions.empty:
        st.write("Transaksi yang dimasukkan:")
        st.table(transactions)

    # Input nilai minimum (φ) dan minimum confidence (%)
    min_support = st.number_input('Masukkan nilai minimum (φ)', min_value=0.0, max_value=1.0, step=0.01, value=0.2)
    min_confidence = st.number_input('Masukkan minimum confidence (%)', min_value=0, max_value=100, step=1, value=60)

    # Tombol untuk memproses dan menampilkan aturan-asosiasi
    if st.button('Proses') and not transactions.empty:
        st.write(
            f"\nMenghitung Aturan-Asosiasi dengan nilai minimum (φ) = {min_support} "
            f"dan minimum confidence = {min_confidence}%\n")

        # Memanggil fungsi untuk menemukan aturan-asosiasi
        rules = find_association_rules(transactions, min_support, min_confidence / 100)

        # Menampilkan hasil aturan-asosiasi
        if len(rules) == 0:
            st.write("Tidak ada aturan-asosiasi yang memenuhi kriteria.")
        else:
            # Menampilkan tabel hasil aturan-asosiasi menggunakan st.table
            st.write("Hasil Aturan-Asosiasi:")
            table_data = []
            for idx, (lhs, rhs, support, confidence, total_percent) in enumerate(rules):
                table_data.append([f"Aturan {idx + 1}", f"{lhs} -> {rhs}", f"{support:.2f}", confidence, total_percent])

            st.table(pd.DataFrame(table_data, columns=['Aturan', 'LHS -> RHS', 'Support', 'Confidence', 'Total']))

        st.markdown('<a href="/" target="_self">Reset</a>', unsafe_allow_html=True)


if __name__ == '__main__':
    main()
