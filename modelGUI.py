import csv # CSV dosyasını okumak için gerekli olan kütüphane
import PySimpleGUI as sg # GUI kütüphanesi

def load_data(filename): # Veri setini okuyan fonksiyon
    """Veri setini okur, veri setini ve başlığı liste şeklinde döndürür"""
    data = []
    with open(filename, 'r') as file:
        reader = csv.reader(file,delimiter=";") # Veri setini okurken ; işaretini ayırıcı olarak kullanır
        for row in reader:
            data.append([value for value in row])
    header = data[0] # Veri setininin sütun başlıklarını alır
    data = data[1:] # Veri setininin sütun başlıklarını veri setinden çıkarır
    for row in range(len(data)):
        for col in range(len(header)-1):
            data[row][col] = int(data[row][col])
    return data, header


def class_counts(rows): 
    """Veri setindeki her sınıfın kaç tane örneği olduğunu sayan fonksiyon"""
    counts = {}  # Sınıf adı -> örnek sayısı şeklinde bir sözlük.
    for row in rows:
        # Veri setinde, etiket her zaman son sütundur
        label = row[-1]
        if label not in counts:
            counts[label] = 0
        counts[label] += 1
    return counts

def is_numeric(value):
    """Bir değerin sayısal olup olmadığını test eden fonksiyon"""
    return isinstance(value, int) or isinstance(value, float)

class Question:
    """Bu sınıf, veri kümesini bölümlemek için kullanılır."""

    def __init__(self, column, value): # Sınıfın yapıcı fonksiyonu
        self.column = column # Sütun numarası
        self.value = value # Sütunun değeri

    def match(self, example):
        # Veri setindeki bir örneğin bu soruya cevap verip vermediğini test eder.
        # Örnekteki değer, sorunun değerine eşitse True, değilse False döndürür.
        val = example[self.column]
        if is_numeric(val): # Eğer değer sayısal ise
            return val >= self.value # Değer sorunun değerinden büyükse True, değilse False döndürür
        else: # Eğer değer sayısal değil ise
            return val == self.valu

def partition(rows, question):
    """Bir soruya göre bir veri kümesini bölümleyen fonksiyon"""
    # Her bir soru için, veri kümesini iki parçaya ayırır.
    true_rows, false_rows = [], []
    for row in rows:
        if question.match(row): # Eğer sorguyla eşleşiyorsa
            true_rows.append(row) # True listesine ekler
        else: # Eğer sorguyla eşleşmiyorsa
            false_rows.append(row) # False listesine ekler
    return true_rows, false_rows

def gini(rows):
    # Gini katsayısını hesaplayan fonksiyon
    counts = class_counts(rows)
    impurity = 1
    for lbl in counts:
        prob_of_lbl = counts[lbl] / float(len(rows)) # Sınıfın olasılığını hesaplar
        impurity -= prob_of_lbl**2
    return impurity


def info_gain(left, right, current_uncertainty):
    """Bilgi kazancını hesaplayan fonksiyon
    Başlangıç düğümünün belirsizliği, ağırlıklı iki çocuk düğümünün belirsizliğinden çıkarılır."""
    p = float(len(left)) / (len(left) + len(right)) # Sol çocuk düğümünün olasılığını hesaplar
    return current_uncertainty - p * gini(left) - (1 - p) * gini(right)

def find_best_split(rows):
    """En iyi soruyu bulmak için her özellik ve değer üzerinde dolaşarak bilgi kazancını hesaplar."""
    best_gain = 0 # En iyi bilgi kazancını tutar
    best_question = None  # En iyi bilgi kazancını veren soruyu (özellik,değer) tutar
    current_uncertainty = gini(rows) # Başlangıç düğümünün belirsizliğini hesaplar
    n_features = len(rows[0]) - 1  # Son sütun etiket olduğu için özellik sayısını bir azaltır

    for col in range(n_features):  # Her bir özellik için

        values = set([row[col] for row in rows])  # Sütundaki benzersiz değerleri alır

        for val in values:  # Her bir değer için

            question = Question(col, val) # Soruyu oluşturur

            # Soruya göre veri kümesini ikiye ayırır
            true_rows, false_rows = partition(rows, question)

            # Eğer veri kümesini ikiye ayıramazsa atlar
            if len(true_rows) == 0 or len(false_rows) == 0:
                continue

            # Bilgi kazancını hesaplar
            gain = info_gain(true_rows, false_rows, current_uncertainty)

            # Eğer bilgi kazancı en iyi bilgi kazancından büyükse
            # en iyi bilgi kazancını ve soruyu günceller
            if gain >= best_gain:
                best_gain, best_question = gain, question

    return best_gain, best_question


