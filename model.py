import csv # CSV dosyasını okumak için gerekli olan kütüphane
import random # Veri setini rastgele olarak dağıtmak için gerekli olan kütüphane

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

def train_test_split(data, test_size=0.2): # Veri setini eğitim ve test setine ayıran fonksiyon
    random.shuffle(data) # Veri setini rastgele olarak karıştırır
    test_set_size = int(len(data) * test_size) # Test setinin boyutunu hesaplar
    test_set = random.sample(data, test_set_size) # Test setini rastgele olarak seçer
    train_set = [row for row in data if row not in test_set] # Eğitim setini test setinden çıkarır
    return train_set, test_set

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
            return val == self.value # Değer sorunun değerine eşitse True, değilse False döndürür

    def __repr__(self): # Sınıfın yazdırılma fonksiyonu
        condition = "=="
        if is_numeric(self.value): # Eğer değer sayısal ise
            condition = ">=" # Karşılaştırma operatörü olarak >= kullanır
        return "Is %s %s %s?" % (
            header[self.column], condition, str(self.value))

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


def print_tree(node, spacing=""):
    """Ağacı yazdıran fonksiyon"""

    # Eğer yaprak düğüm ise tahminleri yazdırır
    if isinstance(node, Leaf):
        print (spacing + "Predict", node.predictions)
        return

    # Soruyu yazdırır
    print (spacing + str(node.question))

    # True çocuk düğümünü yazdırır
    print (spacing + '--> True:')
    print_tree(node.true_branch, spacing + "  ")

    # False çocuk düğümünü yazdırır
    print (spacing + '--> False:')
    print_tree(node.false_branch, spacing + "  ")


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

def print_leaf(counts):
    # Tahminleri yazdıran fonksiyon
    total = sum(counts.values()) * 1.0
    probs = {}
    for lbl in counts.keys():
        probs[lbl] = str(int(counts[lbl] / total * 100)) + "%"
    return probs

def print_accuracy(counts):
    # Doğruluk oranını hesaplayan fonksiyon
    total = sum(counts.values()) * 1.0
    probs = {}
    max_prob = 0
    max_class = None
    for lbl in counts.keys():
        if int(counts[lbl] / total * 100) > max_prob:
            max_prob = int(counts[lbl] / total * 100)
            max_class = lbl
        probs[lbl] = str(int(counts[lbl] / total * 100)) + "%"
    return max_class

def predict(row, tree):
    # Ağacı kullanarak bir veri örneğini sınıflandırır
    return list(classify(row, tree).keys())[0]


if __name__ == '__main__':

    data, header = load_data("Data.csv")
    training_data, testing_data = train_test_split(data, test_size=0.2)
    my_tree = build_tree(training_data)

    print_tree(my_tree)
    true_count = 0
    total_count = 0

    for row in testing_data:
        print ("Actual: %s. Predicted: %s" % (row[-1], print_leaf(classify(row, my_tree))))
        if row[-1] == print_accuracy(classify(row, my_tree)):
            true_count += 1
        else:
            print("Wrong Guess!") 
        total_count += 1
    print("Accuracy: ", true_count / total_count)
   