class Leaf:
    # Karar ağacının yaprak düğümlerini oluşturur
    # Yaprak düğümlerinde sınıfların sayılarını tutar
    # Örneğin: "Economical" -> 5
    # "Economical" sınıfı 5 kez karar ağacının yaprak düğümlerinde görülür

    def __init__(self, rows):
        self.predictions = class_counts(rows)


class Decision_Node:
    # Ağacın karar düğümlerini oluşturur
    # Karar düğümleri soruları tutar
    def __init__(self,
                 question,
                 true_branch,
                 false_branch):
        self.question = question
        self.true_branch = true_branch
        self.false_branch = false_branch


def build_tree(rows):
    # Ağacı oluşturan fonksiyon

    # En iyi bilgi kazancını ve soruyu bulur
    gain, question = find_best_split(rows)

    # Bilgi kazancı 0 ise yaprak düğüm oluşturur
    # Yani karar ağacı oluşturulmaya devam edilmez
    # Çünkü sorulacak soru kalmamıştır
    if gain == 0:
        return Leaf(rows)

    # Soruya göre veri kümesini ikiye ayırır
    # True ve False listeleri oluşturur
    true_rows, false_rows = partition(rows, question)

    # True listesini kullanarak ağacı oluşturur
    true_branch = build_tree(true_rows)

    # False listesini kullanarak ağacı oluşturur  
    false_branch = build_tree(false_rows)

    # Soruyu ve iki çocuk düğümü (true_branch, false_branch) döndürür    
    return Decision_Node(question, true_branch, false_branch)

def classify(row, node):
    """Ağacı kullanarak bir veri örneğini sınıflandıran fonksiyon"""

    # Eğer yaprak düğüm ise tahminleri döndürür
    if isinstance(node, Leaf):
        return node.predictions

    # Compare the feature / value stored in the node
    # Eğer sorunun cevabı True ise true_branch'e git
    # Eğer sorunun cevabı False ise false_branch'e git
    if node.question.match(row):
        return classify(row, node.true_branch)
    else:
        return classify(row, node.false_branch)

def predict(row, tree):
    # Ağacı kullanarak bir veri örneğini sınıflandırır
    return list(classify(row, tree).keys())[0]
    
if __name__ == '__main__':

    training_data, header = load_data("Data.csv")
    my_tree = build_tree(training_data)

    # GUI penceresini oluştur

    layout = [[sg.Text("1: Endişeli Değilim 5: Çok Endişeliyim")],
        [sg.Text('Ekonomik Değer (1-5):'), sg.Input(do_not_clear=True)],
          [sg.Text('Siyasi Değer (1-5):'), sg.Input(do_not_clear=True)],
          [sg.Text('Dinsel Değer (1-5):'), sg.Input(do_not_clear=True)],
          [sg.Text('Savaş Değer (1-5):'), sg.Input(do_not_clear=True)],
          [sg.Text('Mülteci Değer (1-5):'), sg.Input(do_not_clear=True)],
          [sg.Text('Sağlık Değer (1-5):'), sg.Input(do_not_clear=True)],
          [sg.Text('Altyapı Değer (1-5):'), sg.Input(do_not_clear=True)],
          [sg.Text('Suç Değer (1-5):'), sg.Input(do_not_clear=True)],
          [sg.Text('Açlık Değer (1-5):'), sg.Input(do_not_clear=True)],
          [sg.Text('Ulaşım Değer (1-5):'), sg.Input(do_not_clear=True)],
          [sg.Button('Tahmin Et')]
          ]

    window = sg.Window('Bölge Tahmini', layout)

    # GUI penceresini çalıştır ve kullanıcıdan verileri al
    while True:
        event, values = window.read()
        # Kullanıcı pencereyi kapatırsa pencereyi kapat
        if event == sg.WIN_CLOSED or event == None:
            break

        elif event == 'Tahmin Et':  # Kullanıcı Tahmin Et düğmesine tıklar, tahmin işlemini gerçekleştir
            # Kullanıcıdan alınan verileri kullanarak tahmin yapın
            # Kullanıcıdan alınan verileri kontrol et
            all_values_valid = True
            for value in values.values():
                if not (1 <= int(value) <= 5):
                    all_values_valid = False
                    break

            if all_values_valid:
                # Kullanıcıdan alınan verileri kullanarak tahmin yapın
                values = [int(value) for value in values.values()]
                prediction = predict(values,my_tree)
                sg.popup("Tahmin: " + prediction)
            else:
                sg.popup("Lütfen tüm değerleri 1 ile 5 arasında giriniz.")


    window.close()
